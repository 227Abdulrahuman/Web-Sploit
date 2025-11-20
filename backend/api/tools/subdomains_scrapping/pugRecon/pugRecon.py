import yaml, requests

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
key = data["PugRecon"]["apiKey"]


def scrap(domain):
    url = "https://pugrecon.com/api/v1/domains"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {"domain_name": domain}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if 400 <= response.status_code < 500:
            return {-1}

        data = response.json()
        subdomains = set()
        for item in data.get("results", []):
            subdomains.add(item.get("name"))

        return subdomains

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return set()



for i in scrap("jobs.ch"):
    print(i)