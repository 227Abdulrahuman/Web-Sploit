import yaml
import requests


with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)


SHODAN_KEY = data['Shodan']['apiKey']
BASE_URL = "https://api.shodan.io/dns/domain"
def scrap(domain):

  page_num = 1
  subdomains = set()
  while True:
    try:
      url = f"{BASE_URL}/{domain}"
      params = {
        "key": SHODAN_KEY,
        "page": page_num
      }
      response = requests.get(url=url,params=params)

      if 400 <= response.status_code < 500:
          return {-1}

      response_data = response.json()
      prefix_subs = response_data["subdomains"]
      for prefix in prefix_subs:
        subdomains.add(f"{prefix}.{domain}")
      if response_data["more"] == False:
        break
      page_num+=1
    except Exception:
      subdomains = set()
  return subdomains


# print(scrap("wien.at"))