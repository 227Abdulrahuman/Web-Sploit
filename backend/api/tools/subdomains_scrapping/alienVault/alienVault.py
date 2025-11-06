import yaml, requests, json

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
data = data["AlienVault"]
key = data["apiKey"]


def scrap(domain):

    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
    headers = {
        "Authorization" : f"Bearer {key}",
    }
    try:
        response = requests.get(url, headers=headers)
        response = response.json()

        subdomains = set()

        for entry in response["passive_dns"]:
            subdomains.add(entry["hostname"])

        return subdomains

    except Exception:
        return set()

