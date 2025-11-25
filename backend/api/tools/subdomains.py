import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
from django.conf import settings
from api.tools.subdomains_scrapping.chaos.chaos import scrap as chaosScrap


def run_scraper(name, func, domain, output_dir):
    try:
        result = func(domain)

        if result == {-1}:
            print(f"[-] {name} key expired.")
            return (name, 0, [])

        filepath = os.path.join(output_dir, f"{name}.txt")
        with open(filepath, "w") as f:
            for sub in result:
                f.write(sub + "\n")

        count = len(result)
        print(f"[+] {name} found {count} subdomains.")

        return (name, count, result)

    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return (name, 0, [])


def save_subdomains(base_domain, subs, live):
    from core.models import Domain, Subdomain

    try:
        domain = Domain.objects.get(hostname=base_domain)

        for hostname in subs:
            is_alive = hostname in live

            try:
                Subdomain.objects.update_or_create(
                    domain=domain,
                    hostname=hostname,
                    defaults={"is_alive": is_alive}
                )
            except Exception as e:
                print(f"[INNER DB ERROR] Failed to save {hostname}: {e}")

    except Domain.DoesNotExist:
        print(f"[ERROR] Domain {base_domain} not found in database.")
    except Exception as e:
        print(f"[CRITICAL SAVE ERROR] Global failure for {base_domain}: {e}")

def passive_enum(domain):
    base_tools_dir = os.path.join(settings.BASE_DIR, 'api', 'tools')

    output_root = os.path.join(base_tools_dir, 'output', domain)
    output_dir = os.path.join(output_root, 'scrapers')

    passive_file = os.path.join(output_root, 'passive.txt')
    live_file = os.path.join(output_root, 'live.txt')
    resolvers_file = os.path.join(base_tools_dir, 'data', 'resolvers.txt')
    puredns_bin = os.path.join(base_tools_dir, 'bin', 'puredns')


    p = Path(output_dir)
    p.mkdir(parents=True, exist_ok=True)

    scrapers = [
        ("chaos", chaosScrap),
    ]

    print(f"[+] Starting Passive Enumeration for {domain}\n")

    results = {}
    all_subdomains = set()

    with ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
        futures = {
            executor.submit(run_scraper, name, func, domain, output_dir): name
            for name, func in scrapers
        }

        for future in as_completed(futures):
            name, count, subs = future.result()
            results[name] = count
            all_subdomains.update(subs)

    # Write passive file
    with open(passive_file, "w") as f:
        for sub in sorted(all_subdomains):
            f.write(sub + "\n")

    # Resolve subdomains using puredns
    cmd = [puredns_bin, 'resolve', passive_file, '-r', resolvers_file, '-w', live_file]

    try:
        subprocess.run(cmd, text=True, capture_output=True, check=True)
    except FileNotFoundError:
        print(f"[ERROR] Could not find puredns at {puredns_bin}. Ensure it's compiled and executable.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Puredns failed for {domain}: {e.stderr}")

    totalLive = set()
    if os.path.exists(live_file):
        with open(live_file, "r") as f:
            for line in f:
                sub = line.strip()
                if sub.endswith(f".{domain}") or sub == domain:
                    totalLive.add(sub)

        with open(live_file, "w") as f:
            for sub in sorted(totalLive):
                f.write(sub + "\n")

    print(f"[+] Total live subdomains: {len(totalLive)}\n")

    save_subdomains(domain, all_subdomains, totalLive)