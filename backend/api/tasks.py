from celery import shared_task
# from backend.api.tools.subdomains import passive_enum, dns_enum
#
# @shared_task
#
# def enum(domain):
#     try:
#         print(f"[*] Start Passive Enumeration: {domain}")
#         passive_enum(domain)
#         print(f"[*] Done Passive Enumeration: {domain}")
#     except Exception as e:
#         return f"Error during Passive enumeration: {str(e)}"
#
#     try:
#         dns_enum(domain)
#     except Exception as e:
#         return f"Error during DNS enumeration: {str(e)}"