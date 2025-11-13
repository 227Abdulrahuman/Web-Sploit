import requests
import yaml

with open('/work/backend/.config/provider.yaml') as file:
  data = yaml.safe_load(file)


URLSCAN = data['UrlScan']
KEY = URLSCAN['apiKey']
SUBDOMAINS_LINK = URLSCAN['linkToGetSubdomains']
def scarp(domain):

  headers = {"Authintication": KEY}
  url = SUBDOMAINS_LINK
  params = { "q": domain}
  subdomains = set()
  try:
    response = requests.get(url=url,headers=headers,params=params).json()
    results = response["results"]
    for item in results:
      sub1 = [item["task"]["domain"],item["page"]["domain"]]
      for i in sub1:
        if f".{domain}" in i:
          subdomains.add(i)
  except Exception:
    subdomains = set()
  return subdomains
# scarp('uber.ch')