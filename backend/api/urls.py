from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from backend.api.tasks import passive_enum_task
from backend.core.models import Subdomain, Domain, Company

api = NinjaAPI()

@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

@api.get("start_passive_enum")
def start_passive_enum(request, domain:str):
    passive_enum_task.delay(domain)
    return {"result": f"passive enum for {domain} task started" }


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]