import requests, yaml, json

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)

def scrap(domain):
    key = data["bevigil"]["apiKey"]
    url = f"https://osint.bevigil.com/api/{domain}/subdomains/"
    headers = {
        "X-Access-Token" : key
    }
    subdomains = set()
    try:
        response = requests.get(url,headers=headers).json()
        for sub in response["subdomains"]:
            subdomains.add(sub)
        return subdomains
    except Exception:
        return set()


for i in scrap("jobs.ch"):
    print(i)