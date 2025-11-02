import yaml
import requests
import sys


with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)

API_KEY = data['Chaos']['apiKey']


def scrap(domain):
    url = f'https://dns.projectdiscovery.io/dns/{domain}/subdomains'

    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }

    try:
        response = requests.get(url, headers = headers)
        result = response.json()
        subdomains = set()
        for sub in result['subdomains']:
            subdomains.add(f"{sub}.{domain}")
        return subdomains

    except requests.exceptions:
            return set()

for i in scrap("jobup.ch"):
    print(i)