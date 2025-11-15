import yaml, requests, json

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
data = data["certspotter"]
key = data["apiKey"]


def scrap(domain):

    url = f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names"
    headers = {
        "Authorization" : f"Bearer {key}",
    }
    try:
        response = requests.get(url, headers=headers)
        if 400 <= response.status_code < 500:
            return {-1}

        response = response.json()

        subdomains = set()

        for cert in response:
            for sub in cert["dns_names"]:
                subdomains.add(sub)

        return subdomains

    except Exception:
        return set()

