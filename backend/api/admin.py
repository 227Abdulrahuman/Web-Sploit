from django.contrib import admin
from .models import HostScan

@admin.register(HostScan)
class HostScanAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'ip', 'waf', 'technology', 'updated_at')
    search_fields = ('hostname', 'ip')
