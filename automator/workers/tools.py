import subprocess
import os


def katana(target, key):
    output_path = f'../results/{key}/katana.txt'
    cmd = ['katana', '-u', target, '-silent', '-o', output_path]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def runTools(website, domain, key):
    os.makedirs(f'../results/{key}', exist_ok=True)
    katana(website, key)


runTools("https://www.jobscout24.ch", "jobscout24.ch", "jobscout")
