import subprocess
import json
import argparse
from pathlib import Path
import socket
import os
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse




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
        "subfinder", "-d", domain, "-silent", "-o", str(subfinder_file)
    ]
    print("[+] Start: Subfinder")
    subfinderCMD = subprocess.run(subfinderCMD, capture_output=True, text=True)
    if subfinderCMD.returncode != 0:
        print("Subfinder failed:", subfinderCMD.stderr)

    print("[+] Finshed: Subfinder")


    purednsCMD = [
        "puredns", "resolve", str(subfinder_file),
        "-w", str(live_file),
        "-r", str(resolvers_file)
    ]
    print("[+] Start: ")
    purednsProcess = subprocess.run(purednsCMD, capture_output=True, text=True)
    if purednsProcess.returncode != 0:
        print("PureDNS failed:", purednsProcess.stderr)

    print("[+] Finished: Puredns")


    naabuCMD = [
        "naabu", "-list", str(live_file),"-silent",
        "-Pn",
        "-o", str(port_file)
    ]
    print("[+] Start:Naabue")
    naabuProcess = subprocess.run(naabuCMD, capture_output=True, text=True)
    if naabuProcess.returncode != 0:
        print("naabu failed:", naabuProcess.stderr)

    print("[+] Finished: Naabu")


    ports = set()
    with open(str(port_file), 'r') as portsFile:
        for line in portsFile:
            line = line.strip()
            host, port = line.split(':')
            ports.add(port)
    
    print("[+] Start: HTTPX")
    httpxCmd = ['httpx', '-l', str(live_file), '-silent','-nc','-fr' ,'-title', '-sc', '-location', '-p', f'{",".join(ports)}', '-o' ,str(httpx_file)]
    httpxProcess = subprocess.run(httpxCmd, capture_output=True, text=True)
    if httpxProcess.returncode != 0:
        print("httpx failed:", httpxProcess.stderr)

    print("[+] Finished: HTTPX")

    # Domain DataClass
    @dataclass
    class Subdomain:
        hostname: str = ""
        ports: set = field(default_factory=set) 
        targets: set = field(default_factory=set) 
        

    # Fetch alive subdomains
    subdomains = {}  
    with open(str(live_file), 'r') as f:
        for line in f:
            line = line.strip()
            sub = Subdomain()
            sub.hostname = line
            subdomains[line] = sub  

    # Parse the Ports
    with open(str(port_file), 'r') as f:
        for line in f:
            line = line.strip()
            host, port = line.split(":") 
            subdomains[host].ports.add(port)


    #Prase HTTPX
    with open(str(httpx_file), 'r') as f:
        for line in f:
            line = line.strip()
            host = line.split()[0]
            host = urlparse(host)
            host = host.netloc
            if ':' in host:
                host = host.split(':')[0]
            subdomains[host].targets.add(line)
    

    # Print results
    for sub in subdomains.values():
        print(f"{sub.hostname} {sub.ports} {sub.targets}")

    