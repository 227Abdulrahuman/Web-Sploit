from celery import shared_task
from backend.api.tools.subdomains import passive_enum

@shared_task

def passive_enum_task(domain):
    try:
        print(f"[*] Start Passive Enumeration: {domain}")
        passive_enum(domain)
        print(f"[*] Done Passive Enumeration: {domain}")
    except Exception as e:
        return f"Error during enumeration: {str(e)}"