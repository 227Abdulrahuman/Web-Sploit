import dns.resolver
import argparse
import sys

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



potentialVulnerableSubs = [
    "azurewebsites.net",
    "elasticbeanstalk.com",
    "s3.amazonaws.com",
    "airee.ru",
    "animaapp.io",
    "bitbucket.io",
    "trydiscourse.com",
    "hatenablog.com",
    "helpjuice.com",
    "helpscoutdocs.com",
    "helprace.com",
    "cloudapp.net",
    "cloudapp.azure.com",
    "blob.core.windows.net,"
    "cloudapp.azure.com",
    "azure-api.net",
    "azurehdinsight.net",
    "azureedge.net",
    "azurecontainer.io",
    "database.windows.net",
    "azuredatalakestore.net",
    "search.windows.net",
    "azurecr.io",
    "redis.cache.windows.net",
    "azurehdinsight.net",
    "servicebus.windows.net",
    "visualstudio.com",
    "s.strikinglydns.com",
    "na-west1.surge.sh",
    "surveysparrow.com",
    "read.uberflip.com",
    "wordpress.com",
    "worksites.net"
    ]

def maybeVulnerable(domain):
    cnames = getCnames(domain)
    
    for cname in cnames:
        for sub in potentialVulnerableSubs:
            if sub in cname:
                return cnames


parser = argparse.ArgumentParser(description="Implementing can I takeover XYZ?")
parser.add_argument("target", nargs='?', help="Target URL or domain (e.g. example.com)")
parser.add_argument("-l", "--list", dest="file", help="File containing domains, one per line")
parser.add_argument("-o", "--output", help="Output file", default="subzy.txt")

args = parser.parse_args()

if (args.target is None) and (args.file is None):
    parser.error("You must provide either a target domain or -l/--list with a file.")
if (args.target is not None) and (args.file is not None):
    parser.error("Provide only one: either a target domain OR -l/--list, not both.")


if args.target:
    if maybeVulnerable(args.target):
        print(maybeVulnerable(args.target))

else:
    with open(args.file,'r') as f:
        for line in f:
            sub = line.strip()
            if (maybeVulnerable(sub)):
                print(f"{sub}: {maybeVulnerable(sub)}")

