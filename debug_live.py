import re
import requests

WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; WC2026Predictor/1.0)"}

params = {
    "action": "parse",
    "page": "2026_FIFA_World_Cup_squads",
    "prop": "text",
    "format": "json",
    "formatversion": "2"
}

resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=30)
data = resp.json()
html = data["parse"]["text"]

print(f"Live HTML length: {len(html)}")

# Test the same heading pattern
heading_pattern = re.compile(r'<h([234])\s+id="([^"]*)"[^>]*>(.*?)</h\1>', re.DOTALL)
matches = list(heading_pattern.finditer(html))
print(f"Heading matches: {len(matches)}")
for m in matches[:10]:
    text = re.sub(r'<[^>]+>', '', m.group(3)).strip()
    print(f"  h{m.group(1)} id={m.group(2)!r}: {text!r}")
