import subprocess


def scrap(domain):
    cmd = ["haktrailsfree", "-d", domain, "-c", "/work/backend/api/tools/data/cookie.txt", "--silent"]
    proc = subprocess.run(cmd,text=True,capture_output=True)

    if "Cookie Expired" in proc.stdout or "Cookie Expired" in proc.stderr:
        return {-1}

    subdomains = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        subdomains.add(line)

    return subdomains