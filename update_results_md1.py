"""
Update results.csv with actual FIFA World Cup 2026 Matchday 1 results (Groups A-H)
and regenerate the predictor with the real match data incorporated.

The completed results will:
1. Replace NaN scores in results.csv with the actual scores
2. These flow into the training data (as very high-weight recent matches)
3. Team form is recalculated with actual WC performances included
"""

import csv
import pandas as pd
import os

# ─── Actual Matchday 1 results (Groups A-H) ─────────────────────────────────
# Format: (home_team, away_team, home_score, away_score, date, city, country, tournament)
# home/away as they appear in results.csv (checked against existing rows)

MD1_RESULTS = [
    # Group A — June 11
    ("Mexico",        "South Africa",          2, 0, "2026-06-11", "Mexico City",  "Mexico",        "FIFA World Cup"),
    ("South Korea",   "Czech Republic",         2, 1, "2026-06-11", "Zapopan",      "Mexico",        "FIFA World Cup"),
    # Group B — June 12, 13
    ("Canada",        "Bosnia and Herzegovina", 1, 1, "2026-06-12", "Toronto",      "Canada",        "FIFA World Cup"),
    ("Qatar",         "Switzerland",            1, 1, "2026-06-13", "Santa Clara",  "United States", "FIFA World Cup"),
    # Group C — June 13
    ("Brazil",        "Morocco",                1, 1, "2026-06-13", "East Rutherford", "United States", "FIFA World Cup"),
    ("Haiti",         "Scotland",               0, 1, "2026-06-13", "Foxborough",   "United States", "FIFA World Cup"),
    # Group D — June 12, 13
    ("United States", "Paraguay",               4, 1, "2026-06-12", "Inglewood",    "United States", "FIFA World Cup"),
    ("Australia",     "Turkey",                 2, 0, "2026-06-13", "Vancouver",    "Canada",        "FIFA World Cup"),
    # Group E — June 14
    ("Germany",       "Curacao",                7, 1, "2026-06-14", "Houston",      "United States", "FIFA World Cup"),
    ("Ivory Coast",   "Ecuador",                1, 0, "2026-06-14", "Philadelphia", "United States", "FIFA World Cup"),
    # Group F — June 14
    ("Netherlands",   "Japan",                  2, 2, "2026-06-14", "Arlington",    "United States", "FIFA World Cup"),
    ("Sweden",        "Tunisia",                5, 1, "2026-06-14", "Guadalupe",    "Mexico",        "FIFA World Cup"),
    # Group G — June 15
    ("Belgium",       "Egypt",                  1, 1, "2026-06-15", "Seattle",      "United States", "FIFA World Cup"),
    ("Iran",          "New Zealand",            2, 2, "2026-06-15", "Inglewood",    "United States", "FIFA World Cup"),
    # Group H — June 15
    ("Spain",         "Cape Verde",             0, 0, "2026-06-15", "Atlanta",      "United States", "FIFA World Cup"),
    ("Saudi Arabia",  "Uruguay",                1, 1, "2026-06-15", "Miami Gardens","United States", "FIFA World Cup"),
]

def main():
    print("=" * 65)
    print("Updating results.csv with FIFA WC 2026 Matchday 1 results")
    print("=" * 65)

    df = pd.read_csv('results.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Make score columns numeric
    df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
    df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')

    TEAM_ALIASES = {
        'USA': 'United States',
        'Korea Republic': 'South Korea',
        'Curaçao': 'Curacao',
        'Türkiye': 'Turkey',
        'Côte d\'Ivoire': 'Ivory Coast',
    }

    def clean(name):
        return TEAM_ALIASES.get(name, name)

    updated = 0
    added = 0

    for (home, away, hs, as_, date_str, city, country, tournament) in MD1_RESULTS:
        match_date = pd.to_datetime(date_str)
        
        # Find existing row — match by teams (either home/away order) and date
        mask = (
            (df['date'] == match_date) &
            (
                (df['home_team'].apply(clean) == clean(home)) &
                (df['away_team'].apply(clean) == clean(away))
            )
        )
        alt_mask = (
            (df['date'] == match_date) &
            (
                (df['home_team'].apply(clean) == clean(away)) &
                (df['away_team'].apply(clean) == clean(home))
            )
        )

        if df[mask].shape[0] > 0:
            # Update existing row
            if pd.isna(df.loc[mask, 'home_score'].values[0]):
                df.loc[mask, 'home_score'] = hs
                df.loc[mask, 'away_score'] = as_
                print(f"  UPDATED: {home} {hs}-{as_} {away}  ({date_str})")
                updated += 1
            else:
                existing_hs = df.loc[mask, 'home_score'].values[0]
                existing_as = df.loc[mask, 'away_score'].values[0]
                print(f"  SKIP (already has score {existing_hs}-{existing_as}): {home} vs {away}")
        elif df[alt_mask].shape[0] > 0:
            # Reversed teams in CSV — update with swapped scores
            if pd.isna(df.loc[alt_mask, 'home_score'].values[0]):
                df.loc[alt_mask, 'home_score'] = as_  # away team is "home" in CSV
                df.loc[alt_mask, 'away_score'] = hs
                print(f"  UPDATED (reversed): {away} {as_}-{hs} {home}  ({date_str})")
                updated += 1
            else:
                print(f"  SKIP (reversed, already scored): {home} vs {away}")
        else:
            # Row doesn't exist — append a new one
            new_row = {
                'date': date_str,
                'home_team': home,
                'away_team': away,
                'home_score': hs,
                'away_score': as_,
                'tournament': tournament,
                'city': city,
                'country': country,
                'neutral': True
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(f"  ADDED: {home} {hs}-{as_} {away}  ({date_str})")
            added += 1

    print(f"\nSummary: {updated} rows updated, {added} rows added")

    # Save
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    df.to_csv('results.csv', index=False)
    print("Saved results.csv")

    # Print verification — 2026 WC rows with scores
    df2 = pd.read_csv('results.csv')
    wc26_scored = df2[
        (df2['date'].str.startswith('2026')) &
        (df2['tournament'] == 'FIFA World Cup') &
        (~df2['home_score'].isna()) &
        (df2['home_score'].astype(str) != 'nan')
    ]
    print(f"\n2026 WC matches with scores: {len(wc26_scored)}")
    for _, r in wc26_scored.iterrows():
        print(f"  {r['date']}  {r['home_team']} {int(r['home_score'])}-{int(r['away_score'])} {r['away_team']}")

    print("\n✓ results.csv updated. Re-run predict_world_cup.py to get updated predictions.")

if __name__ == "__main__":
    main()
