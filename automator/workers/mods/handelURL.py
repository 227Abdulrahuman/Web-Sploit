import re
from urllib.parse import parse_qs, urlparse

#Takes a url and returns path and set of params.

def handelURL(url: str):
    parsed_url = urlparse(url)   
    path = re.sub(r'^(?:\./|\../)+', '/', parsed_url.path)
    path = re.sub(r'/+', '/', path)
    if not path.startswith('/'):
        path = '/' + path
    if not path.endswith('/'):
        path += '/'

    query_params = set(parse_qs(parsed_url.query, keep_blank_values=True).keys())
    return path, query_params


