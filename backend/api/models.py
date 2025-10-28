from django.db import models

# This model stores your scan results in the database.
# It matches the full schema we discussed earlier.
class HostScan(models.Model):
    # Hostname is the unique identifier
    hostname = models.CharField(max_length=255, unique=True, primary_key=True)
    
    ip = models.GenericIPAddressField(null=True, blank=True)
    ports = models.JSONField(default=list)
    cnames = models.JSONField(default=list)
    
    ptr = models.CharField(max_length=255, null=True, blank=True)
    txt = models.TextField(null=True, blank=True)
    subs = models.JSONField(default=list)
    live_subs = models.JSONField(default=list)
    
    waf = models.CharField(max_length=100, null=True, blank=True)
    technology = models.CharField(max_length=255, null=True, blank=True)
    
    crawled_urls = models.JSONField(default=list)
    archived_urls = models.JSONField(default=list)
    virustotal_urls = models.JSONField(default=list)
    all_urls = models.JSONField(default=list)
    parameters = models.JSONField(default=list)
    endpoints = models.JSONField(default=list)
    js_files = models.JSONField(default=list)
    js_secrets = models.JSONField(default=list)
    js_urls = models.JSONField(default=list)
    js_endpoints = models.JSONField(default=list)
    
    vuln = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hostname
