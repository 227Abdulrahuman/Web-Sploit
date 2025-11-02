import requests

keys = {
    "SecuriryTrails" : "rntU2I9I55GNxEJ23bI75ZDXjgpsdR2v" #https://securitytrails.com/app/account/credentials
}


def securityTrails(domain):
    subs = set()
    apiKey = keys["SecuriryTrails"]
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    header = {"APIKEY":f"{apiKey}"}
    
    req = requests.get(url=url, headers=header)
    
    if req.status_code == 200:
        result = req.json()['subdomains']
        
        for sub in result:
            subs.add(f"{sub}.{domain}")
            
        print(f"[+] Found {len(subs)} subdomains from secuirty trails.")
        return subs
    else :
        print("[-] API Key Expired.")
        return set()



