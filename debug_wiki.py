"""Debug: Check what the Wikipedia API actually returns for the squads page"""
import requests
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

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
print(f"Status: {resp.status_code}")
data = resp.json()

if "parse" in data:
    html = data["parse"]["text"]
    print(f"HTML length: {len(html)} chars")
    
    # Check for headings
    headings = re.findall(r'<h[234][^>]*>(.*?)</h[234]>', html, re.DOTALL)
    print(f"\nFirst 30 headings found:")
    for h in headings[:30]:
        clean = re.sub(r'<[^>]+>', '', h).strip()
        clean = re.sub(r'\[.*?\]', '', clean).strip()
        print(f"  '{clean}'")
    
    # Save first 5000 chars around "Mexico" or first nation
    mexico_idx = html.find('Mexico')
    if mexico_idx > -1:
        print(f"\n\n--- HTML around first 'Mexico' mention (chars {mexico_idx-200}:{mexico_idx+500}) ---")
        print(html[max(0,mexico_idx-200):mexico_idx+500])
    
    # Save the first 3000 chars
    print(f"\n\n--- First 3000 chars of HTML ---")
    print(html[:3000])
    
    # Save HTML to file for inspection
    with open('debug_wiki_html.txt', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nFull HTML saved to debug_wiki_html.txt")
else:
    print("No 'parse' key in response")
    print(list(data.keys()))
    if 'error' in data:
        print("Error:", data['error'])
