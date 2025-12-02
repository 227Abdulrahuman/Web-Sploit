import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC

def scrap(domain, days_back = 30) :

    subdomains = set()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"}

    for i in range(days_back):
        date = (datetime.now(UTC) - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://subdomainfinder.c99.nl/scans/{date}/{domain}"

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            for a in soup.find_all("a"):
                href = a.get("href", "")

                if "subdomainfinder.c99.nl/scans" in href:
                    continue

                if domain in href:
                    clean = href.lstrip("/").lstrip("/")
                    clean = clean.strip()
                    if clean.endswith(f".{domain}"):
                        subdomains.add(clean)

            if subdomains:
                return subdomains

        except Exception:
            continue

    return subdomains

