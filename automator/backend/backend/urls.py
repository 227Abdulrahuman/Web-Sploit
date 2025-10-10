from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from backend.tools.subdomains import enumerateSubdomains
import json

def to_json_safe(obj):
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_json_safe(i) for i in obj]
    return obj


api = NinjaAPI()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

@api.get('/GatherSubs')
def GatherSubs(request, domain:str):
    res = enumerateSubdomains(domain)
    res = to_json_safe(res)
    return res


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]