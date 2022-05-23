/* -*- mode: C++; c-basic-offset: 4; tab-width: 4 -*-
 *
 * Copyright (c) 2016 Apple Inc. All rights reserved.
 *
 * @APPLE_LICENSE_HEADER_START@
 * 
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this
 * file.
 * 
 * The Original Code and all software distributed under the License are
 * distributed on an 'AS IS' basis, WITHOUT WARRANTY OF ANY KIND, EITHER
 * EXPRESS OR IMPLIED, AND APPLE HEREBY DISCLAIMS ALL SUCH WARRANTIES,
 * INCLUDING WITHOUT LIMITATION, ANY WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT OR NON-INFRINGEMENT.
 * Please see the License for the specific language governing rights and
 * limitations under the License.
 * 
 * @APPLE_LICENSE_HEADER_END@
 */

#include <dlfcn.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdio.h>
#include <libproc.h>
#include <sys/param.h>
#include <mach/shared_region.h>
#include <mach/mach_vm.h>
#include <mach/vm_region.h>
#include <libkern/OSAtomic.h>
#include <mach-o/dyld_process_info.h>
#include <mach-o/dyld_images.h>

#include "MachOFile.h"
#include "dyld_process_info_internal.h"
#include "Tracing.h"
#include "DebuggerSupport.h"
#include "DyldProcessConfig.h"

RemoteBuffer& RemoteBuffer::operator=(RemoteBuffer&& other) {
    std::swap(_localAddress, other._localAddress);
    std::swap(_size, other._size);
    std::swap(_kr, other._kr);
    return *this;
}

RemoteBuffer::RemoteBuffer() : _localAddress(0), _size(0), _kr(KERN_SUCCESS) {}
RemoteBuffer::RemoteBuffer(std::tuple<mach_vm_address_t,vm_size_t,kern_return_t> T)
    : _localAddress(std::get<0>(T)), _size(std::get<1>(T)), _kr(std::get<2>(T)) {}

RemoteBuffer::RemoteBuffer(task_t task, mach_vm_address_t remote_address, size_t remote_size, bool allow_truncation)
: RemoteBuffer(RemoteBuffer::create(task, remote_address, remote_size, allow_truncation)) {};

std::pair<mach_vm_address_t, kern_return_t>
RemoteBuffer::map(task_t task, mach_vm_address_t remote_address, vm_size_t size) {
    static kern_return_t (*mvrn)(vm_map_t, mach_vm_address_t*, mach_vm_size_t, mach_vm_offset_t, int, vm_map_read_t, mach_vm_address_t,
                                 boolean_t, vm_prot_t*, vm_prot_t*, vm_inherit_t) = nullptr;
    vm_prot_t cur_protection = VM_PROT_NONE;
    vm_prot_t max_protection = VM_PROT_READ;
    if (size == 0) {
        return std::make_pair(MACH_VM_MIN_ADDRESS, KERN_INVALID_ARGUMENT);
    }
    mach_vm_address_t localAddress = 0;
#if TARGET_OS_SIMULATOR
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        mvrn = (kern_return_t (*)(vm_map_t, mach_vm_address_t*, mach_vm_size_t, mach_vm_offset_t, int, vm_map_read_t, mach_vm_address_t,
                                  boolean_t, vm_prot_t*, vm_prot_t*, vm_inherit_t))dlsym(RTLD_DEFAULT, "mach_vm_remap_new");
        if (mvrn == nullptr) {
            // We are running on a system that does not support task_read ports, use the old call
            mvrn = (kern_return_t (*)(vm_map_t, mach_vm_address_t*, mach_vm_size_t, mach_vm_offset_t, int, vm_map_read_t, mach_vm_address_t,
                                      boolean_t, vm_prot_t*, vm_prot_t*, vm_inherit_t))dlsym(RTLD_DEFAULT, "mach_vm_remap");
        }
    });
#else
    mvrn = &mach_vm_remap_new;
#endif
    auto kr = mvrn(mach_task_self(),
                        &localAddress,
                        size,
                        0,  // mask
                        VM_FLAGS_ANYWHERE | VM_FLAGS_RESILIENT_CODESIGN | VM_FLAGS_RESILIENT_MEDIA,
                        task,
                        remote_address,
                        true,
                        &cur_protection,
                        &max_protection,
                        VM_INHERIT_NONE);
    // The call is not succesfull return
    if (kr != KERN_SUCCESS) {
        return std::make_pair(MACH_VM_MIN_ADDRESS, kr);
    }
    // If it is not a shared buffer then copy it into a local buffer so our results are coherent in the event
    // the page goes way due to storage removal, etc. We have to do this because even after we read the page the
    // contents might go away of the object is paged out and then the backing region is disconnected (for example, if
    // we are copying some memory in the middle of a mach-o that is on a USB drive that is disconnected after we perform
    // the mapping). Once we copy them into a local buffer the memory will be handled by the default pager instead of
    // potentially being backed by the mmap pager, and thus will be guaranteed not to mutate out from under us.
    void* buffer = malloc(size);
    if (buffer == nullptr) {
        (void)vm_deallocate(mach_task_self(), (vm_address_t)localAddress, size);
        return std::make_pair(MACH_VM_MIN_ADDRESS, KERN_NO_SPACE);
    }
    memcpy(buffer, (void *)localAddress, size);
    (void)vm_deallocate(mach_task_self(), (vm_address_t)localAddress, size);
    return std::make_pair((vm_address_t)buffer, KERN_SUCCESS);
}

std::tuple<mach_vm_address_t,vm_size_t,kern_return_t> RemoteBuffer::create(task_t task,
                                                                                mach_vm_address_t remote_address,
                                                                                size_t size,
                                                                                bool allow_truncation) {
    mach_vm_address_t localAddress;
    kern_return_t kr;
    // Try the initial map
    std::tie(localAddress, kr) = map(task, remote_address, size);
    if (kr == KERN_SUCCESS) return std::make_tuple(localAddress, size, kr);
    // The first attempt failed, truncate if possible and try again. We only need to try once since the largest
    // truncatable buffer we map is less than a single page. To be more general we would need to try repeatedly in a
    // loop.
    if (allow_truncation) {
        size = PAGE_SIZE - remote_address%PAGE_SIZE;
        std::tie(localAddress, kr) = map(task, remote_address, size);
        if (kr == KERN_SUCCESS) return std::make_tuple(localAddress, size, kr);
    }
    // If we reach this then the mapping completely failed
    return std::make_tuple(MACH_VM_MIN_ADDRESS, 0, kr);
}

RemoteBuffer::~RemoteBuffer() {
    if (!_localAddress) { return; }
    free((void*)_localAddress);
}
void *RemoteBuffer::getLocalAddress() const { return (void *)_localAddress; }
size_t RemoteBuffer::getSize() const { return _size; }
kern_return_t RemoteBuffer::getKernelReturn() const { return _kr; }

void withRemoteBuffer(task_t task, mach_vm_address_t remote_address, size_t remote_size, bool allow_truncation, kern_return_t *kr, void (^block)(void *buffer, size_t size)) {
    kern_return_t krSink = KERN_SUCCESS;
    if (kr == nullptr) {
        kr = &krSink;
    }
    RemoteBuffer buffer(task, remote_address, remote_size, allow_truncation);
    *kr = buffer.getKernelReturn();
    if (*kr == KERN_SUCCESS) {
        block(buffer.getLocalAddress(), buffer.getSize());
    }
}


//
// Opaque object returned by _dyld_process_info_create()
//

struct __attribute__((visibility("hidden"))) dyld_process_info_deleter { // deleter
    //    dyld_process_info_deleter() {};
    //    dyld_process_info_deleter(const dyld_process_info_deleter&) { }
    //    dyld_process_info_deleter(dyld_process_info_deleter&) {}
    //    dyld_process_info_deleter(dyld_process_info_deleter&&) {}
    void operator()(dyld_process_info_base* p) const {
        if (p) {
            free(p);
        }
    };
};

static dyld_process_info_deleter deleter;
typedef std::unique_ptr<dyld_process_info_base, dyld_process_info_deleter> dyld_process_info_ptr;

struct __attribute__((visibility("hidden"))) dyld_process_info_base {
    template<typename T1, typename T2>
    static dyld_process_info_ptr make(task_t task, const T1& allImageInfo, uint64_t timestamp, kern_return_t* kr);
    template<typename T>
    static dyld_process_info_ptr makeSuspended(task_t task, const T& allImageInfo, kern_return_t* kr);

    std::atomic<uint32_t>&       retainCount() const { return _retainCount; }
    dyld_process_cache_info*     cacheInfo() const { return (dyld_process_cache_info*)(((char*)this) + _cacheInfoOffset); }
    dyld_process_aot_cache_info* aotCacheInfo() const { return (dyld_process_aot_cache_info*)(((char*)this) + _aotCacheInfoOffset); }
    dyld_process_state_info*     stateInfo() const { return (dyld_process_state_info*)(((char*)this) + _stateInfoOffset); }
    dyld_platform_t              platform() const { return _platform; }

    void                         forEachImage(void (^callback)(uint64_t machHeaderAddress, const uuid_t uuid, const char* path)) const;
    void                         forEachAotImage(bool (^callback)(uint64_t x86Address, uint64_t aotAddress, uint64_t aotSize, uint8_t* aotImageKey, size_t aotImageKeySize)) const;
    void                         forEachSegment(uint64_t machHeaderAddress, void (^callback)(uint64_t segmentAddress, uint64_t segmentSize, const char* segmentName)) const;

    bool reserveSpace(size_t space) {
        if (_freeSpace < space) { return false; }
        _freeSpace -= space;
        return true;
    }

    void retain()
    {
        _retainCount++;
    }

    void release()
    {
        uint32_t newCount = --_retainCount;

        if ( newCount == 0 ) {
            free(this);
        }
    }

private:
    struct ImageInfo {
        uuid_t                  uuid;
        uint64_t                loadAddress;
        const char*             path;
        uint32_t                segmentStartIndex;
        uint32_t                segmentsCount;
    };

    struct SegmentInfo {
        const char*             name;
        uint64_t                addr;
        uint64_t                size;
    };

                                dyld_process_info_base(dyld_platform_t platform, unsigned imageCount, unsigned aotImageCount, size_t totalSize);
    void*                       operator new (size_t, void* buf) { return buf; }

    static bool                 inCache(uint64_t addr) { return (addr > SHARED_REGION_BASE) && (addr < SHARED_REGION_BASE+SHARED_REGION_SIZE); }
    bool                        addImage(task_t task, bool sameCacheAsThisProcess, uint64_t imageAddress, uint64_t imagePath, const char* imagePathLocal);

    bool                        addAotImage(dyld_aot_image_info_64 aotImageInfo);

    kern_return_t               addDyldImage(task_t task, uint64_t dyldAddress, uint64_t dyldPathAddress, const char* localPath);

    bool                        invalid() { return ((char*)_stringRevBumpPtr < (char*)_curSegment); }
    const char*                 copyPath(task_t task, uint64_t pathAddr);
    const char*                 addString(const char*, size_t);
    const char*                 copySegmentName(const char*);

    void                        addInfoFromLoadCommands(const mach_header* mh, uint64_t addressInTask, size_t size);
    kern_return_t               addInfoFromRemoteLoadCommands(task_t task, uint64_t remoteMH);

    void                        inspectLocalImageLoadCommands(uint64_t imageAddress, void* func);
    kern_return_t               inspectRemoteImageLoadCommands(task_t task, uint64_t imageAddress, void* func);

    mutable std::atomic<uint32_t>            _retainCount;
    const uint32_t              _cacheInfoOffset;
    const uint32_t              _aotCacheInfoOffset;
    const uint32_t              _stateInfoOffset;
    const uint32_t              _imageInfosOffset;
    const uint32_t              _aotImageInfosOffset;
    const uint32_t              _segmentInfosOffset;
    size_t                      _freeSpace;
    dyld_platform_t             _platform;
    ImageInfo* const            _firstImage;
    ImageInfo*                  _curImage;
    dyld_aot_image_info_64* const            _firstAotImage;
    dyld_aot_image_info_64*                  _curAotImage;
    SegmentInfo* const          _firstSegment;
    SegmentInfo*                _curSegment;
    uint32_t                    _curSegmentIndex;
    char*                       _stringRevBumpPtr;

    // dyld_process_cache_info  cacheInfo;
    // dyld_process_state_info  stateInfo;
    // ImageInfo                images[];
    // SegmentInfo              segments[];
    // char                     stringPool[]
};

dyld_process_info_base::dyld_process_info_base(dyld_platform_t platform, unsigned imageCount, unsigned aotImageCount, size_t totalSize)
 :  _retainCount(1), _cacheInfoOffset(sizeof(dyld_process_info_base)),
    _aotCacheInfoOffset(sizeof(dyld_process_info_base) + sizeof(dyld_process_cache_info)),
    _stateInfoOffset(sizeof(dyld_process_info_base) + sizeof(dyld_process_cache_info) + sizeof(dyld_process_aot_cache_info)),
    _imageInfosOffset(sizeof(dyld_process_info_base) + sizeof(dyld_process_cache_info) + sizeof(dyld_process_aot_cache_info) + sizeof(dyld_process_state_info)),
    _aotImageInfosOffset(sizeof(dyld_process_info_base) + sizeof(dyld_process_cache_info) + sizeof(dyld_process_aot_cache_info) + sizeof(dyld_process_state_info) + imageCount*sizeof(ImageInfo)),
    _segmentInfosOffset(sizeof(dyld_process_info_base) + sizeof(dyld_process_cache_info) + sizeof(dyld_process_aot_cache_info) + sizeof(dyld_process_state_info) + imageCount*sizeof(ImageInfo) + aotImageCount*sizeof(dyld_aot_image_info_64)),
    _freeSpace(totalSize), _platform(platform),
    _firstImage((ImageInfo*)(((uint8_t*)this) + _imageInfosOffset)),
    _curImage((ImageInfo*)(((uint8_t*)this) + _imageInfosOffset)),
    _firstAotImage((dyld_aot_image_info_64*)(((uint8_t*)this) + _aotImageInfosOffset)),
    _curAotImage((dyld_aot_image_info_64*)(((uint8_t*)this) + _aotImageInfosOffset)),
    _firstSegment((SegmentInfo*)(((uint8_t*)this) + _segmentInfosOffset)),
    _curSegment((SegmentInfo*)(((uint8_t*)this) + _segmentInfosOffset)),
    _curSegmentIndex(0),
    _stringRevBumpPtr((char*)(this)+totalSize)
{
}

template<typename T1, typename T2>
dyld_process_info_ptr dyld_process_info_base::make(task_t task, const T1& allImageInfo, uint64_t timestamp, kern_return_t* kr)
{
    __block dyld_process_info_ptr result = nullptr;

    // bail out of dyld is too old
    if ( allImageInfo.version < 15 ) {
        *kr = KERN_FAILURE;
        return nullptr;
    }

    // Check if the process is suspended
    if (allImageInfo.infoArrayChangeTimestamp == 0) {
        result = dyld_process_info_base::makeSuspended<T1>(task, allImageInfo, kr);
        // If we have a result return it, otherwise rescan
        if (result) {
            // If it returned the process is suspended and there is nothing more to do
            return std::move(result);
        }
        usleep(1000 * 50); // 50ms
        // Not exactly correct, but conveys that operation may succeed in the future
        *kr = KERN_RESOURCE_SHORTAGE;
        return  nullptr;
    }

    // Test to see if there are no changes and we can exit early
    if (timestamp != 0 && timestamp == allImageInfo.infoArrayChangeTimestamp) {
        *kr = KERN_SUCCESS;
        return nullptr;
    }

    uint64_t currentTimestamp = allImageInfo.infoArrayChangeTimestamp;
    mach_vm_address_t infoArray = allImageInfo.infoArray;
    if (infoArray == 0) {
        usleep(1000 * 50); // 50ms
        // Not exactly correct, but conveys that operation may succeed in the future
        *kr = KERN_RESOURCE_SHORTAGE;
        return  nullptr;
    };

    // For the moment we are going to truncate any image list longer than 8192 because some programs do
    // terrible things that corrupt their own image lists and we need to stop clients from crashing
    // reading them. We can try to do something more advanced in the future. rdar://27446361
    uint32_t imageCount = allImageInfo.infoArrayCount;
    imageCount = MIN(imageCount, 8192);
    size_t imageArraySize = imageCount * sizeof(T2);

    withRemoteBuffer(task, infoArray, imageArraySize, false, kr, ^(void *buffer, size_t size) {
        // figure out how many path strings will need to be copied and their size
        T2* imageArray = (T2 *)buffer;
        const dyld_all_image_infos* myInfo = (const dyld_all_image_infos*)dyld4::gDyld.allImageInfos;
        bool sameCacheAsThisProcess = !allImageInfo.processDetachedFromSharedRegion
            && !myInfo->processDetachedFromSharedRegion
            && ((memcmp(myInfo->sharedCacheUUID, &allImageInfo.sharedCacheUUID[0], 16) == 0)
            && (myInfo->sharedCacheSlide == allImageInfo.sharedCacheSlide));
        unsigned countOfPathsNeedingCopying = 0;
        if ( sameCacheAsThisProcess ) {
            for (uint32_t i=0; i < imageCount; ++i) {
                if ( !inCache(imageArray[i].imageFilePath) )
                    ++countOfPathsNeedingCopying;
            }
        }
        else {
            countOfPathsNeedingCopying = imageCount+1;
        }
        unsigned imageCountWithDyld = imageCount+1;

        // allocate result object
        size_t allocationSize = sizeof(dyld_process_info_base)
                                    + sizeof(dyld_process_cache_info)
                                    + sizeof(dyld_process_aot_cache_info)
                                    + sizeof(dyld_process_state_info)
                                    + sizeof(ImageInfo)*(imageCountWithDyld)
                                    + sizeof(dyld_aot_image_info_64)*(allImageInfo.aotInfoCount) // add the size necessary for aot info to this buffer
                                    + sizeof(SegmentInfo)*imageCountWithDyld*10
                                    + countOfPathsNeedingCopying*PATH_MAX;
        void* storage = malloc(allocationSize);
        if (storage == nullptr) {
            *kr = KERN_NO_SPACE;
            result = nullptr;
            return;
        }
        auto info = dyld_process_info_ptr(new (storage) dyld_process_info_base(allImageInfo.platform, imageCountWithDyld, allImageInfo.aotInfoCount, allocationSize), deleter);
        (void)info->reserveSpace(sizeof(dyld_process_info_base)+sizeof(dyld_process_cache_info)+sizeof(dyld_process_state_info)+sizeof(dyld_process_aot_cache_info));
        (void)info->reserveSpace(sizeof(ImageInfo)*imageCountWithDyld);

        // fill in base info
        dyld_process_cache_info* cacheInfo = info->cacheInfo();
        memcpy(cacheInfo->cacheUUID, &allImageInfo.sharedCacheUUID[0], 16);
        cacheInfo->cacheBaseAddress    = allImageInfo.sharedCacheBaseAddress;
        cacheInfo->privateCache        = allImageInfo.processDetachedFromSharedRegion;
        // if no cache is used, allImageInfo has all zeros for cache UUID
        cacheInfo->noCache = true;
        for (int i=0; i < 16; ++i) {
            if ( cacheInfo->cacheUUID[i] != 0 ) {
                cacheInfo->noCache = false;
            }
        }

        // fill in aot shared cache info
        dyld_process_aot_cache_info* aotCacheInfo = info->aotCacheInfo();
        memcpy(aotCacheInfo->cacheUUID, &allImageInfo.aotSharedCacheUUID[0], 16);
        aotCacheInfo->cacheBaseAddress = allImageInfo.aotSharedCacheBaseAddress;

        dyld_process_state_info* stateInfo = info->stateInfo();
        stateInfo->timestamp           = currentTimestamp;
        stateInfo->imageCount          = imageCountWithDyld;
        stateInfo->initialImageCount   = (uint32_t)(allImageInfo.initialImageCount+1);
        stateInfo->dyldState = dyld_process_state_dyld_initialized;

        if ( allImageInfo.libSystemInitialized != 0 ) {
            stateInfo->dyldState = dyld_process_state_libSystem_initialized;
            if ( allImageInfo.initialImageCount != imageCount ) {
                stateInfo->dyldState = dyld_process_state_program_running;
            }
        }
        if ( allImageInfo.errorMessage != 0 ) {
            stateInfo->dyldState = allImageInfo.terminationFlags ? dyld_process_state_terminated_before_inits : dyld_process_state_dyld_terminated;
        }
        // fill in info for dyld
        if ( allImageInfo.dyldPath != 0 ) {
            if ((*kr = info->addDyldImage(task, allImageInfo.dyldImageLoadAddress, allImageInfo.dyldPath, NULL))) {
                *kr = KERN_FAILURE;
                result = nullptr;
                return;
            }
        }
        // fill in info for each image
        for (uint32_t i=0; i < imageCount; ++i) {
            if (!info->addImage(task, sameCacheAsThisProcess, imageArray[i].imageLoadAddress, imageArray[i].imageFilePath, NULL)) {
                *kr = KERN_FAILURE;
                result = nullptr;
                return;
            }
        }
        // sanity check internal data did not overflow
        if ( info->invalid() ) {
            *kr = KERN_FAILURE;
            result = nullptr;
            return;
        }

        result = std::move(info);
    });

    mach_vm_address_t aotImageArray = allImageInfo.aotInfoArray;
    // shortcircuit this code path if aotImageArray == 0 (32 vs 64 bit struct difference)
    // and if result == nullptr, since we need to append aot image infos to the process info struct
    if (aotImageArray != 0 && result != nullptr) {
        uint32_t aotImageCount = allImageInfo.aotInfoCount;
        size_t aotImageArraySize = aotImageCount * sizeof(dyld_aot_image_info_64);

        withRemoteBuffer(task, aotImageArray, aotImageArraySize, false, kr, ^(void *buffer, size_t size) {
            dyld_aot_image_info_64* imageArray = (dyld_aot_image_info_64*)buffer;
            for (uint32_t i = 0; i < aotImageCount; i++) {
                if (!result->addAotImage(imageArray[i])) {
                    *kr = KERN_FAILURE;
                    result = nullptr;
                    return;
                }
            }
        });
    }
    return std::move(result);
}

template<typename T>
dyld_process_info_ptr dyld_process_info_base::makeSuspended(task_t task, const T& allImageInfo, kern_return_t* kr)
{
    pid_t   pid;
    if ((*kr = pid_for_task(task, &pid))) {
        return NULL;
    }

    mach_task_basic_info ti;
    mach_msg_type_number_t count = MACH_TASK_BASIC_INFO_COUNT;
    if ((*kr = task_info(task, MACH_TASK_BASIC_INFO, (task_info_t)&ti, &count))) {
        return  nullptr;
    }

    // The task is not suspended, exit
    if (ti.suspend_count == 0) {
        return  nullptr;
    }

    __block unsigned        imageCount = 0;  // main executable and dyld
    __block uint64_t        mainExecutableAddress = 0;
    __block uint64_t        dyldAddress = 0;
    char                    dyldPathBuffer[PATH_MAX+1];
    char                    mainExecutablePathBuffer[PATH_MAX+1];
    __block char *          dyldPath = &dyldPathBuffer[0];
    __block char *          mainExecutablePath = &mainExecutablePathBuffer[0];
    __block dyld3::Platform platformID = dyld3::Platform::unknown;
    mach_vm_size_t      size;
    for (mach_vm_address_t address = 0; ; address += size) {
        vm_region_basic_info_data_64_t  info;
        mach_port_t                     objectName;
        unsigned int                    infoCount = VM_REGION_BASIC_INFO_COUNT_64;
        if (kern_return_t r = mach_vm_region(task, &address, &size, VM_REGION_BASIC_INFO,
                                             (vm_region_info_t)&info, &infoCount, &objectName)) {
            break;
        }
        if ( info.protection != (VM_PROT_READ|VM_PROT_EXECUTE) )
            continue;
            // read start of vm region to verify it is a mach header
            withRemoteObject(task, address, NULL, ^(mach_header_64 mhBuffer){
                if ( (mhBuffer.magic != MH_MAGIC) && (mhBuffer.magic != MH_MAGIC_64) )
                    return;
                // now know the region is the start of a mach-o file
                if ( mhBuffer.filetype == MH_EXECUTE ) {
                    mainExecutableAddress = address;
                    int len = proc_regionfilename(pid, mainExecutableAddress, mainExecutablePath, PATH_MAX);
                    if ( len != 0 ) {
                        mainExecutablePath[len] = '\0';
                    }
                    ++imageCount;
                }
                else if ( mhBuffer.filetype == MH_DYLINKER ) {
                    dyldAddress = address;
                    int len = proc_regionfilename(pid, dyldAddress, dyldPath, PATH_MAX);
                    if ( len != 0 ) {
                        dyldPath[len] = '\0';
                    }
                    ++imageCount;
                }
            });
            //fprintf(stderr, "vm region: addr=0x%llX, size=0x%llX, prot=0x%X\n", (uint64_t)address, (uint64_t)size, info.protection);
    }
    //fprintf(stderr, "dyld: addr=0x%llX, path=%s\n", dyldAddress, dyldPathBuffer);
    //fprintf(stderr, "app:  addr=0x%llX, path=%s\n", mainExecutableAddress, mainExecutablePathBuffer);

    // explicitly set aot image count to 0 in the suspended case
    unsigned aotImageCount = 0;

    // allocate result object
    size_t allocationSize =   sizeof(dyld_process_info_base)
                            + sizeof(dyld_process_cache_info)
                            + sizeof(dyld_process_aot_cache_info)
                            + sizeof(dyld_process_state_info)
                            + sizeof(ImageInfo)*(imageCount)
                            + sizeof(dyld_aot_image_info_64)*aotImageCount // this should always be 0, but including it here to be explicit
                            + sizeof(SegmentInfo)*imageCount*10
                            + imageCount*PATH_MAX;
    void* storage = malloc(allocationSize);
    if (storage == nullptr) {
        *kr = KERN_NO_SPACE;
        return  nullptr;
    }
    auto obj = dyld_process_info_ptr(new (storage) dyld_process_info_base((dyld_platform_t)platformID, imageCount, aotImageCount, allocationSize), deleter);
    (void)obj->reserveSpace(sizeof(dyld_process_info_base)+sizeof(dyld_process_cache_info)+sizeof(dyld_process_aot_cache_info)+sizeof(dyld_process_state_info));
    // fill in base info
    dyld_process_cache_info* cacheInfo = obj->cacheInfo();
    bzero(cacheInfo->cacheUUID, 16);
    cacheInfo->cacheBaseAddress    = 0;
    cacheInfo->noCache             = true;
    cacheInfo->privateCache        = false;

    // zero out aot cache info
    dyld_process_aot_cache_info* aotCacheInfo = obj->aotCacheInfo();
    bzero(aotCacheInfo->cacheUUID, 16);
    aotCacheInfo->cacheBaseAddress = 0;

    dyld_process_state_info* stateInfo = obj->stateInfo();
    stateInfo->timestamp           = 0;
    stateInfo->imageCount          = imageCount;
    stateInfo->initialImageCount   = imageCount;
    stateInfo->dyldState           = dyld_process_state_not_started;

    // fill in info for dyld
    if ( dyldAddress != 0 ) {
        if ((*kr = obj->addDyldImage(task, dyldAddress, 0, dyldPath))) {
            return nullptr;
        }
    }

    // fill in info for each image
    if ( mainExecutableAddress != 0 ) {
        if (!obj->addImage(task, false, mainExecutableAddress, 0, mainExecutablePath)) {
            return nullptr;
        }
    }

    if (allImageInfo.infoArrayChangeTimestamp != 0) {
        return  nullptr;
    }

    count = MACH_TASK_BASIC_INFO_COUNT;
    if ((*kr = task_info(task, MACH_TASK_BASIC_INFO, (task_info_t)&ti, &count))) {
        return  nullptr;
    }

    // The task is not suspended, exit
    if (ti.suspend_count == 0) {
        return  nullptr;
    }

    return obj;
}



const char* dyld_process_info_base::addString(const char* str, size_t maxlen)
{
    size_t len = strnlen(str, maxlen) + 1;
    // If we don't have enough space return an empty string
    if (!reserveSpace(len)) { return ""; }
    _stringRevBumpPtr -= len;
    strlcpy(_stringRevBumpPtr, str, len);
    return _stringRevBumpPtr;
}

const char* dyld_process_info_base::copyPath(task_t task, uint64_t stringAddressInTask)
{
    __block const char* retval = "";
    withRemoteBuffer(task, stringAddressInTask, PATH_MAX, true, nullptr, ^(void *buffer, size_t size) {
        retval = addString(static_cast<const char *>(buffer), size);
    });
    return retval;
}

bool dyld_process_info_base::addImage(task_t task, bool sameCacheAsThisProcess, uint64_t imageAddress, uint64_t imagePath, const char* imagePathLocal)
{
    _curImage->loadAddress = imageAddress;
    _curImage->segmentStartIndex = _curSegmentIndex;
    if ( imagePathLocal != NULL ) {
        _curImage->path = addString(imagePathLocal, PATH_MAX);
    } else if ( sameCacheAsThisProcess && inCache(imagePath) ) {
        _curImage->path = (const char*)imagePath;
    } else if (imagePath) {
        _curImage->path = copyPath(task, imagePath);
    } else {
        _curImage->path = "";
    }

    if ( sameCacheAsThisProcess && inCache(imageAddress) ) {
        addInfoFromLoadCommands((mach_header*)imageAddress, imageAddress, 32*1024);
    } else if (addInfoFromRemoteLoadCommands(task, imageAddress) != KERN_SUCCESS) {
        // The image is not here, return early
        return false;
    }
    _curImage->segmentsCount = _curSegmentIndex - _curImage->segmentStartIndex;
    _curImage++;
    return true;
}

bool dyld_process_info_base::addAotImage(dyld_aot_image_info_64 aotImageInfo) {
    if (!reserveSpace(sizeof(dyld_aot_image_info_64))) {
        return false;
    }
    _curAotImage->x86LoadAddress = aotImageInfo.x86LoadAddress;
    _curAotImage->aotLoadAddress = aotImageInfo.aotLoadAddress;
    _curAotImage->aotImageSize = aotImageInfo.aotImageSize;
    memcpy(_curAotImage->aotImageKey, aotImageInfo.aotImageKey, sizeof(aotImageInfo.aotImageKey));

    _curAotImage++;
    return true;
}

kern_return_t dyld_process_info_base::addInfoFromRemoteLoadCommands(task_t task, uint64_t remoteMH) {
    __block kern_return_t kr = KERN_SUCCESS;
    __block size_t headerPagesSize = 0;
    __block bool done = false;

    //Since the minimum we can reasonably map is a page, map that.
    withRemoteBuffer(task, remoteMH, PAGE_SIZE, true, &kr, ^(void * buffer, size_t size) {
        if (size > sizeof(mach_header)) {
            const mach_header* mh = (const mach_header*)buffer;
            headerPagesSize = sizeof(mach_header) + mh->sizeofcmds;
            if (headerPagesSize <= size) {
                addInfoFromLoadCommands(mh, remoteMH, size);
                done = true;
            }
        }
    });

    //The load commands did not fit in the first page, but now we know the size, so remap and try again
    if (!done) {
        if (kr != KERN_SUCCESS) {
            return kr;
        }
        withRemoteBuffer(task, remoteMH, headerPagesSize, false, &kr, ^(void * buffer, size_t size) {
            addInfoFromLoadCommands((mach_header*)buffer, remoteMH, size);
        });
    }

    return kr;
}

kern_return_t dyld_process_info_base::addDyldImage(task_t task, uint64_t dyldAddress, uint64_t dyldPathAddress, const char* localPath)
{
    __block kern_return_t kr = KERN_SUCCESS;
    _curImage->loadAddress = dyldAddress;
    _curImage->segmentStartIndex = _curSegmentIndex;
    if ( localPath != NULL ) {
        _curImage->path = addString(localPath, PATH_MAX);
    }
    else {
        _curImage->path = copyPath(task, dyldPathAddress);
        if ( kr != KERN_SUCCESS)
            return kr;
    }

    kr = addInfoFromRemoteLoadCommands(task, dyldAddress);
    if ( kr != KERN_SUCCESS)
        return kr;

    _curImage->segmentsCount = _curSegmentIndex - _curImage->segmentStartIndex;
    _curImage++;
    return KERN_SUCCESS;
}


void dyld_process_info_base::addInfoFromLoadCommands(const mach_header* mh, uint64_t addressInTask, size_t size)
{
    const load_command* startCmds = NULL;
    if ( mh->magic == MH_MAGIC_64 )
        startCmds = (load_command*)((char *)mh + sizeof(mach_header_64));
    else if ( mh->magic == MH_MAGIC )
        startCmds = (load_command*)((char *)mh + sizeof(mach_header));
    else
        return;  // not a mach-o file, or wrong endianness

    const load_command* const cmdsEnd = (load_command*)((char*)startCmds + mh->sizeofcmds);
    const load_command* cmd = startCmds;
    for(uint32_t i = 0; i < mh->ncmds; ++i) {
        const load_command* nextCmd = (load_command*)((char *)cmd + cmd->cmdsize);
        if ( (cmd->cmdsize < 8) || (nextCmd > cmdsEnd) || (nextCmd < startCmds) ) {
            return;  // malformed load command
        }
        if ( cmd->cmd == LC_UUID ) {
            const uuid_command* uuidCmd = (uuid_command*)cmd;
            memcpy(_curImage->uuid, uuidCmd->uuid, 16);
        }
        else if ( cmd->cmd == LC_SEGMENT ) {
            if (!reserveSpace(sizeof(SegmentInfo))) { break; }
            const segment_command* segCmd = (segment_command*)cmd;
            _curSegment->name = copySegmentName(segCmd->segname);
            _curSegment->addr = segCmd->vmaddr;
            _curSegment->size = segCmd->vmsize;
            _curSegment++;
            _curSegmentIndex++;
        }
        else if ( cmd->cmd == LC_SEGMENT_64 ) {
            if (!reserveSpace(sizeof(SegmentInfo))) { break; }
            const segment_command_64* segCmd = (segment_command_64*)cmd;
            _curSegment->name = copySegmentName(segCmd->segname);
            _curSegment->addr = segCmd->vmaddr;
            _curSegment->size = segCmd->vmsize;
            _curSegment++;
            _curSegmentIndex++;
        }
        cmd = nextCmd;
    }
}

const char* dyld_process_info_base::copySegmentName(const char* name)
{
    // don't copy names of standard segments into string pool
    static const char* stdSegNames[] = {
        "__TEXT", "__DATA", "__LINKEDIT",
        "__DATA_DIRTY", "__DATA_CONST",
        "__OBJC", "__OBJC_CONST",
        "__AUTH", "__AUTH_CONST",
        NULL
    };
    for (const char** s=stdSegNames; *s != NULL; ++s) {
        if ( strcmp(name, *s) == 0 )
        return *s;
    }
    // copy custom segment names into string pool
    return addString(name, 16);
}

void dyld_process_info_base::forEachImage(void (^callback)(uint64_t machHeaderAddress, const uuid_t uuid, const char* path)) const
{
    for (const ImageInfo* p = _firstImage; p < _curImage; ++p) {
        callback(p->loadAddress, p->uuid, p->path);
    }
}


#if TARGET_OS_OSX
void dyld_process_info_base::forEachAotImage(bool (^callback)(uint64_t x86Address, uint64_t aotAddress, uint64_t aotSize, uint8_t* aotImageKey, size_t aotImageKeySize)) const
{
    for (const dyld_aot_image_info_64* p = _firstAotImage; p < _curAotImage; ++p) {
        if (!callback(p->x86LoadAddress, p->aotLoadAddress, p->aotImageSize, (uint8_t*)p->aotImageKey, sizeof(p->aotImageKey))) {
            break;
        }
    }
}
#endif

void dyld_process_info_base::forEachSegment(uint64_t machHeaderAddress, void (^callback)(uint64_t segmentAddress, uint64_t segmentSize, const char* segmentName)) const
{
    for (const ImageInfo* p = _firstImage; p < _curImage; ++p) {
        if ( p->loadAddress == machHeaderAddress ) {
            uint64_t slide = 0;
            for (uint32_t i=0; i < p->segmentsCount; ++i) {
                const SegmentInfo* seg = &_firstSegment[p->segmentStartIndex+i];
                if ( strcmp(seg->name, "__TEXT") == 0 ) {
                    slide = machHeaderAddress - seg->addr;
                    break;
                }
            }
            for (uint32_t i=0; i < p->segmentsCount; ++i) {
                const SegmentInfo* seg = &_firstSegment[p->segmentStartIndex+i];
                callback(seg->addr + slide, seg->size, seg->name);
            }
            break;
        }
    }
}

dyld_process_info _dyld_process_info_create(task_t task, uint64_t timestamp, kern_return_t* kr)
{
    __block dyld_process_info result = nullptr;
    kern_return_t krSink = KERN_SUCCESS;
    if (kr == nullptr) {
        kr = &krSink;
    }
    *kr = KERN_SUCCESS;

    task_dyld_info_data_t task_dyld_info;
    mach_msg_type_number_t count = TASK_DYLD_INFO_COUNT;
    if ( kern_return_t r = task_info(task, TASK_DYLD_INFO, (task_info_t)&task_dyld_info, &count) ) {
        *kr = r;
        return  nullptr;
    }

    //The kernel will return MACH_VM_MIN_ADDRESS for an executable that has not had dyld loaded
    if (task_dyld_info.all_image_info_addr == MACH_VM_MIN_ADDRESS) {
        *kr = KERN_FAILURE;
        return nullptr;
    }

    for (auto i = 0; i < 10; ++i) {
        withRemoteBuffer(task, task_dyld_info.all_image_info_addr, (size_t)task_dyld_info.all_image_info_size, false, kr, ^(void *buffer, size_t size) {
            dyld_process_info_ptr base;
            if (task_dyld_info.all_image_info_format == TASK_DYLD_ALL_IMAGE_INFO_32 ) {
                const dyld_all_image_infos_32* info = (const dyld_all_image_infos_32*)buffer;
                base = dyld_process_info_base::make<dyld_all_image_infos_32, dyld_image_info_32>(task, *info, timestamp, kr);
            } else {
                const dyld_all_image_infos_64* info = (const dyld_all_image_infos_64*)buffer;
                base = dyld_process_info_base::make<dyld_all_image_infos_64, dyld_image_info_64>(task, *info, timestamp, kr);
            }
            if (base) {
                if (result) {
                    free((void*)result);
                }
                result = base.release();
            }
        });
        if (*kr == KERN_SUCCESS) { break; }
    }
    return  result;
}

void _dyld_process_info_get_state(dyld_process_info info, dyld_process_state_info* stateInfo)
{
    *stateInfo = *info->stateInfo();
}

void _dyld_process_info_get_cache(dyld_process_info info, dyld_process_cache_info* cacheInfo)
{
    *cacheInfo = *info->cacheInfo();
}

void _dyld_process_info_get_aot_cache(dyld_process_info info, dyld_process_aot_cache_info* aotCacheInfo)
{
    *aotCacheInfo = *info->aotCacheInfo();
}

void _dyld_process_info_retain(dyld_process_info object)
{
    const_cast<dyld_process_info_base*>(object)->retain();
}

dyld_platform_t _dyld_process_info_get_platform(dyld_process_info object) {
    return  const_cast<dyld_process_info_base*>(object)->platform();
}

void _dyld_process_info_release(dyld_process_info object)
{
    const_cast<dyld_process_info_base*>(object)->release();
}

void _dyld_process_info_for_each_image(dyld_process_info info, void (^callback)(uint64_t machHeaderAddress, const uuid_t uuid, const char* path))
{
    info->forEachImage(callback);
}

#if TARGET_OS_OSX
void _dyld_process_info_for_each_aot_image(dyld_process_info info, bool (^callback)(uint64_t x86Address, uint64_t aotAddress, uint64_t aotSize, uint8_t* aotImageKey, size_t aotImageKeySize))
{
    info->forEachAotImage(callback);
}
#endif

void _dyld_process_info_for_each_segment(dyld_process_info info, uint64_t machHeaderAddress, void (^callback)(uint64_t segmentAddress, uint64_t segmentSize, const char* segmentName))
{
    info->forEachSegment(machHeaderAddress, callback);
}



