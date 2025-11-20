import requests
import yaml

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)

CHAOS_KEY = data['Chaos']['apiKey']  
BASE_URL = "https://dns.projectdiscovery.io/dns"


def scrap(domain):
    headers = {"Authorization": CHAOS_KEY}
    url = f"{BASE_URL}/{domain}/subdomains"
    subdomains = set()
    try:
        response =  requests.get(url, headers=headers)

        if 400 <= response.status_code < 500:
            return {-1}

        subs = response.json()["subdomains"]
        for subdomain in subs:
            full_subdomain = f"{subdomain}.{domain}"
            if full_subdomain[0] == '*' and full_subdomain[1] == '.':
                full_subdomain = full_subdomain[2:]
            subdomains.add(full_subdomain)
    except Exception as e:
        subdomains = set()
    return subdomains
