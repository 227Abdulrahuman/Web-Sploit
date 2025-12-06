from django.db import models



class Company(models.Model):
    name = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.name


class Domain(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="domains")
    hostname = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.hostname

class Subdomain(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="subdomains")
    is_alive = models.BooleanField(default=False)
    hostname = models.CharField(max_length=1000)
    cname = models.CharField(max_length=1000, null=True, blank=True)
    ip = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        unique_together = ("domain", "hostname")

    def __str__(self):
        return self.hostname


class Port(models.Model):
    subdomain = models.ForeignKey(Subdomain, on_delete=models.CASCADE, related_name="ports")
    port_number = models.IntegerField()

    class Meta:
        unique_together = ("subdomain", "port_number")

    def __str__(self):
        return f"{self.subdomain}:{self.port_number}"

class HTTPX(models.Model):
    subdomain = models.ForeignKey(Subdomain, on_delete=models.CASCADE, related_name="httpx")
    status_code = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=1000000,null=True, blank=True)
    content_length = models.IntegerField(null=True, blank=True)
    tech = models.JSONField(default=list,null=True, blank=True)
    location = models.CharField(max_length=1000000,null=True, blank=True)
    title = models.CharField(max_length=1000000,null=True, blank=True)

    class Meta:
        unique_together = ("subdomain", "url")