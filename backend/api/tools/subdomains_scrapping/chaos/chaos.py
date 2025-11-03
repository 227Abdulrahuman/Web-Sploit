import requests
import time
import yaml

# Load Chaos API key from your config file
with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)

CHAOS_KEY = data['Chaos']['apiKey']  # adjust to match your YAML structure
BASE_URL = "https://dns.projectdiscovery.io/dns"


def get_subdomains(domain):
    headers = {"Authorization": CHAOS_KEY}
    url = f"{BASE_URL}/{domain}/subdomains"
    subdomains = set()

    try:
        response =  requests.get(url, headers=headers)
        # print(response.text)
        subs = response.json()["subdomains"]
        
        for subdomain in subs:
          full_subdomain = f"{subdomain}.{domain}"
          print(full_subdomain)
          subdomains.add(full_subdomain)
        
        print(f"Found {len(subdomains)} subdomains for {domain}")
    except Exception as e:
        subdomains = set()
    return subdomains

# domain = "wien.at"
# get_subdomains(domain=domain)
