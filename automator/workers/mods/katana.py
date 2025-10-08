import subprocess
import sys
from urllib.parse import parse_qs, urlparse
import re
"""
python3 katana.py https://example.com/ example
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
        self.js = set()

def runKatana(website, domain):
    result = domainData()

    cmd = ['katana','-u',website,'-silent']
    proc = subprocess.run(cmd, capture_output=True, text=True)

    for link in proc.stdout.splitlines():
        link = link.strip()
        parsed = urlparse(link)
        
        if parsed.hostname and domain in parsed.hostname:
            loot = handelURL(link)

            if '.js' in parsed.path.lower():
                result.js.add(link)
            else:
                result.endpoints.add(loot[0])
                result.parameters.update(loot[1])
                result.urls.add(link)
            
    return result

if __name__ == '__main__':
    url = sys.argv[1]
    domain = sys.argv[2]
    result = runKatana(url, domain)

    print(f"[+] URLs: {len(result.urls)}")
    for url in result.urls:
        print(url)
        print()

    print(f"[+] Parameters: {len(result.parameters)}")
    for param in result.parameters:
        print(param)
        print()

    print(f"[+] Endpoints: {len(result.endpoints)}")
    for e in result.endpoints:
        print(e)
        print()



    print(f"[+] JS: {len(result.js)}")
    for js in result.js:
        print(js)
        print()

