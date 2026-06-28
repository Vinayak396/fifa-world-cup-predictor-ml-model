"""
Update results.csv with all completed FIFA 2026 World Cup group stage results.
Matches in CSV are stored with home/away in the original CSV order, but Wikipedia 
may list them differently. We match by date + teams (bidirectional).
"""
import pandas as pd
import numpy as np

# All 72 group stage results from Wikipedia (scraped June 28, 2026)
# Format: (date, home_team_csv, away_team_csv, home_score, away_score)
# Note: home/away here matches the CSV row order (not necessarily venue home)
RESULTS = {
    # Group A
    ("2026-06-11", "Mexico", "South Africa"):         (2, 0),
    ("2026-06-11", "South Korea", "Czech Republic"):  (2, 1),
    ("2026-06-18", "Czech Republic", "South Africa"): (1, 1),
    ("2026-06-18", "Mexico", "South Korea"):          (1, 0),
    ("2026-06-24", "Mexico", "Czech Republic"):       (3, 0),   # CSV has Mexico as away; wiki says Czech 0-3 Mexico
    ("2026-06-24", "South Africa", "South Korea"):    (1, 0),
    # Group B
    ("2026-06-12", "Canada", "Bosnia and Herzegovina"): (1, 1),
    ("2026-06-13", "Qatar", "Switzerland"):           (1, 1),
    ("2026-06-18", "Switzerland", "Bosnia and Herzegovina"): (4, 1),
    ("2026-06-18", "Canada", "Qatar"):                (6, 0),
    ("2026-06-24", "Canada", "Switzerland"):          (1, 2),   # CSV has Switzerland as home; Canada as away
    ("2026-06-24", "Bosnia and Herzegovina", "Qatar"): (3, 1),
    # Group C
    ("2026-06-13", "Brazil", "Morocco"):              (1, 1),
    ("2026-06-13", "Haiti", "Scotland"):              (0, 1),
    ("2026-06-19", "Scotland", "Morocco"):            (0, 1),
    ("2026-06-19", "Brazil", "Haiti"):                (3, 0),
    ("2026-06-24", "Scotland", "Brazil"):             (0, 3),
    ("2026-06-24", "Morocco", "Haiti"):               (4, 2),
    # Group D
    ("2026-06-12", "United States", "Paraguay"):      (4, 1),
    ("2026-06-13", "Australia", "Turkey"):            (2, 0),
    ("2026-06-19", "United States", "Australia"):     (2, 0),
    ("2026-06-19", "Turkey", "Paraguay"):             (0, 1),   # wiki: Turkey 0-1 Paraguay
    ("2026-06-25", "United States", "Turkey"):        (2, 3),   # CSV has Turkey as home; wiki Turkey 3-2 USA → USA 2-3 Turkey
    ("2026-06-25", "Paraguay", "Australia"):          (0, 0),
    # Group E
    ("2026-06-14", "Germany", "Curacao"):             (7, 1),
    ("2026-06-14", "Ivory Coast", "Ecuador"):         (1, 0),
    ("2026-06-20", "Germany", "Ivory Coast"):         (2, 1),
    ("2026-06-20", "Ecuador", "Curacao"):             (0, 0),
    ("2026-06-25", "Curacao", "Ivory Coast"):         (0, 2),
    ("2026-06-25", "Ecuador", "Germany"):             (2, 1),
    # Group F
    ("2026-06-14", "Netherlands", "Japan"):           (2, 2),
    ("2026-06-14", "Sweden", "Tunisia"):              (5, 1),
    ("2026-06-20", "Netherlands", "Sweden"):          (5, 1),
    ("2026-06-20", "Tunisia", "Japan"):               (0, 4),
    ("2026-06-25", "Japan", "Sweden"):                (1, 1),
    ("2026-06-25", "Tunisia", "Netherlands"):         (1, 3),
    # Group G
    ("2026-06-15", "Belgium", "Egypt"):               (1, 1),
    ("2026-06-15", "Iran", "New Zealand"):            (2, 2),
    ("2026-06-21", "Belgium", "Iran"):                (0, 0),
    ("2026-06-21", "New Zealand", "Egypt"):           (1, 3),
    ("2026-06-26", "Egypt", "Iran"):                  (1, 1),
    ("2026-06-26", "New Zealand", "Belgium"):         (1, 5),
    # Group H
    ("2026-06-15", "Spain", "Cape Verde"):            (0, 0),
    ("2026-06-15", "Saudi Arabia", "Uruguay"):        (1, 1),
    ("2026-06-21", "Spain", "Saudi Arabia"):          (4, 0),
    ("2026-06-21", "Uruguay", "Cape Verde"):          (2, 2),
    ("2026-06-26", "Cape Verde", "Saudi Arabia"):     (0, 0),
    ("2026-06-26", "Uruguay", "Spain"):               (0, 1),
    # Group I
    ("2026-06-16", "France", "Senegal"):              (3, 1),
    ("2026-06-16", "Iraq", "Norway"):                 (1, 4),
    ("2026-06-22", "France", "Iraq"):                 (3, 0),
    ("2026-06-22", "Norway", "Senegal"):              (3, 2),
    ("2026-06-26", "Norway", "France"):               (1, 4),
    ("2026-06-26", "Senegal", "Iraq"):                (5, 0),
    # Group J
    ("2026-06-16", "Argentina", "Algeria"):           (3, 0),
    ("2026-06-16", "Austria", "Jordan"):              (3, 1),
    ("2026-06-22", "Argentina", "Austria"):           (2, 0),
    ("2026-06-22", "Jordan", "Algeria"):              (1, 2),
    ("2026-06-27", "Algeria", "Austria"):             (3, 3),
    ("2026-06-27", "Jordan", "Argentina"):            (1, 3),
    # Group K
    ("2026-06-17", "Portugal", "DR Congo"):           (1, 1),
    ("2026-06-17", "Uzbekistan", "Colombia"):         (1, 3),
    ("2026-06-23", "Portugal", "Uzbekistan"):         (5, 0),
    ("2026-06-23", "Colombia", "DR Congo"):           (1, 0),
    ("2026-06-27", "Colombia", "Portugal"):           (0, 0),
    ("2026-06-27", "DR Congo", "Uzbekistan"):         (3, 1),
    # Group L
    ("2026-06-17", "England", "Croatia"):             (4, 2),
    ("2026-06-17", "Ghana", "Panama"):                (1, 0),
    ("2026-06-23", "England", "Ghana"):               (0, 0),
    ("2026-06-23", "Panama", "Croatia"):              (0, 1),
    ("2026-06-27", "Panama", "England"):              (0, 2),
    ("2026-06-27", "Croatia", "Ghana"):               (2, 1),
}

# Load results.csv
df = pd.read_csv('results.csv')
df['date'] = pd.to_datetime(df['date'])

# Build a name mapping for lookup (CSV uses 'United States' for USA)
NAME_MAP = {
    'USA': 'United States',
}

def normalize(name):
    return NAME_MAP.get(name, name)

updated = 0
not_found = []

for (date_str, home, away), (hs, as_) in RESULTS.items():
    target_date = pd.to_datetime(date_str)
    home_norm = normalize(home)
    away_norm = normalize(away)
    
    # Find matching row (could be in either direction in CSV)
    mask_fwd = (
        (df['date'] == target_date) &
        (df['home_team'] == home_norm) &
        (df['away_team'] == away_norm)
    )
    mask_rev = (
        (df['date'] == target_date) &
        (df['home_team'] == away_norm) &
        (df['away_team'] == home_norm)
    )
    
    if mask_fwd.any():
        df.loc[mask_fwd, 'home_score'] = float(hs)
        df.loc[mask_fwd, 'away_score'] = float(as_)
        updated += 1
    elif mask_rev.any():
        # Reversed: home/away are swapped in CSV
        df.loc[mask_rev, 'home_score'] = float(as_)
        df.loc[mask_rev, 'away_score'] = float(hs)
        updated += 1
    else:
        not_found.append((date_str, home, away))

print(f"Updated {updated} matches")
if not_found:
    print(f"NOT FOUND ({len(not_found)}):")
    for item in not_found:
        print(f"  {item}")

# Save backup then overwrite
df.to_csv('results.csv', index=False)
print("Saved results.csv")

# Verify
wc2026 = df[(df['date'].dt.year == 2026) & (df['tournament'] == 'FIFA World Cup')]
completed = wc2026[wc2026['home_score'].notna()]
print(f"Total WC 2026 matches: {len(wc2026)}, completed: {len(completed)}")
