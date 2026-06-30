import csv
from difflib import SequenceMatcher
import re

def normalise(name):
    replacements = {
        '\u00e1': 'a', '\u00e0': 'a', '\u00e3': 'a', '\u00e2': 'a', '\u00e4': 'a',
        '\u00e9': 'e', '\u00e8': 'e', '\u00ea': 'e', '\u00eb': 'e',
        '\u00ed': 'i', '\u00ec': 'i', '\u00ee': 'i', '\u00ef': 'i',
        '\u00f3': 'o', '\u00f2': 'o', '\u00f4': 'o', '\u00f6': 'o',
        '\u00fa': 'u', '\u00f9': 'u', '\u00fb': 'u', '\u00fc': 'u',
        '\u00f1': 'n', '\u00e7': 'c',
    }
    n = name.lower()
    for k, v in replacements.items():
        n = n.replace(k, v)
    n = re.sub(r"[^a-z\s'-]", '', n)
    return re.sub(r'\s+', ' ', n).strip()

with open('wc2026_squads.csv', newline='', encoding='utf-8') as f:
    wc = list(csv.DictReader(f))
print(f'Total WC players: {len(wc)}')

with open('eafc26_wc_squad_ratings.csv', newline='', encoding='utf-8') as f:
    eafc = [r for r in csv.DictReader(f) if int(r['Penalties']) > 0]

# Check Spain
spain_wc = [r for r in wc if r['Nation'] == 'Spain']
spain_eafc = [r for r in eafc if r['Nation'] == 'Spain']
print(f'\nSpain WC ({len(spain_wc)}):')
for p in spain_wc[:8]:
    print(f'  WC: {p["PlayerName"]!r}  -> norm: {normalise(p["PlayerName"])!r}')

print(f'\nSpain EA FC ({len(spain_eafc)}):')
for p in spain_eafc[:8]:
    print(f'  EA: {p["Name"]!r}  -> norm: {normalise(p["Name"])!r}')

# Try matching Lamine Yamal
for wname in ['Lamine Yamal', 'Pedri', 'Dani Olmo']:
    for ep in spain_eafc:
        score = SequenceMatcher(None, normalise(wname), normalise(ep['Name'])).ratio()
        if score > 0.7:
            print(f'\n{wname!r} matches {ep["Name"]!r} with score {score:.2f}')
