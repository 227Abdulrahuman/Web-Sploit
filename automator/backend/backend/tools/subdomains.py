import subprocess
import json
import argparse
from pathlib import Path
import dns.resolver
import socket
import os
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse

#TODO: Sort Subfinder, Eyewtniss, Ext DNS Records.

#Helper Functions
def getCnames(domain):
    """
    Takes a domain and resturns a list of cnames.
    """
    cname_chain = []
    current_domain = domain
    max_iterations = 10  
    
    for _ in range(max_iterations):
        try:
            answers = dns.resolver.resolve(current_domain, 'CNAME')
            
            cname_target = str(answers[0].target).rstrip('.')
            cname_chain.append(cname_target)
            
            current_domain = cname_target
            
        except dns.resolver.NoAnswer:
            break
        except dns.resolver.NXDOMAIN:
            break
        except Exception as e:
            print(f"Error resolving {current_domain}: {e}")
            break
    
    return cname_chain

def getIP(domain):
    """
    Takes a domain and retuns the IP.
    """
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None



if __name__ == "__main__":
    #Data Type
    @dataclass
    class Subdomain:
        hostname: str = ""
        ip: str = ""
        ports: set = field(default_factory=set) 
        cnames: list = field(default_factory=list)

    #Parsing Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Target domain")
    args = parser.parse_args()
    domain = args.domain

    #Creating Dirs
    os.makedirs(f'/workspace/results/{domain}', exist_ok=True)
    path = Path(f'/workspace/results/{domain}')
    resourcesPath = Path(f'/workspace/resources/')

    
    #Creating files
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
    subfinderProcess = subprocess.run(subfinderCMD, capture_output=True, text=True)
    if subfinderProcess.returncode != 0:
        print("Subfinder failed:", subfinderProcess.stderr)

    print("[+] Finshed: Subfinder")


    purednsCMD = [
        "puredns", "resolve", str(subfinder_file),
        "-w", str(live_file),
        "-r", str(resolvers_file)
    ]
    print("[+] Start: Puredns ")
    purednsProcess = subprocess.run(purednsCMD, capture_output=True, text=True)
    if purednsProcess.returncode != 0:
        print("PureDNS failed:", purednsProcess.stderr)

    print("[+] Finished: Puredns")

    # Fetch alive subdomains
    subdomains = {}  
    with open(str(live_file), 'r') as f:
        for line in f:
            line = line.strip()
            sub = Subdomain()
            sub.hostname = line
            subdomains[line] = sub  

    #Get IPs
    for sub in subdomains.values():
        sub.ip = getIP(sub.hostname)

    # Get Cnames
    for sub in subdomains.values():
        sub.cnames = getCnames(sub.hostname)

    #Put the IPs in a file
    with open(str(ips_file), 'w') as f:
        for sub in subdomains.values():
            f.write(f"{sub.ip}\n")

    naabuCMD = [
        "naabu", "-list", str(ips_file),"-silent",
        "-Pn",
        "-o", str(port_file)
    ]
    print("[+] Start:naabu")
    naabuProcess = subprocess.run(naabuCMD, capture_output=True, text=True)
    if naabuProcess.returncode != 0:
        print("naabu failed:", naabuProcess.stderr)

    #Taking Screeenshoots.

    print("[+] Finished: naabu")

    
        

    

    #Parse the Ports
    with open(str(port_file), 'r') as f:
        for line in f:
            line = line.strip()
            if ":" not in line:
                continue
            ip, port = line.split(":")
            for sub in subdomains.values():
                if sub.ip == ip:
                    sub.ports.add(port)



    # Print results
    for sub in subdomains.values():
        print(sub)
       
def enumerateSubdomains(domain):


    #Creating Dirs
    os.makedirs(f'/workspace/results/{domain}', exist_ok=True)
    path = Path(f'/workspace/results/{domain}')
    resourcesPath = Path(f'/workspace/resources/')

    #Creating files
    subfinder_file = path / "subfinder.txt"
    live_file = path / "live.txt"
    port_file = path / "ports.txt"

    resolvers_file = resourcesPath / "resolvers.txt"



    subfinderCMD = [
        "subfinder", "-d", domain, "-o", str(subfinder_file)
    ]
    subprocess.run(subfinderCMD, capture_output=True, text=True)

    tmp = set()
    with open(str(subfinder_file), 'r') as f:
        for line in f:
            line  = line.strip()
            tmp.add(line)

    with open(str(subfinder_file), 'w') as f:
        for domain in tmp:
            f.write(f"{domain}\n") 

    purednsCMD = [
            "puredns", "resolve", str(subfinder_file),
            "-w", str(live_file),
            "-r", str(resolvers_file)
        ]
    subprocess.run(purednsCMD, capture_output=True, text=True)

    naabuCMD = [
        "naabu", "-list", str(live_file),"-silent","-ec",
        "-Pn",
        "-o", str(port_file)
    ]
    subprocess.run(naabuCMD, capture_output=True, text=True)


    subdomains = list()
    #Parse domains.
    with open(str(live_file), 'r') as f:
        for line in f:
            line = line.strip()
            sub = {}
            sub["hostname"] = line
            subdomains.append(sub)
    
   # Parse Ports
    with open(str(port_file), 'r') as f:
        port_lines = [line.strip() for line in f if line.strip()]

    for sub in subdomains:
        sub["ports"] = set()
        for line in port_lines:
            host, port = line.split(':')
            if sub["hostname"] == host:
                sub["ports"].add(port)

                    

    #Get IP
    for sub in subdomains:
        sub["ip"] = getIP(sub["hostname"])
        sub["cnames"] = getCnames(sub["hostname"])
    
    return subdomains
                
    
