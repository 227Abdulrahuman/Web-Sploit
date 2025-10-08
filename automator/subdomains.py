import subprocess
import json
import argparse
from pathlib import Path
import socket
import os



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Target domain")
    args = parser.parse_args()
    domain = args.domain

    os.makedirs(f'/workspace/results/{domain}', exist_ok=True)
    path = Path(f'/workspace/results/{domain}')
    resourcesPath = Path(f'/workspace/resources/')

    

    subfinder_file = path / "subfinder.txt"
    live_file = path / "live.txt"
    dns_file = path / "dns.txt"
    ips_file = path / "ips.txt"
    port_file = path / "ports.txt"
    httpx_file = path / "httpx.txt"
    results_file = path / "results.json"

    resolvers_file = resourcesPath / "resolvers.txt"

    final_file = path / "final.json"

    subfinderCMD = [
        "subfinder", "-d", domain, "-silent", "-all", "-o", str(subfinder_file)
    ]
    subfinderCMD = subprocess.run(subfinderCMD, capture_output=True, text=True)
    if subfinderCMD.returncode != 0:
        print("Subfinder failed:", subfinderCMD.stderr)

    print(f"[+] Subfinder")


    purednsCMD = [
        "puredns", "resolve", str(subfinder_file),
        "-w", str(live_file),
        "-r", str(resolvers_file)
    ]
    purednsProcess = subprocess.run(purednsCMD, capture_output=True, text=True)
    if purednsProcess.returncode != 0:
        print("PureDNS failed:", purednsProcess.stderr)

    print(f"[+] Puredns")



    naabuCMD = [
        "naabu", "-list", str(live_file),"-silent",
        "-Pn",
        "-o", str(port_file)
    ]
    naabuProcess = subprocess.run(naabuCMD, capture_output=True, text=True)
    if naabuProcess.returncode != 0:
        print("naabu failed:", naabuProcess.stderr)

    print(f"[+] naabu")


    ports = set()
    with open(str(port_file), 'r') as portsFile:
        for line in portsFile:
            line = line.strip()
            host, port = line.split(':')
            ports.add(port)
    
    httpxCmd = ['httpx', '-l', str(live_file), '-silent','-fr' ,'-title', '-sc', '-location', '-p', f'{",".join(ports)}', '-o' ,str(httpx_file)]
    httpxProcess = subprocess.run(httpxCmd, capture_output=True, text=True)
    if httpxProcess.returncode != 0:
        print("httpx failed:", httpxProcess.stderr)

    print("[+] httpx")