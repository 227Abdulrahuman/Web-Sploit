import yaml, requests

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
data = data["DnsDumpster"]
key = data["apiKey"]


def scrap(domain):
    url = f"https://api.dnsdumpster.com/domain/{domain}"
    headers = {
        "X-API-Key": key
    }

    response = requests.get(url, headers=headers)
    if 400 <= response.status_code < 500:
        return {-1}
    else:
        try:
            response = response.json()
            subdomains = set(record['host'] for record in response.get('a', []))
            return subdomains
        except Exception:
            return set()
