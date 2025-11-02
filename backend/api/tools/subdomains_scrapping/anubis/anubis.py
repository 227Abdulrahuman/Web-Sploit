import requests


def scrap(domain):
    try:
        response = requests.get(f"https://anubisdb.com/subdomains/{domain}")
        response = response.json()
        subdomains = set()
        
        for sub in response:
            subdomains.add(sub)
            
        return subdomains
    except Exception:
        return set()