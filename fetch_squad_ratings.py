"""
EA FC 26 Squad Ratings Fetcher
Pulls OVR, PAC, SHO, PAS, DRI, DEF, PHY, Acceleration, Positioning, Penalties
for all 48 FIFA World Cup 2026 nations from the MSMC API.
Outputs: eafc26_wc_squad_ratings.csv
"""

import sys, io, json, csv, time, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_BASE = "https://api.msmc.cc/api/eafc/players"
GAME     = "fc26"
GENDER   = "m"

# Mapping for display names to EAFC API nation names
NATION_MAP = {
    "Ivory Coast": "C\u00f4te d'Ivoire",
    "Curacao": "Cura\u00e7ao",
    "Netherlands": "Holland",
    "DR Congo": "Congo DR",
    "South Korea": "Korea Republic",
}

# Nation name as the API recognises it
WC_NATIONS = [
    "Mexico", "Jamaica", "Ecuador", "Venezuela",
    "Canada", "Uruguay", "Panama", "New Zealand",
    "Morocco", "Brazil", "Scotland", "Haiti",
    "United States", "Turkey", "Australia", "Paraguay",
    "Germany", "Ivory Coast", "Curacao",
    "Netherlands", "Japan", "Sweden", "Tunisia",
    "Belgium", "Iran", "Egypt",
    "Spain", "Cape Verde", "Saudi Arabia",
    "France", "Norway", "Senegal", "Iraq",
    "Argentina", "Austria", "Algeria", "Jordan",
    "Portugal", "Colombia", "DR Congo", "Uzbekistan",
    "England", "Croatia", "Ghana",
    "South Korea", "South Africa", "Czech Republic",
    "Bosnia and Herzegovina",
]

# Fields we want to keep
KEEP = ["name", "ovr", "pac", "sho", "pas", "dri",
        "def", "phy", "acceleration", "positioning", "penalties",
        "age", "position", "nation"]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; WC2026Predictor/1.0)"}

def fetch_nation(nation_name):
    params = {
        "game":   GAME,
        "gender": GENDER,
        "nation": nation_name,
    }
    try:
        r = requests.get(API_BASE, params=params, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data
        print(f"  [HTTP {r.status_code}] for {nation_name}")
    except Exception as e:
        print(f"  [ERROR] {nation_name}: {e}")
    return []

def safe_int(val):
    try:
        return int(val) if val not in ("", None) else 0
    except:
        return 0

def process_player(p, nation_label):
    return {
        "Nation":       nation_label,
        "Name":         p.get("name", ""),
        "Position":     p.get("position", ""),
        "Age":          safe_int(p.get("age", 0)),
        "OVR":          safe_int(p.get("ovr", 0)),
        "PAC":          safe_int(p.get("pac", 0)),
        "SHO":          safe_int(p.get("sho", 0)),
        "PAS":          safe_int(p.get("pas", 0)),
        "DRI":          safe_int(p.get("dri", 0)),
        "DEF":          safe_int(p.get("def", 0)),
        "PHY":          safe_int(p.get("phy", 0)),
        "Acceleration": safe_int(p.get("acceleration", 0)),
        "Positioning":  safe_int(p.get("positioning", 0)),
        "Penalties":    safe_int(p.get("penalties", 0)),
    }

def main():
    print("=" * 60)
    print("EA FC 26 WC Squad Ratings Fetcher")
    print("=" * 60)

    all_rows   = []
    failed     = []

    for nation in WC_NATIONS:
        print(f"Fetching {nation}...", end=" ", flush=True)
        query_name = NATION_MAP.get(nation, nation)
        players = fetch_nation(query_name)

        if not players:
            print("[FAIL]")
            failed.append(nation)
            time.sleep(0.5)
            continue

        # Take top 26 by OVR (simulates squad selection)
        players_sorted = sorted(players, key=lambda p: safe_int(p.get("ovr", 0)), reverse=True)
        squad = players_sorted[:26]

        for p in squad:
            all_rows.append(process_player(p, nation))

        avg_ovr = sum(safe_int(p.get("ovr",0)) for p in squad) / len(squad)
        print(f"[OK] {len(squad)} players, avg OVR={avg_ovr:.1f}")
        time.sleep(0.4)   # polite delay

    # ── Save full player-level CSV ──────────────────────────────────────
    player_file = "eafc26_wc_squad_ratings.csv"
    fieldnames  = ["Nation","Name","Position","Age","OVR","PAC","SHO",
                   "PAS","DRI","DEF","PHY","Acceleration","Positioning","Penalties"]

    with open(player_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nSaved {len(all_rows)} player rows -> {player_file}")

    # ── Aggregate to team-level summary ────────────────────────────────
    from collections import defaultdict
    import statistics

    team_data = defaultdict(list)
    for row in all_rows:
        team_data[row["Nation"]].append(row)

    summary_rows = []
    for nation, players in sorted(team_data.items()):
        top11 = sorted(players, key=lambda x: x["OVR"], reverse=True)[:11]
        bench = players[11:]

        def avg(lst, key):
            vals = [x[key] for x in lst if x[key] > 0]
            return round(sum(vals)/len(vals), 2) if vals else 0

        summary_rows.append({
            "Nation":           nation,
            "Squad_Size":       len(players),
            "Avg_OVR":          avg(players, "OVR"),
            "Top11_OVR":        avg(top11,   "OVR"),
            "Bench_OVR":        avg(bench,   "OVR") if bench else 0,
            "Avg_Age":          avg(players, "Age"),
            "Attack_Score":     round((avg(top11,"SHO") + avg(top11,"PAC") +
                                       avg(top11,"Acceleration") +
                                       avg(top11,"Positioning") +
                                       avg(top11,"DRI")) / 5, 2),
            "Defense_Score":    round((avg(top11,"DEF") + avg(top11,"PHY")) / 2, 2),
            "Penalty_Score":    avg(players, "Penalties"),
        })

    summary_file = "eafc26_wc_team_summary.csv"
    summary_fields = ["Nation","Squad_Size","Avg_OVR","Top11_OVR","Bench_OVR",
                      "Avg_Age","Attack_Score","Defense_Score","Penalty_Score"]

    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_fields)
        w.writeheader()
        w.writerows(sorted(summary_rows, key=lambda x: x["Top11_OVR"], reverse=True))
    print(f"Saved team summary -> {summary_file}")

    # ── Print league table ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"{'Nation':<28} {'Top11 OVR':>10} {'ATK':>6} {'DEF':>6} {'PEN':>6} {'Age':>5}")
    print("-" * 60)
    for r in sorted(summary_rows, key=lambda x: x["Top11_OVR"], reverse=True):
        print(f"{r['Nation']:<28} {r['Top11_OVR']:>10} "
              f"{r['Attack_Score']:>6} {r['Defense_Score']:>6} "
              f"{r['Penalty_Score']:>6} {r['Avg_Age']:>5}")

    if failed:
        print(f"\n[WARN] Could not fetch: {', '.join(failed)}")

    print("\nDone. Files ready for predict_world_cup.py integration.")

if __name__ == "__main__":
    main()
