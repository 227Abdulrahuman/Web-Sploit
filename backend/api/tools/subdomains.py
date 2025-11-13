import sys
import os
from pathlib import Path
from subdomains_scrapping.securityTrails.securityTrails import scrap as securityTrailsScrap
from subdomains_scrapping.digitalYama.digitalYama import scrap as digitalYamaScrap

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def enum(domain):
    output_dir = f"/work/backend/api/tools/output/{domain}"
    p = Path(output_dir)
    p.mkdir(parents=True, exist_ok=True)

    #1) Security Trails
    securityTrailsResult = securityTrailsScrap(domain)
    if securityTrailsResult == {-1}:
        print("Security Trails key expired.")
    else:
        with open(f"{output_dir}/securityTrails.txt", "w") as file:
            for subdomain in securityTrailsResult:
                file.write(f"{subdomain}\n")


    #2) Digital Yama
    digitalYamaResult = digitalYamaScrap(domain)
    if digitalYamaResult == {-1}:
        print("Digital Yama key expired.")
    else:
        with open(f"{output_dir}/digitalYama.txt", "w") as file:
            for subdomain in digitalYamaResult:
                file.write(f"{subdomain}\n")

enum("jobs.ch")