import os,sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
sys.path.insert(0, "/work")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.api.settings")

#Intialize the Django.
import django
django.setup()

#Import the scrapers.
from backend.api.tools.subdomains_scrapping.virusTotal.virusTotal import scrap as virustotal_scrap
from backend.api.tools.subdomains_scrapping.chaos.chaos import scrap as chaos_scrap
from backend.api.tools.subdomains_scrapping.crtsh.crtsh import scrap as crtsh_scrap


#Import the Modes.
from backend.core.models import Subdomain, Domain

def run_scraper(name, func, domain,scrapers_dir):
    try:
        result = func(domain)

        if result == {-1}:
            print(f"[-] {name} key expired.")
            return

        with open(f"{scrapers_dir}/{name}.txt", "w") as f:
            for subdomain in result:
                subdomain = subdomain.strip()
                if subdomain.endswith(f".{domain}"):
                    f.write(f"{subdomain}\n")

        print(f"[+] {name}: {len(result)} subdomains.")

    except Exception as e:
        print(f"[Error] {name}: {e}")

def passive_enum(domain):
    # Creating the output directory.
    base_dir = f"/work/backend/api/tools/output/{domain}"
    scrapers_dir = f"{base_dir}/scrapers"
    os.makedirs(scrapers_dir, exist_ok=True)

    #Run Scrapers in parallel.
    scrapers = [
        ("Chaos", chaos_scrap),
        ("Crtsh", crtsh_scrap),
        ("VirusTotal", virustotal_scrap),
    ]
    with ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
        futures = {
            executor.submit(run_scraper, name, func, domain,scrapers_dir): name
            for name, func in scrapers
        }

    #Save the results into passive.txt
    cmd = f"cat /work/backend/api/tools/output/{domain}/scrapers/*.txt | sort | uniq > /work/backend/api/tools/output/{domain}/passive.txt"
    subprocess.run(cmd, shell=True, check=True)

    #Resolve the live domains into live.txt
    passive_file = f"/work/backend/api/tools/output/{domain}/passive.txt"
    resolvers_file = f"/work/backend/api/tools/data/resolvers.txt"
    live_file = f"/work/backend/api/tools/output/{domain}/live.txt"
    cmd = ['puredns', 'resolve', passive_file, '-r', resolvers_file, '-w', live_file]
    subprocess.run(cmd, text=True, capture_output=True)

    #Sort and Uniq on live.txt
    with open(live_file) as f:
        lines = sorted(set(line.strip() for line in f if line.strip()))
    with open(live_file, "w") as f:
        for line in lines:
            f.write(line + "\n")

    #Insert the results into the database
    with open(passive_file) as f:
        passive_subdomains = set(line.strip() for line in f if line.strip())
    with open(live_file) as f:
        live_subdomains = set(line.strip() for line in f if line.strip())
    domain_obj = Domain.objects.get(hostname=domain)
    for sub in passive_subdomains:
        is_alive = sub in live_subdomains
        Subdomain.objects.update_or_create(
            domain=domain_obj,
            hostname=sub,
            defaults={"is_alive": is_alive},
        )
