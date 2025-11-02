import yaml
import requests
import sys


with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file) 
API_KEY = data['SecurityTrails']['apiKey']


def scrap(domain):
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {
        "accept" : "application/json",
        "APIKEY" : API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        subdomains = set()

        for sub in result['subdomains']:
            subdomains.add(f"{sub}.{domain}")

        return subdomains
        

    except requests.exceptions:
        return set()


scrap("jobs.ch")

