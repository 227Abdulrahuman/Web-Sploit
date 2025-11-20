import yaml, requests

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
key = data["Leakix"]["apiKey"]

def scrap(domain):
    url = f"https://leakix.net/api/subdomains/{domain}"
    headers = {
        "Accept": "application/json",
        "api-key": key
    }
    response = requests.get(url, headers=headers)
    if 400 <= response.status_code < 500:
        return {-1}

    response = response.json()

    subdomains = set()
    for item in response:
        subdomains.add(item["subdomain"])

    return subdomains

