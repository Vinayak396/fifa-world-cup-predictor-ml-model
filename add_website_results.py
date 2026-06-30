import re
import json

original_winner_probs = {
    "England": 9.32, "France": 9.02, "Argentina": 8.04, "Spain": 7.24, "Morocco": 6.56,
    "Brazil": 5.73, "Portugal": 4.12, "Germany": 4.05, "Belgium": 3.48, "Uruguay": 3.46,
    "Ecuador": 3.22, "Netherlands": 3.11, "Colombia": 3.01, "Japan": 2.61, "USA": 2.58,
    "Mexico": 2.33, "Croatia": 2.29, "Switzerland": 2.00, "South Korea": 1.50, "Senegal": 1.34,
    "Turkey": 1.12, "Algeria": 1.10, "Egypt": 1.07, "Canada": 0.99, "Austria": 0.77,
    "Iran": 0.76, "Uzbekistan": 0.75, "Tunisia": 0.71, "Czech Republic": 0.67, "Australia": 0.64,
    "Scotland": 0.63, "DR Congo": 0.62, "Paraguay": 0.58, "Norway": 0.57, "Ivory Coast": 0.49,
    "Iraq": 0.49, "South Africa": 0.48, "Sweden": 0.43, "Panama": 0.41, "Cape Verde": 0.37,
    "Jordan": 0.32, "Bosnia and Herzegovina": 0.29, "Ghana": 0.19, "Saudi Arabia": 0.15,
    "Curacao": 0.13, "Qatar": 0.13, "New Zealand": 0.08, "Haiti": 0.05
}

MD1_RESULTS = [
    # Group A — June 11
    ("Mexico",        "South Africa",          2, 0),
    ("South Korea",   "Czech Republic",         2, 1),
    # Group B — June 12, 13
    ("Canada",        "Bosnia and Herzegovina", 1, 1),
    ("Qatar",         "Switzerland",            1, 1),
    # Group C — June 13
    ("Brazil",        "Morocco",                1, 1),
    ("Haiti",         "Scotland",               0, 1),
    # Group D — June 12, 13
    ("USA",           "Paraguay",               4, 1),
    ("Australia",     "Turkey",                 2, 0),
    # Group E — June 14
    ("Germany",       "Curacao",                7, 1),
    ("Ivory Coast",   "Ecuador",                1, 0),
    # Group F — June 14
    ("Netherlands",   "Japan",                  2, 2),
    ("Sweden",        "Tunisia",                5, 1),
    # Group G — June 15
    ("Belgium",       "Egypt",                  1, 1),
    ("Iran",          "New Zealand",            2, 2),
    # Group H — June 15
    ("Spain",         "Cape Verde",             0, 0),
    ("Saudi Arabia",  "Uruguay",                1, 1),
]

def get_probs(home, away):
    wH = original_winner_probs.get(home, 0.1)
    wA = original_winner_probs.get(away, 0.1)
    total = wH + wA
    rawH = wH / total
    balance = 1 - abs(rawH - 0.5) * 2
    drawPct = 0.27 * (0.5 + 0.5 * balance)
    winH = rawH * (1 - drawPct)
    winA = (1 - rawH) * (1 - drawPct)
    return {
        'home': round(winH * 100, 1),
        'draw': round(drawPct * 100, 1),
        'away': round(winA * 100, 1)
    }

def main():
    print("Parsing website/js/data.js...")
    with open('website/js/data.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We will build a lookup of (home, away) for MD1 results
    results_lookup = {}
    for home, away, hs, as_ in MD1_RESULTS:
        results_lookup[(home, away)] = (hs, as_)
        results_lookup[(away, home)] = (as_, hs) # support reverse ordering if needed

    new_lines = []
    fixture_pattern = re.compile(r'\{\s*id:\s*(\d+),\s*md:\s*(\d+),\s*date:\s*"([^"]+)",\s*home:\s*"([^"]+)",\s*away:\s*"([^"]+)",\s*group:\s*"([^"]+)",\s*venue:\s*"([^"]+)"\s*\}')

    updated_count = 0

    for line in lines:
        match = fixture_pattern.search(line)
        if match:
            fid = int(match.group(1))
            md = int(match.group(2))
            date = match.group(3)
            home = match.group(4)
            away = match.group(5)
            group = match.group(6)
            venue = match.group(7)

            key = (home, away)
            if key in results_lookup:
                hs, as_ = results_lookup[key]
                probs = get_probs(home, away)
                
                # Format to a new JSON-like line with result and preMatchProbs
                new_line = f'  {{ id:{fid},  md:{md}, date:"{date}", home:"{home}", away:"{away}", group:"{group}", venue:"{venue}", result: {{ homeScore:{hs}, awayScore:{as_} }}, preMatchProbs: {{ home:{probs["home"]}, draw:{probs["draw"]}, away:{probs["away"]} }} }},\n'
                new_lines.append(new_line)
                updated_count += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open('website/js/data.js', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"Successfully added results and pre-match probabilities for {updated_count} matches in website/js/data.js")

if __name__ == '__main__':
    main()
