from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from .models import HostScan
from .schemas import HostScanSchema, ErrorSchema

# Create a router to group our "scan" endpoints
router = Router(tags=["Scan Management (CRUD)"])

@router.post(
    "/",
    response={201: HostScanSchema, 200: HostScanSchema},
    summary="Create or Update a Host Scan Result"
)
def create_or_update_scan(request, payload: HostScanSchema):
    data = payload.dict()
    hostname = data.pop("hostname")
    
    scan, created = HostScan.objects.update_or_create(
        hostname=hostname,
        defaults=data
    )
    
    status_code = 201 if created else 200
    return status_code, scan

@router.get(
    "/",
    response=List[HostScanSchema],
    summary="List All Saved Scan Results"
)
def list_scans(request):
    scans = HostScan.objects.all()
    return scans

@router.get(
    "/{hostname}",
    response={200: HostScanSchema, 404: ErrorSchema},
    summary="Retrieve a Specific Scan Result"
)
def get_scan(request, hostname: str):
    scan = get_object_or_404(HostScan, hostname=hostname)
    return 200, scan

@router.delete(
    "/{hostname}",
    response={204: None, 404: ErrorSchema},
    summary="Delete a Scan Result"
)
def delete_scan(request, hostname: str):
    scan = get_object_or_404(HostScan, hostname=hostname)
    scan.delete()
    return 204, None
