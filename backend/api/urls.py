from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from api.tools.subdomains import enumerateSubdomains

api = NinjaAPI()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

@api.get("/subdomains")
def subdomains(request, domain:str):
    return enumerateSubdomains(domain)



urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]