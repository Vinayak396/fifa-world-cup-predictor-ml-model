import csv
import json
import re
import sys
import io
import time
import requests
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_BASE = "https://api.msmc.cc/api/eafc/players"
GAME     = "fc26"
GENDER   = "m"

NATION_MAP = {
    "Ivory Coast": "Côte d'Ivoire",
    "Curacao": "Curaçao",
    "Netherlands": "Holland",
    "DR Congo": "Congo DR",
    "South Korea": "Korea Republic",
}

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

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; WC2026Predictor/1.0)"}

def clean_name(name):
    if not isinstance(name, str):
        return name
    name = name.strip()
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'^\s*[\u200b-\u200d\ufeff]\s*', '', name)
    name = name.strip()
    if 'Cura' in name:
        return 'Curacao'
    if 'Côte' in name or 'Cte' in name:
        return 'Ivory Coast'
    if 'T\u00fcrk' in name or 'Trkiye' in name or 'Trkiye' in name:
        return 'Turkey'
    return name

def normalise(name):
    replacements = {
        '\u00e1': 'a', '\u00e0': 'a', '\u00e3': 'a', '\u00e2': 'a', '\u00e4': 'a', '\u0101': 'a', '\u00e5': 'a',
        '\u00e9': 'e', '\u00e8': 'e', '\u00ea': 'e', '\u00eb': 'e', '\u011b': 'e', '\u0113': 'e',
        '\u00ed': 'i', '\u00ec': 'i', '\u00ee': 'i', '\u00ef': 'i', '\u012b': 'i',
        '\u00f3': 'o', '\u00f2': 'o', '\u00f4': 'o', '\u00f6': 'o', '\u00f5': 'o', '\u00f8': 'o', '\u014d': 'o',
        '\u00fa': 'u', '\u00f9': 'u', '\u00fb': 'u', '\u00fc': 'u', '\u016b': 'u',
        '\u00fd': 'y', '\u00f1': 'n', '\u00e7': 'c', '\u0219': 's', '\u015f': 's',
        '\u021b': 't', '\u017e': 'z', '\u017a': 'z', '\u017c': 'z',
        '\u010d': 'c', '\u0107': 'c', '\u0161': 's', '\u0159': 'r', '\u013a': 'l', '\u013e': 'l',
        '\u00f0': 'd', '\u00fe': 'th', '\u011f': 'g', '\u0131': 'i', '\u00e6': 'ae',
        '\u00f8': 'o',
    }
    n = name.lower()
    for k, v in replacements.items():
        n = n.replace(k, v)
    n = re.sub(r"[^a-z\s'-]", '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def match_player(parsed_name, eafc_players):
    p_norm = normalise(parsed_name)
    best_match = None
    best_score = 0.0
    
    # Try exact match first
    for ep in eafc_players:
        s_norm = normalise(ep.get('name', ''))
        if p_norm == s_norm:
            return ep
            
    # Try substring match or name_similarity
    for ep in eafc_players:
        s_norm = normalise(ep.get('name', ''))
        
        parts_p = set(p_norm.split())
        parts_s = set(s_norm.split())
        
        common = parts_p.intersection(parts_s)
        if len(common) >= 2 or (len(parts_p) == 1 and len(common) >= 1) or (len(parts_s) == 1 and len(common) >= 1):
            score = SequenceMatcher(None, p_norm, s_norm).ratio()
            if score > best_score:
                best_score = score
                best_match = ep
                
    if best_score >= 0.75:
        return best_match
        
    return None

def fetch_nation(nation_name):
    params = {
        "game":   GAME,
        "gender": GENDER,
        "nation": nation_name,
    }
    max_retries = 5
    backoff = 1.0
    for attempt in range(max_retries):
        try:
            r = requests.get(API_BASE, params=params, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    return data
            elif r.status_code == 429:
                print(f"  [HTTP 429] for {nation_name}. Retrying in {backoff}s...")
            else:
                print(f"  [HTTP {r.status_code}] for {nation_name}")
        except Exception as e:
            print(f"  [ERROR] {nation_name}: {e}")
        time.sleep(backoff)
        backoff *= 2.0
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
    print("EA FC 26 Active Squad Ratings Fetcher")
    print("=" * 60)
    
    # 1. Load active players map
    with open('active_players_by_nation.json', 'r', encoding='utf-8') as f:
        active_players = json.load(f)
        
    all_rows = []
    failed = []
    
    for nation in WC_NATIONS:
        print(f"Fetching {nation}...", end=" ", flush=True)
        query_name = NATION_MAP.get(nation, nation)
        players = fetch_nation(query_name)
        
        if not players:
            print("[FAIL]")
            failed.append(nation)
            time.sleep(0.5)
            continue
            
        # Get active players for this nation
        active_names = active_players.get(clean_name(nation), [])
        
        matched_players = []
        unmatched_names = []
        for name in active_names:
            matched_p = match_player(name, players)
            if matched_p:
                matched_players.append(matched_p)
            else:
                unmatched_names.append(name)
                
        # Deduplicate matched players by normalised name
        seen_names = set()
        deduped_matched = []
        for ep in matched_players:
            k = normalise(ep.get('name', ''))
            if k not in seen_names:
                seen_names.add(k)
                deduped_matched.append(ep)
                
        # Fallback if no players matched (e.g. empty active players or error)
        if not deduped_matched:
            # Sort by OVR, take top 26
            players_sorted = sorted(players, key=lambda p: safe_int(p.get("ovr", 0)), reverse=True)
            deduped_matched = players_sorted[:26]
            print(f"[OK/FALLBACK] Using top 26 squad players (0 active matched)")
        else:
            print(f"[OK] {len(deduped_matched)} active matched, {len(unmatched_names)} unmatched")
            if unmatched_names:
                print(f"    Unmatched names: {unmatched_names}")
                
        for p in deduped_matched:
            all_rows.append(process_player(p, nation))
            
        time.sleep(0.4) # polite delay
        
    # Write to eafc26_wc_squad_ratings.csv
    player_file = "eafc26_wc_squad_ratings.csv"
    fieldnames  = ["Nation","Name","Position","Age","OVR","PAC","SHO",
                   "PAS","DRI","DEF","PHY","Acceleration","Positioning","Penalties"]
                   
    with open(player_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nSaved {len(all_rows)} active player rows -> {player_file}")
    
    # Aggregate and calculate team stats
    from collections import defaultdict
    team_data = defaultdict(list)
    for row in all_rows:
        team_data[row["Nation"]].append(row)
        
    summary_rows = []
    for nation, players in sorted(team_data.items()):
        def avg(lst, key):
            vals = [x[key] for x in lst if x[key] > 0]
            return round(sum(vals)/len(vals), 2) if vals else 0
            
        avg_ovr = avg(players, "OVR")
        
        summary_rows.append({
            "Nation":           nation,
            "Squad_Size":       len(players),
            "Avg_OVR":          avg_ovr,
            "Top11_OVR":        avg_ovr, # Same as Avg_OVR since we are not using top 11
            "Bench_OVR":        0.0,     # Set to 0 since we use all active players
            "Avg_Age":          avg(players, "Age"),
            "Attack_Score":     round((avg(players,"SHO") + avg(players,"PAC") +
                                       avg(players,"Acceleration") +
                                       avg(players,"Positioning") +
                                       avg(players,"DRI")) / 5, 2),
            "Defense_Score":    round((avg(players,"DEF") + avg(players,"PHY")) / 2, 2),
            "Penalty_Score":    avg(players, "Penalties"),
        })
        
    summary_file = "eafc26_wc_team_summary.csv"
    summary_fields = ["Nation","Squad_Size","Avg_OVR","Top11_OVR","Bench_OVR",
                      "Avg_Age","Attack_Score","Defense_Score","Penalty_Score"]
                      
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_fields)
        w.writeheader()
        w.writerows(sorted(summary_rows, key=lambda x: x["Top11_OVR"], reverse=True))
    print(f"Saved active team summary -> {summary_file}")
    
    if failed:
        print(f"\n[WARN] Could not fetch: {', '.join(failed)}")
        
    print("\nDONE. All active player ratings generated and team summaries updated.")

if __name__ == '__main__':
    main()
