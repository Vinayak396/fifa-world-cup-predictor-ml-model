"""
Update results.csv and shootouts.csv with the 4 completed Round of 32 matches.

Results:
  Match 73: Canada 1-0 South Africa     (Jun 28, SoFi Stadium, Inglewood)
  Match 74: Germany 1-1 Paraguay (aet)   Paraguay win 4-3 on pens (Jun 29, Gillette Stadium, Foxborough)
  Match 75: Netherlands 1-1 Morocco (aet) Morocco win 3-2 on pens  (Jun 29, Estadio BBVA, Guadalupe)
  Match 76: Brazil 2-1 Japan             (Jun 29, NRG Stadium, Houston)
"""

import csv
import os

CWD = os.path.dirname(os.path.abspath(__file__))

# ── 1. ADD TO results.csv ────────────────────────────────────────────────────
new_results = [
    # date, home_team, away_team, home_score, away_score, tournament, city, country, neutral
    # Match 73: Canada 1-0 South Africa
    ["2026-06-28", "Canada", "South Africa", "1.0", "0.0", "FIFA World Cup", "Inglewood", "United States", "True"],
    # Match 74: Germany 1-1 Paraguay (Paraguay win on pens - score is full-time + ET)
    ["2026-06-29", "Germany", "Paraguay", "1.0", "1.0", "FIFA World Cup", "Foxborough", "United States", "True"],
    # Match 75: Netherlands 1-1 Morocco (Morocco win on pens - score is full-time + ET)
    ["2026-06-29", "Netherlands", "Morocco", "1.0", "1.0", "FIFA World Cup", "Guadalupe", "Mexico", "True"],
    # Match 76: Brazil 2-1 Japan
    ["2026-06-29", "Brazil", "Japan", "2.0", "1.0", "FIFA World Cup", "Houston", "United States", "True"],
]

results_path = os.path.join(CWD, "results.csv")

# Check if already added (avoid duplicates)
with open(results_path, 'r', encoding='utf-8') as f:
    content = f.read()

already_added = "2026-06-28" in content and "Canada" in content and "South Africa" in content

if already_added:
    # Check more specifically
    already_added = "2026-06-28,Canada,South Africa" in content

if not already_added:
    with open(results_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in new_results:
            writer.writerow(row)
    print(f"[OK] Added {len(new_results)} R32 results to results.csv")
else:
    print("[SKIP] R32 results already present in results.csv - skipping")

# ── 2. ADD TO shootouts.csv ──────────────────────────────────────────────────
# Format: date,home_team,away_team,winner,first_shooter
new_shootouts = [
    # Match 74: Paraguay beat Germany 4-3 on penalties
    ["2026-06-29", "Germany", "Paraguay", "Paraguay", "Germany"],
    # Match 75: Morocco beat Netherlands 3-2 on penalties
    ["2026-06-29", "Netherlands", "Morocco", "Morocco", "Netherlands"],
]

shootouts_path = os.path.join(CWD, "shootouts.csv")

with open(shootouts_path, 'r', encoding='utf-8') as f:
    shootouts_content = f.read()

already_added_s = "2026-06-29,Germany,Paraguay" in shootouts_content

if not already_added_s:
    with open(shootouts_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in new_shootouts:
            writer.writerow(row)
    print(f"[OK] Added {len(new_shootouts)} penalty shootout results to shootouts.csv")
else:
    print("[SKIP] Shootout results already present in shootouts.csv - skipping")

print("\n[DONE] Data update complete! Now run predict_world_cup.py to retrain the model.")
