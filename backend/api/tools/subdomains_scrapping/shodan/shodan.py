import yaml
import requests


with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
    
    
data = data['Shodan']
Key = data['apiKey']

def scrap(domain):
  
  
  page_num = 1
  
  subs = set()
  
  while True:
    try:
      url = f"https://api.shodan.io/dns/domain/{domain}?key={Key}&page={page_num}"
      
      response = requests.get(url=url)
      
      response_data = response.json()
      prefix_subs = response_data["subdomains"]
      
      for prefix in prefix_subs:
        subs.add(f"{prefix}.{domain}")
        
      

      if response_data["more"] == False:
        break
      
      page_num+=1
      
    except Exception as Ex:
      subs = set()  
      
  return subs
  # print("found " , len(subs) , f" subdomains in {page_num} pages\n")
    
