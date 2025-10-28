from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from typing import List
import json  # <-- Import the json module

# Imports from your project
from api.tools.subdomains import enumerateSubdomains

# Imports for the new database models and API
from api.models import HostScan
from api.schemas import HostScanSchema
from api.api_views import router as scans_router

api = NinjaAPI()

@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}

@api.get("/subdomains", response=List[HostScanSchema], summary="Run and Save Subdomain Scan")
def subdomains(request, domain:str):
    # Your function returns a JSON string, not a Python list
    json_string_results = enumerateSubdomains(domain) 
    
    try:
        results = json.loads(json_string_results)
    except json.JSONDecodeError:
        # Handle case where the string might be empty or invalid
        return 400, {"message": "Invalid JSON response from subdomain tool"}
    
    saved_scans = []
    for sub_data in results:
        # Now sub_data is a dict, and sub_data['hostname'] will work
        scan, created = HostScan.objects.update_or_create(
            hostname=sub_data['hostname'],
            defaults={
                'ip': sub_data.get('ip'),
                'ports': sub_data.get('ports', []),
                'cnames': sub_data.get('cnames', [])
            }
        )
        saved_scans.append(scan)
        
    return saved_scans

api.add_router("/scans", scans_router)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
