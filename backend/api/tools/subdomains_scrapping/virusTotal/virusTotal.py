import yaml
import requests

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
    

data = data['VirusTotal']
key = data['apiKey']
headers = {'X-Apikey': key}
params = {'limit':40}

def scrap(domain):
    url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains"
    req = requests.get(url=url,headers=headers,params=params)
    resp = req.json()
    subdomains = [item["id"] for item in resp["data"]]
    
    result = set(subdomains)
    return result
    
