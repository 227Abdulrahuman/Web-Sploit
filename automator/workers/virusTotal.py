import requests
import json
from urllib.parse import parse_qs, urlparse
import sys
import re

"""
Takes a domain `example.com` and returns urls,params,endpoints found in virustotal.
"""

def handelURL(url: str):
    parsed_url = urlparse(url)   
    path = re.sub(r'^(?:\./|\../)+', '/', parsed_url.path)
    path = re.sub(r'/+', '/', path)
    if not path.startswith('/'):
        path = '/' + path
    if not path.endswith('/'):
        path += '/'

    query_params = set(parse_qs(parsed_url.query, keep_blank_values=True).keys())
    return path, query_params

class domainData:
    def __init__(self):
        self.endpoints = set()
        self.parameters = set()
        self.urls = set()
        

    def __str__(self):
        return "DomainData"
    
apiKey = "2f2c977bb139ab1f04a8edbc3bc2fa15988c88c2de3e09d46aaec7167313897e"

result = domainData()

def run(domain):
    url = f"https://www.virustotal.com/vtapi/v2/domain/report?apikey={apiKey}&domain={domain}"
    response = requests.get(url)

    if __name__ == '__main__':   
        data = json.loads(response.text)
        for link in data["undetected_urls"]:
            print(link[0])
            print()

    else:
        data = json.loads(response.text)
        for link in data["undetected_urls"]:
            loot = handelURL(link[0])
            result.endpoints.add(loot[0])
            result.parameters.update(loot[1])
            result.urls.add(link[0])
        return result
    
    


if __name__ == '__main__':
    d = sys.argv[1]
    run(d)