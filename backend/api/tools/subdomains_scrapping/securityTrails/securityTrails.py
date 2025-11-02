import yaml

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
    

data = data['SecurityTrails']
print(data['apiKey'])


def scrap(domain):
    
    pass #return set()