from django.db import models

# Create your models here.


class Domain(models.Model):

    def __str__(self):
        return self.hostname

    hostname = models.CharField(max_length=1000, unique=True)
    ip = models.CharField(max_length=1000)
    ports = models.TextField()#[80,443]





