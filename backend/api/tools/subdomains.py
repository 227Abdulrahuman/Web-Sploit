import os,sys, json
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
sys.path.insert(0, "/work")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.api.settings")

#Intialize the Django.
import django
django.setup()

#Import the scrapers.
from backend.api.tools.subdomains_scrapping.alienVault.alienVault import scrap as alienvault_scrap
from backend.api.tools.subdomains_scrapping.anubis.anubis import scrap as anubis_scrap
from backend.api.tools.subdomains_scrapping.bevigil.bevigil import scrap as bevigil_scrap #Bad Scraper.
from backend.api.tools.subdomains_scrapping.c99.c99 import scrap as c99_scrap
from backend.api.tools.subdomains_scrapping.certspotter.certspotter import scrap as certspotter_scrap
from backend.api.tools.subdomains_scrapping.chaos.chaos import scrap as chaos_scrap
from backend.api.tools.subdomains_scrapping.crtsh.crtsh import scrap as crtsh_scrap
from backend.api.tools.subdomains_scrapping.dnsDumpster.dnsDumpster import scrap as dnsDumpster_scrap
from backend.api.tools.subdomains_scrapping.fullHunt.fullHunt import scrap as fullHunt_scrap
from backend.api.tools.subdomains_scrapping.leakix.leakix import scrap as leakix_scrap
from backend.api.tools.subdomains_scrapping.netlas.netlas import scrap as netlas_scrap
from backend.api.tools.subdomains_scrapping.pugRecon.pugRecon import scrap as pugRecon_scrap
from backend.api.tools.subdomains_scrapping.securityTrails.securityTrails import scrap as securityTrails_scrap
from backend.api.tools.subdomains_scrapping.shodan.shodan import scrap as shodan_scrap
from backend.api.tools.subdomains_scrapping.virusTotal.virusTotal import scrap as virusTotal_scrap
#Import the Modes.
from backend.core.models import Subdomain, Domain, Port, HTTPX

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

# Takes a domain and scarps the subdomains into passive.txt and the live ones into live.txt and inserts them to the database.
def passive_enum(domain):
    # Creating the output directory.
    base_dir = f"/work/backend/api/tools/output/{domain}"
    scrapers_dir = f"{base_dir}/scrapers"
    os.makedirs(scrapers_dir, exist_ok=True)

    #Run Scrapers in parallel.
    scrapers = [
        ("AlienVault", alienvault_scrap),
        ("Anubis", anubis_scrap),
        ("Bevigil", bevigil_scrap),
        ("C99", c99_scrap),
        ("Certspotter", certspotter_scrap),
        ("Chaos", chaos_scrap),
        ("Crtsh", crtsh_scrap),
        ("DnsDumpster", dnsDumpster_scrap),
        ("FullHunt", fullHunt_scrap),
        ("LeakiX", leakix_scrap),
        ("Netlas", netlas_scrap),
        ("PugRecon", pugRecon_scrap),
        ("SecurityTrails", securityTrails_scrap),
        ("Shodan", shodan_scrap),
        ("VirusTotal", virusTotal_scrap),

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

    print(f"[+] Found {len(live_subdomains)} live subdomains.")

#Takes a domain and resolves cnames and ips into the database Depends on passive_enum.
def dns_enum(domain):
    domain_obj = Domain.objects.get(hostname=domain)

    #Get the cnames and IPs from DNSX.
    output_file = f"/work/backend/api/tools/output/{domain}/dns.json"
    live_file = f"/work/backend/api/tools/output/{domain}/live.txt"
    cmd = [
        'dnsx', '-l', live_file,
        '-a', '-cname',
        '-silent', '-nc', '-resp',
        '-j', '-o', output_file
    ]

    print(f"[+] Starting DNS scan for {domain}")
    subprocess.run(cmd, text=True, capture_output=True)

    with open(output_file, 'r') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
                Subdomain.objects.update_or_create(
                    domain=domain_obj,
                    hostname=data.get('host'),
                    defaults={
                        "is_alive": True,
                        "cname": data.get('cname')[-1] if data.get('cname') else None,
                        "ip": data.get('a')[0] if data.get('a') else None,
                    }
                )
            except Exception:
                pass
    print(f"Finished DNS scan for {domain}")

#Takes a domain an scan for ports and saves it to ports.json Depends on passive_enum.
def ports_enum(domain):
    output_file = f"/work/backend/api/tools/output/{domain}/ports.json"
    live_file = f"/work/backend/api/tools/output/{domain}/live.txt"

    cmd = [
        'naabu', '-l', live_file,
        '-nc', '-silent',
        '-j', '-o', output_file,
    ]

    subprocess.run(cmd, text=True, capture_output=True)

    with open(output_file, 'r') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue
            try:
                data = json.loads(line)
                host = data.get('host')
                port = data.get('port')

                subdomain_obj = Subdomain.objects.get(hostname=host)
                Port.objects.update_or_create(
                    subdomain=subdomain_obj,
                    port_number=int(port),
                )
            except Exception:
                pass

#Takes a domain and runs httpx on it and saves to http.json depends on passive_enum.
def http_enum(domain):
    output_file = f"/work/backend/api/tools/output/{domain}/http.json"
    live_file = f"/work/backend/api/tools/output/{domain}/live.txt"

    print(f"[+] Starting Web Fingerprinting for {domain}")

    cmd = [
        'httpx', '-l', live_file,
        '-nc', '-silent',
        '-sc', '-title', '-location',
        '-j', '-o', output_file,
    ]
    subprocess.run(cmd, text=True, capture_output=True)

    with open(output_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)

                url = data.get('url')
                host_name = data.get('input')
                status_code = data.get('status_code')
                content_length = data.get('content_length')
                tech = data.get('tech')
                title = data.get('title')
                location = data.get('location')

                subdomain_obj = Subdomain.objects.get(hostname=host_name)
                HTTPX.objects.update_or_create(
                    subdomain=subdomain_obj,
                    url=url,
                    defaults={
                        "status_code": status_code,
                        "content_length": content_length,
                        "tech": tech,
                        "title": title,
                        "location": location,
                    }
                )
            except Exception:
                pass

    print(f"[+] Done Web Fingerprinting for {domain}")