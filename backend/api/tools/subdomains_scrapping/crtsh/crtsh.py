import requests
import json


def scrap(domain):
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)

        if r.status_code != 200:
            return {-1}

        try:
            data = json.loads(r.text)
        except json.JSONDecodeError:
            return {-1}

        subdomains = set()

        for entry in data:
            name = entry.get("name_value")
            if name:
                for line in name.split("\n"):
                    line = line.strip()
                    if line.endswith(f".{domain}"):
                        subdomains.add(line)

        return sorted(subdomains)

    except Exception as e:
        return {-1}

