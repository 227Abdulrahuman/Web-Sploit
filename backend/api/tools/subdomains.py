import subprocess
import json
import argparse
from pathlib import Path
import dns.resolver
import socket
import os
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse

def toJSON(obj):
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {k: toJSON(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [toJSON(i) for i in obj]
    return obj


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

       
def enumerateSubdomains(domain):

    #Creating Dirs
    os.makedirs(f'/work/backend/api/tools/results/{domain}', exist_ok=True)
    path = Path(f'/work/backend/api/tools/results/{domain}')
    resourcesPath = Path(f'/work/backend/api/tools/data')

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
    
    return json.dumps(toJSON(subdomains))

