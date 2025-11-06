import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)



from subdomains_scrapping.certspotter.certspotter import scrap as scrap


for i in scrap("jobs.ch"):
    print(i)

