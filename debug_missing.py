import re
import csv

# All nations found in Wikipedia headings
WIKI_NATIONS = [
    'Czech Republic', 'Mexico', 'South Africa', 'South Korea',
    'Bosnia and Herzegovina', 'Canada', 'Qatar', 'Switzerland',
    'Brazil', 'Haiti', 'Morocco', 'Scotland',
    'Australia', 'Paraguay', 'Turkey', 'United States',
    'Curacao', 'Ecuador', 'Germany', 'Ivory Coast',
    'Japan', 'Netherlands', 'Sweden', 'Tunisia',
    'Belgium', 'Egypt', 'Iran', 'New Zealand',
    'Cape Verde', 'Saudi Arabia', 'Spain', 'Uruguay',
    'France', 'Iraq', 'Norway', 'Senegal',
    'Algeria', 'Argentina', 'Austria', 'Jordan',
    'Colombia', 'DR Congo', 'Portugal', 'Uzbekistan',
    'Croatia', 'England', 'Ghana', 'Panama',
    'Jamaica', 'Venezuela',  # from EA FC data
]

# Check wc2026_squads.csv
with open('wc2026_squads.csv', newline='', encoding='utf-8') as f:
    wc = list(csv.DictReader(f))

wc_nations = set(r['Nation'] for r in wc)
print(f'Nations in wc2026_squads.csv: {len(wc_nations)}')
print(sorted(wc_nations))

missing = [n for n in WIKI_NATIONS if n not in wc_nations]
print(f'\nMissing from wc2026_squads.csv: {missing}')
