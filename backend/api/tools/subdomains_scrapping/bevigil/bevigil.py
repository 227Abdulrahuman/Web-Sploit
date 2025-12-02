import requests, yaml, json

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)

key = data["bevigil"]["apiKey"]

def scrap(domain):

    url = f"https://osint.bevigil.com/api/{domain}/subdomains/"
    headers = {
        "X-Access-Token" : key
    }
    subdomains = set()
    try:
        response = requests.get(url,headers=headers)
        if 400 <= response.status_code < 500:
            return {-1}

        response = response.json()

        for sub in response["subdomains"]:
            sub = sub.strip()
            if sub.endswith(f".{domain}"):
                subdomains.add(sub)
        return subdomains
    except Exception:
        return set()
