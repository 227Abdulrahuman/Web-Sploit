import requests, yaml, json

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)

key = data["DigitalYama"]["apiKey"]
def scrap(domain):
    url = f"https://api.digitalyama.com/subdomain_finder?domain={domain}"
    headers = {
        "x-api-key" : key
    }
    subdomains = set()

    try:
        response = requests.get(url,headers=headers)
        if 400 <= response.status_code < 500:
            return {-1}

        res = response.json()
        for sub in res["subdomains"]:
            subdomains.add(sub)
        return subdomains
    except Exception:
        return set()

