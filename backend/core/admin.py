from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Domain)
admin.site.register(models.Company)

@admin.register(models.Subdomain)
class SubdomainAdmin(admin.ModelAdmin):
    list_display = ("hostname","ip","cname","is_alive")
