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
    # securityTrailsResult = securityTrailsScrap(domain)
    # if securityTrailsResult == {-1}:
    #     print("Security Trails key expired.")
    # else:
    #     with open(f"{output_dir}/securityTrails.txt", "w") as file:
    #         for subdomain in securityTrailsResult:
    #             file.write(f"{subdomain}\n")


    #
    #
    # #2) Digital Yama
    # # digitalYamaResult = digitalYamaScrap(domain)
    # # if digitalYamaResult == {-1}:
    # #     print("Digital Yama key expired.")
    # # else:
    # #     with open(f"{output_dir}/digitalYama.txt", "w") as file:
    # #         for subdomain in digitalYamaResult:
    # #             file.write(f"{subdomain}\n")
    #
    #
    # #3) Anubis
    # # from subdomains_scrapping.anubis.anubis import scrap as anubisScrap
    # # anubisResult = anubisScrap(domain)
    # # with open(f"{output_dir}/anubis.txt", "w") as file:
    # #     for subdomain in anubisResult:
    # #         file.write(f"{subdomain}\n")
    #
    # # #4) Chaos
    # # from subdomains_scrapping.chaos.chaos import scrap as chaosScrap
    # # choasResult = chaosScrap(domain)
    # # with open(f"{output_dir}/chaos.txt", "w") as file:
    # #     for subdomain in choasResult:
    # #         file.write(f"{subdomain}\n")
    #
    #
    # # #5) Shodan
    # # from subdomains_scrapping.shodan.shodan import scrap as shodanScrap
    # # shodanResult = shodanScrap(domain)
    # # with open(f"{output_dir}/shodan.txt", "w") as file:
    # #     for subdomain in shodanResult:
    # #         file.write(f"{subdomain}\n")
    #
    # #6) Urlscan
    # from subdomains_scrapping.urlScan.urlScan import scarp as urlScanScrap
    # urlScanResult = urlScanScrap(domain)
    # with open(f"{output_dir}/urlScan.txt", "w") as file:
    #     for subdomain in urlScanResult:
    #         file.write(f"{subdomain}\n")
    #
    # #7) certspotter
    # # from subdomains_scrapping.certspotter.certspotter import scrap as certspotterScrap
    # # certspotterResult = certspotterScrap(domain)
    # # with open(f"{output_dir}/certspotter.txt", "w") as file:
    # #     for subdomain in certspotterResult:
    # #         file.write(f"{subdomain}\n")
    #
    #
    # #8) bevigil
    # from subdomains_scrapping.bevigil.bevigil import scrap as bevigilScrap
    # bevigilResult = bevigilScrap(domain)
    # with open(f"{output_dir}/bevigil.txt", "w") as file:
    #     for subdomain in bevigilResult:
    #         file.write(f"{subdomain}\n")


    #9) dnsdumpster
    # from subdomains_scrapping.dnsDumpster.dnsDumpster import scrap as dnsDumpsterScrap
    # dnsDumpsterResult = dnsDumpsterScrap(domain)
    # if dnsDumpsterResult == {-1}:
    #     print("DNS Dumpster key expired.")
    # else:
    #     with open(f"{output_dir}/dnsDumpster.txt", "w") as file:
    #         for subdomain in dnsDumpsterResult:
    #             file.write(f"{subdomain}\n")

    #10) Umbrella
    # from subdomains_scrapping.umbrella.umbrella import scrap as umbrellaScrap
    # umbrellaResult = umbrellaScrap(domain)
    # if umbrellaResult == {-1}:
    #     print("Umbrella key expired.")
    # else:
    #     with open(f"{output_dir}/umbrella.txt", "w") as file:
    #         for subdomain in umbrellaResult:
    #             file.write(f"{subdomain}\n")

    # #11) Full Hunt
    # from subdomains_scrapping.fullHunt.fullHunt import scrap as fullHuntScrap
    # fullHuntResult = fullHuntScrap(domain)
    # if fullHuntResult == {-1}:
    #     print("Full Hunt key expired.")
    # else:
    #     with open(f"{output_dir}/fullHunt.txt", "w") as file:
    #         for subdomain in fullHuntResult:
    #             file.write(f"{subdomain}\n")

    #12) netlas
    # from subdomains_scrapping.netlas.netlas import scrap as netlasScrap
    # netlasResult = netlasScrap(domain)
    # if netlasResult == {-1}:
    #     print("Netlas key expired.")
    # else:
    #     with open(f"{output_dir}/netlas.txt", "w") as file:
    #         for subdomain in netlasResult:
    #             file.write(f"{subdomain}\n")

enum("jobs.ch")