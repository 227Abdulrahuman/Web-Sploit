from celery import shared_task
from backend.api.tools.subdomains import passive_enum, dns_enum, ports_enum, http_enum

@shared_task
def enum(domain):
    try:
        passive_enum(domain)
    except Exception as e:
        return f"Error during Passive enumeration: {str(e)}"

    try:
        dns_enum(domain)
    except Exception as e:
        return f"Error during DNS enumeration: {str(e)}"

    try:
        ports_enum(domain)
    except Exception as e:
        return f"Error during DNS enumeration: {str(e)}"

    try:
        http_enum(domain)
    except Exception as e:
        return f"Error during HTTP enumeration: {str(e)}"
