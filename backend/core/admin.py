from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Domain)
admin.site.register(models.Company)
admin.site.register(models.Port)

@admin.register(models.Subdomain)
class SubdomainAdmin(admin.ModelAdmin):
    list_display = ("hostname","ip","cname","is_alive")

@admin.register(models.HTTPX)
class HTTPXAdmin(admin.ModelAdmin):
    list_display = ("url", "title", "status_code", "location", "tech", "content_length" )
