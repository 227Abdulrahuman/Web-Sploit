# backend/api/tasks.py

from celery import shared_task
from django.db import transaction # <-- New Import
from api.tools.subdomains import passive_enum

@shared_task
@transaction.atomic # <-- Add this decorator
def passive_enum_task(domain):
    try:
        print(f"[*] Start Passive Enumeration: {domain}")
        passive_enum(domain)
        print(f"[*] Done Passive Enumeration: {domain}")
    except Exception as e:
        # Note: If an exception occurs, transaction.atomic ensures the database rolls back.
        return f"Error during enumeration: {str(e)}"