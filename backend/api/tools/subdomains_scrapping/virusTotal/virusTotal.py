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
    headers = {'x-apikey': key}
    params = {'limit': 40}
    subdomains = set()
    cursor = None

    try:
        while True:
            if cursor:
                params['cursor'] = cursor
            req = requests.get(url, headers=headers, params=params)
            if 400 <= req.status_code < 500:
                return {-1}
            resp = req.json()
            if "data" not in resp:
                break
            subdomains.update(item["id"] for item in resp["data"])
            cursor = resp.get("meta", {}).get("cursor")
            if not cursor:
                break

    except Exception:
        pass

    return subdomains

