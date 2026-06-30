import pyfifa
import json
import urllib.request

url = "https://inside.fifa.com/api/ranking-overview?locale=en&dateId=FRS_Male_Football_20260119"
print(f"Fetching {url}")
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())

print("Keys in JSON data:", data.keys())
if "rankings" in data:
    print("Number of items in 'rankings':", len(data["rankings"]))
    if len(data["rankings"]) > 0:
        print("First item sample:", json.dumps(data["rankings"][0], indent=2))
else:
    # Print the first level keys and some sample
    print(json.dumps(data, indent=2)[:1000])
