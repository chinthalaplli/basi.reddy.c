from django.contrib import admin

# Register your models here.
import scapy.all as scapy
import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '-target', dest='target', help='Target IP / IP range')
    options = parser.parse_args()
    return options


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.src(arp_request_broadcast, timeout=1)[0]

    router_mac = answered_list[0][1].hwsrc

    clients_list = []
    for item in answered_list:
        client_dict = {'ip': item[1].psrc, 'mac': item[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list


def print_result(clients_list):
    for client in clients_list:
        print(client)


scan_result = scan('192.168.0.1/00')
print_result(scan_result)