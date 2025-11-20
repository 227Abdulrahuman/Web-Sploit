import yaml, requests

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
data = data["Netlas"]
key = data["apiKey"]

def scrap(domain):
    url = "https://app.netlas.io/api"
    headers = {
        "Accept": "application/json",
        "X-API-Key": key
    }

    count_url = f"{url}/domains_count/"
    q = f"domain:*.{domain} AND NOT domain:{domain}"
    resp_count = requests.get(count_url, headers=headers, params={"q": q})

    if  400 <= resp_count.status_code < 500:
        return {-1}
    count = resp_count.json().get("count", 0)
    download_url = f"{url}/domains/download/"
    payload = {
        "q": q,
        "fields": ["*"],
        "source_type": "include",
        "size": count
    }

    resp_data = requests.post(download_url, headers={**headers, "Content-Type": "application/json"},json=payload)
    if  400 <= resp_data.status_code < 500:
        return {-1}

    data = resp_data.json()
    subdomains = {
        item["data"].get("domain")
        for item in data
        if "data" in item and item["data"].get("domain")
    }

    return subdomains