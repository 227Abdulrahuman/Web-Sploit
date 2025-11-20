import requests

def scrap(domain):
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        req = requests.get(url)
        req = req.json()

        subdomains = set()

        for field in req:
            cn = field['common_name']
            if cn.endswith(f".{domain}"):
                if cn[0] == '*' and cn[1] == '.':
                    cn = cn[2:]
                subdomains.add(cn)

            name_value = field['name_value']
            if name_value.endswith(f".{domain}"):
                if name_value[0] == '*' and name_value[1] == '.':
                    name_value = cn[2:]
                subdomains.add(name_value)
        return subdomains
    except Exception:
        return set()


for i in scrap("jobs.ch"):
    print(i)