import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

from django.core.management.base import BaseCommand
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()

from core.models import Domain, Subdomain


TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../api/tools')
sys.path.insert(0, TOOLS_DIR)

# Import all scrapers
from subdomains_scrapping.alienVault.alienVault import scrap as alienVaultScrap
from subdomains_scrapping.anubis.anubis import scrap as anubisScrap
from subdomains_scrapping.bevigil.bevigil import scrap as bevigilScrap
from subdomains_scrapping.c99.c99 import scrap as c99Scrap
from subdomains_scrapping.certspotter.certspotter import scrap as certspotterScrap
from subdomains_scrapping.chaos.chaos import scrap as chaosScrap
from subdomains_scrapping.crtsh.crtsh import scrap as crtshScrap
from subdomains_scrapping.digitalYama.digitalYama import scrap as digitalYamaScrap
from subdomains_scrapping.dnsDumpster.dnsDumpster import scrap as dnsDumpsterScrap
from subdomains_scrapping.fullHunt.fullHunt import scrap as fullHuntScrap
from subdomains_scrapping.leakix.leakix import scrap as leakixScrap
from subdomains_scrapping.netlas.netlas import scrap as netlasScrap
from subdomains_scrapping.pugRecon.pugRecon import scrap as pugReconScrap
from subdomains_scrapping.securityTrails.securityTrails import scrap as securityTrailsScrap
from subdomains_scrapping.shodan.shodan import scrap as shodanScrap
from subdomains_scrapping.urlScan.urlScan import scrap as urlScanScrap
from subdomains_scrapping.virusTotal.virusTotal import scrap as virusTotalScrap

class Command(BaseCommand):
    help = "Run passive enumeration for a domain"

    def add_arguments(self, parser):
        parser.add_argument(
            'domain', type=str, help="The base domain to enumerate, e.g. jobs.ch"
        )

    def handle(self, *args, **options):
        base_domain = options['domain']
        self.passive_enum(base_domain)

    def run_scraper(self, name, func, domain, output_dir):
        try:
            result = func(domain)

            if result == {-1}:
                print(f"[-] {name} key expired.")
                return (name, 0, [])

            filepath = f"{output_dir}/{name}.txt"
            with open(filepath, "w") as f:
                for sub in result:
                    f.write(sub + "\n")

            count = len(result)
            print(f"[+] {name} found {count} subdomains.")
            return (name, count, result)

        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            return (name, 0, [])

    def save_subdomains(self, base_domain, subs, live):
        domain = Domain.objects.get(hostname=base_domain)
        for hostname in subs:
            is_alive = hostname in live
            Subdomain.objects.get_or_create(
                domain=domain,
                hostname=hostname,
                defaults={"is_alive": is_alive}
            )

    def passive_enum(self, domain):
        output_dir = f"/work/backend/api/tools/output/{domain}/scrapers"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        scrapers = [
            ("securityTrails", securityTrailsScrap),
            ("anubis", anubisScrap),
            ("bevigil", bevigilScrap),
            ("c99", c99Scrap),
            ("certspotter", certspotterScrap),
            ("chaos", chaosScrap),
            ("crtsh", crtshScrap),
            ("dnsDumpster", dnsDumpsterScrap),
            ("fullHunt", fullHuntScrap),
            ("leakix", leakixScrap),
            ("netlas", netlasScrap),
            ("pugRecon", pugReconScrap),
            ("shodan", shodanScrap),
            ("digitalYama", digitalYamaScrap),
            ("urlScan", urlScanScrap),
            ("virusTotal", virusTotalScrap),
            ("alienVault", alienVaultScrap),
        ]

        print(f"[+] Starting Passive Enumeration for {domain}\n")

        results = {}
        all_subdomains = set()

        with ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
            futures = {
                executor.submit(self.run_scraper, name, func, domain, output_dir): name
                for name, func in scrapers
            }
            for future in as_completed(futures):
                name, count, subs = future.result()
                results[name] = count
                all_subdomains.update(subs)

        passive_file = f"/work/backend/api/tools/output/{domain}/passive.txt"
        live_file = f"/work/backend/api/tools/output/{domain}/live.txt"

        with open(passive_file, "w") as f:
            for sub in sorted(all_subdomains):
                f.write(sub + "\n")

        cmd = [
            '/work/backend/api/tools/bin/puredns', 'resolve', passive_file,
            '-r', '/work/backend/api/tools/data/resolvers.txt',
            '-w', live_file
        ]
        subprocess.run(cmd, text=True, capture_output=True)

        totalLive = set()
        with open(live_file, "r") as f:
            for line in f:
                sub = line.strip()
                if sub.endswith(f".{domain}"):
                    totalLive.add(sub)

        with open(live_file, "w") as f:
            for sub in sorted(totalLive):
                f.write(sub + "\n")

        print(f"\n[+] Live subdomains: {len(totalLive)}\n")
        print(f"[+] Total subdomains: {len(all_subdomains)}\n")

        self.save_subdomains(domain, all_subdomains, totalLive)
