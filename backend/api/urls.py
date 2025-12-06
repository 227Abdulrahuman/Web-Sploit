from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
# from backend.api.tasks import enum
from backend.core.models import *
from ninja.responses import Response

api = NinjaAPI()

@api.get("addCompany")
def add_company(request, company_name:str):
    if Company.objects.filter(name=company_name).exists():
        return Response({"error":"Company already exists"}, status=400)
    else:
        Company.objects.create(name=company_name)
        return Response({"status":"success"}, status=201)

@api.get("addDomain")
def add_domain(request, domain_name:str, company_name:str):
    domain_name = domain_name.lower()
    if Domain.objects.filter(hostname=domain_name).exists():
        return Response({"error":"Domain already exists"}, status=400)
    else:
        company, created = Company.objects.get_or_create(name=company_name)
        Domain.objects.create(hostname=domain_name, company=company)
        return Response({"status":"success"}, status=201)



# @api.get("recon")
# def start_passive_enum(request, domain:str):
#     enum.delay(domain)
#     return {"result": f"passive enum for {domain} task started" }


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]