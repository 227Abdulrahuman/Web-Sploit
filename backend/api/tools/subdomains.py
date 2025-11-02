import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from subdomains_scrapping.virusTotal.virusTotal import scrap as VTScrap

# x = VTScrap("jobs.ch")
# print(len(x))

from subdomains_scrapping.anubis.anubis import scrap as anubisScrap
for i in anubisScrap("jobup.ch"):
    print(i)