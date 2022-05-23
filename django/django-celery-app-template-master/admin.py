from django.contrib import admin
from {{ app_name }}.models import *


class DemoAdmin(admin.ModelAdmin):
    fields = ((),)
    list_display = ()
    list_filter = ()
    search_fields = ()

admin.site.register(Demo, DemoAdmin)
