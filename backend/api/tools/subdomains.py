import sys
import os

# Add the tools directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now you can import
from subdomains_scrapping.virusTotal.virusTotal import scrap as VTScrap

x = VTScrap("jobs.ch")
print(len(x))