from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from core.models import Domain
import json
import time
from celery import shared_task
from api.tasks import test2


api = NinjaAPI()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

#Test Celery Endpoint.
@api.get("/celery")
def run(request, a:int):
    test2.delay()
    return {"status": 200}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]