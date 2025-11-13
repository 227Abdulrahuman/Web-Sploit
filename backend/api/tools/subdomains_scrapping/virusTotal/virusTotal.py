import yaml
import requests

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)

data = data['VirusTotal']
key = data['apiKey']
headers = {'X-Apikey': key}
params = {'limit': 40}

def scrap(domain):
    url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains"
    try:
        req = requests.get(url=url, headers=headers, params=params)
        if 400 <= req.status_code < 500:
            return {-1}
        resp = req.json()
        if "data" not in resp:
            return set()
        subdomains = [item["id"] for item in resp["data"]]
        return set(subdomains)
    except Exception:
        return set()
