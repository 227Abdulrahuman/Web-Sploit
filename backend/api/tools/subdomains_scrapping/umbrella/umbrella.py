import yaml, requests, json, time

with open('/work/backend/.config/provider.yaml') as file:
    data = yaml.safe_load(file)
data = data["Umbrella"]
key = data["apiKey"]


#Replace the keys with JWT token.
def fetchJWT(key=key):
    url = "https://api.umbrella.com/auth/v2/token"
    auth = ("9cb92ce00c03427a8c84bec592a60220", "7d4d8b2146de4589882c8faf19fed0f1")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(url, auth=auth, headers=headers, data=body)
        return response.json()['access_token']
    except Exception:
        return ""

def scrap(domain):
    subdomains = set()
    retryCounter = 0
    token = fetchJWT(key)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"https://api.umbrella.com/investigate/v2/subdomains/{domain}"
    offset_name = None

    while True:
        params = {"limit": 100}
        if offset_name:
            params["offsetName"] = offset_name

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            retryCounter += 1
            time.sleep(3)

            if retryCounter > 3:
                break

        elif 400 <= response.status_code < 500:
            return {-1}

        else:
            data = response.json()

            if not data:
                break

            subs = [item["name"] for item in data if "name" in item]

            subdomains.update(subs)

            offset_name = data[-1]["name"]
    return subdomains