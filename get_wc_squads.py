"""
FIFA World Cup 2026 Squad Scraper + EA FC Rating Cross-Reference
================================================================
1. Scrapes all 48 WC squads from Wikipedia (2026_FIFA_World_Cup_squads)
2. Cross-references player names against eafc26_wc_squad_ratings.csv
3. Computes Top11_OVR, Attack_Score, Defense_Score, Penalty_Score
   using ONLY players actually in the WC squad
4. Writes corrected eafc26_wc_team_summary.csv
"""

import sys
import io
import re
import csv
import time
import requests
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}
WIKI_API = "https://en.wikipedia.org/w/api.php"


# ── Wikipedia scraper ─────────────────────────────────────────────────────────

def get_wiki_page_html(title):
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": "2"
    }
    resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        if "parse" in data:
            return data["parse"]["text"]
    return None


# Position icon prefix → standard position code
# Wikipedia renders position cells like "1  GK" or "2  DF" etc.
POS_ICON_MAP = {
    '1': 'GK',
    '2': 'DF',
    '3': 'MF',
    '4': 'FW',
}

# The Wikipedia article uses these exact h3 id values for the nation headings.
# Map underscore-id → canonical nation name
HEADING_ID_TO_NATION = {
    'Czech_Republic': 'Czech Republic',
    'Mexico': 'Mexico',
    'South_Africa': 'South Africa',
    'South_Korea': 'South Korea',
    'Bosnia_and_Herzegovina': 'Bosnia and Herzegovina',
    'Canada': 'Canada',
    'Qatar': 'Qatar',
    'Switzerland': 'Switzerland',
    'Brazil': 'Brazil',
    'Haiti': 'Haiti',
    'Morocco': 'Morocco',
    'Scotland': 'Scotland',
    'Australia': 'Australia',
    'Paraguay': 'Paraguay',
    'Turkey': 'Turkey',
    'United_States': 'United States',
    'Cura%C3%A7ao': 'Curacao',
    'Ecuador': 'Ecuador',
    'Germany': 'Germany',
    'Ivory_Coast': 'Ivory Coast',
    'Japan': 'Japan',
    'Netherlands': 'Netherlands',
    'Sweden': 'Sweden',
    'Tunisia': 'Tunisia',
    'Belgium': 'Belgium',
    'Croatia': 'Croatia',
    'Ghana': 'Ghana',
    'South_Korea': 'South Korea',
    'Colombia': 'Colombia',
    'Argentina': 'Argentina',
    'Algeria': 'Algeria',
    'Egypt': 'Egypt',
    'Uruguay': 'Uruguay',
    'Panama': 'Panama',
    'Venezuela': 'Venezuela',
    'Jamaica': 'Jamaica',
    'France': 'France',
    'Norway': 'Norway',
    'Senegal': 'Senegal',
    'Saudi_Arabia': 'Saudi Arabia',
    'Iran': 'Iran',
    'Iraq': 'Iraq',
    'Jordan': 'Jordan',
    'Uzbekistan': 'Uzbekistan',
    'Cape_Verde': 'Cape Verde',
    'New_Zealand': 'New Zealand',
    'Portugal': 'Portugal',
    'England': 'England',
    'DR_Congo': 'DR Congo',
    'Austria': 'Austria',
    'Spain': 'Spain',
    'Jamaica': 'Jamaica',
    'Venezuela': 'Venezuela',
    'Switzerland': 'Switzerland',
    # Also handle direct text matches (the text in the heading)
}

# Extra text-based matching for headings with special chars
HEADING_TEXT_TO_NATION = {
    'Czech Republic': 'Czech Republic',
    'Mexico': 'Mexico',
    'South Africa': 'South Africa',
    'South Korea': 'South Korea',
    'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
    'Canada': 'Canada',
    'Qatar': 'Qatar',
    'Switzerland': 'Switzerland',
    'Brazil': 'Brazil',
    'Haiti': 'Haiti',
    'Morocco': 'Morocco',
    'Scotland': 'Scotland',
    'Australia': 'Australia',
    'Paraguay': 'Paraguay',
    'Turkey': 'Turkey',
    'United States': 'United States',
    'Ecuador': 'Ecuador',
    'Germany': 'Germany',
    'Ivory Coast': 'Ivory Coast',
    'Japan': 'Japan',
    'Netherlands': 'Netherlands',
    'Sweden': 'Sweden',
    'Tunisia': 'Tunisia',
    'Belgium': 'Belgium',
    'Croatia': 'Croatia',
    'Ghana': 'Ghana',
    'Colombia': 'Colombia',
    'Argentina': 'Argentina',
    'Algeria': 'Algeria',
    'Egypt': 'Egypt',
    'Uruguay': 'Uruguay',
    'Panama': 'Panama',
    'Venezuela': 'Venezuela',
    'Jamaica': 'Jamaica',
    'France': 'France',
    'Norway': 'Norway',
    'Senegal': 'Senegal',
    'Saudi Arabia': 'Saudi Arabia',
    'Iran': 'Iran',
    'Iraq': 'Iraq',
    'Jordan': 'Jordan',
    'Uzbekistan': 'Uzbekistan',
    'Cape Verde': 'Cape Verde',
    'New Zealand': 'New Zealand',
    'Portugal': 'Portugal',
    'England': 'England',
    'DR Congo': 'DR Congo',
    'Austria': 'Austria',
    'Spain': 'Spain',
    'Jamaica': 'Jamaica',
    'Venezuela': 'Venezuela',
    'Switzerland': 'Switzerland',
}


def extract_name_clean(raw):
    """Remove footnotes, (captain), extra spaces from a player name."""
    name = re.sub(r'\[.*?\]', '', raw)
    name = re.sub(r'\(\s*captain\s*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(c\)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\u200b', '', name)   # zero-width space
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def extract_position(pos_cell_text):
    """
    Extract position code from Wikipedia position cell.
    Wikipedia renders positions like '1  GK', '2  DF', '3  MF', '4  FW'
    where the leading number is an icon index.
    Also handles plain 'GK'/'DF'/'MF'/'FW'.
    """
    t = pos_cell_text.strip()
    # Check for explicit position codes
    for code in ['GK', 'DF', 'MF', 'FW']:
        if code in t.upper():
            return code
    # Check for numeric icon prefix
    m = re.match(r'^(\d+)', t)
    if m:
        return POS_ICON_MAP.get(m.group(1), '')
    return ''


def parse_squads_from_main_article(html):
    """
    Parse the 2026_FIFA_World_Cup_squads Wikipedia article.
    Headings have format: <h3 id="Mexico">Mexico</h3>
    Tables follow immediately after the heading.
    """
    squads = {}

    # Find ALL heading tags with their positions
    # Pattern: <h2 id="Group_A">Group A</h2>  or  <h3 id="Mexico">Mexico</h3>
    heading_pattern = re.compile(
        r'<h([234])\s+id="([^"]*)"[^>]*>(.*?)</h\1>',
        re.DOTALL
    )

    headings = []
    for m in heading_pattern.finditer(html):
        level = int(m.group(1))
        hid = m.group(2)
        text = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        text = re.sub(r'\[.*?\]', '', text).strip()
        text = re.sub(r'\s+', ' ', text).strip()

        # Try to resolve nation
        nation = HEADING_ID_TO_NATION.get(hid) or HEADING_TEXT_TO_NATION.get(text)

        # Handle encoding variants for Curaçao
        if not nation and ('ura' in hid or 'ura' in text.lower()):
            nation = 'Curacao'

        headings.append({
            'level': level,
            'id': hid,
            'text': text,
            'nation': nation,
            'start': m.start(),
            'end': m.end()
        })

    print(f"    Found {len(headings)} headings total")
    nation_headings = [h for h in headings if h['nation']]
    print(f"    Nation headings: {len(nation_headings)}")

    for i, h in enumerate(headings):
        if not h['nation']:
            continue

        nation = h['nation']

        # Section = from end of this heading to start of next heading
        next_start = headings[i+1]['start'] if i+1 < len(headings) else len(html)
        section_html = html[h['end']:next_start]

        # Find the squad table (largest table in the section)
        tables = re.findall(r'<table[^>]*>(.*?)</table>', section_html, re.DOTALL)
        if not tables:
            print(f"    [WARN] No table found for {nation}")
            continue

        # Use the largest table
        table_html = max(tables, key=len)

        # Extract player rows
        players = []
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)

        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            if len(cells) < 3:
                continue

            # Clean each cell
            clean = []
            for c in cells:
                text = re.sub(r'<[^>]+>', ' ', c)
                text = re.sub(r'&amp;', '&', text)
                text = re.sub(r'&nbsp;', ' ', text)
                text = re.sub(r'&#160;', ' ', text)
                text = re.sub(r'\[.*?\]', '', text)  # Remove footnotes
                text = re.sub(r'\s+', ' ', text).strip()
                clean.append(text)

            if len(clean) < 3:
                continue

            # Row format: No. | Pos. | Player | DOB | Caps | Goals | Club
            shirt = clean[0].strip()
            pos_raw = clean[1].strip()
            name_raw = clean[2].strip()

            # Shirt number must be 1-26
            if not re.match(r'^\d{1,2}$', shirt):
                continue

            pos = extract_position(pos_raw)
            if not pos:
                continue

            name = extract_name_clean(name_raw)
            if not name or len(name) < 2 or len(name) > 60:
                continue

            players.append({
                'Name': name,
                'Position': pos,
                'ShirtNo': shirt
            })

        if players:
            if nation not in squads:
                squads[nation] = []
            squads[nation].extend(players)
            # Deduplicate
            seen = set()
            deduped = []
            for p in squads[nation]:
                k = p['ShirtNo']  # shirt number is unique per team
                if k not in seen:
                    seen.add(k)
                    deduped.append(p)
            squads[nation] = deduped

    return squads


# ── Fuzzy name matching ───────────────────────────────────────────────────────

def normalise(name):
    """Lower-case, normalise accents, strip punctuation for matching."""
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


def name_similarity(a, b):
    """Return similarity score between 0 and 1."""
    na, nb = normalise(a), normalise(b)
    if na == nb:
        return 1.0
    if na in nb or nb in na:
        return 0.92
    parts_a = na.split()
    parts_b = nb.split()
    if parts_a and parts_b and parts_a[-1] == parts_b[-1]:
        return 0.85
    return SequenceMatcher(None, na, nb).ratio()


def find_eafc_player(wiki_name, eafc_players, threshold=0.78):
    """Find the best-matching EA FC player for a Wikipedia player name."""
    best_score = 0.0
    best_player = None
    for ep in eafc_players:
        score = name_similarity(wiki_name, ep['Name'])
        if score > best_score:
            best_score = score
            best_player = ep
    if best_score >= threshold:
        return best_player, best_score
    return None, best_score


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("WC 2026 Squad Cross-Referencer: Wikipedia + EA FC 26 Ratings")
    print("=" * 65)

    # Step 1: Load EA FC player ratings
    print("\n[1] Loading EA FC 26 squad ratings...")
    eafc_by_nation = {}
    with open('eafc26_wc_squad_ratings.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['Penalties']) == 0:
                continue
            nation = row['Nation']
            if nation not in eafc_by_nation:
                eafc_by_nation[nation] = []
            eafc_by_nation[nation].append({
                'Name':         row['Name'],
                'Position':     row['Position'],
                'Age':          int(row['Age']),
                'OVR':          int(row['OVR']),
                'PAC':          int(row['PAC']),
                'SHO':          int(row['SHO']),
                'PAS':          int(row['PAS']),
                'DRI':          int(row['DRI']),
                'DEF':          int(row['DEF']),
                'PHY':          int(row['PHY']),
                'Acceleration': int(row['Acceleration']),
                'Positioning':  int(row['Positioning']),
                'Penalties':    int(row['Penalties']),
            })
    print(f"    Loaded {sum(len(v) for v in eafc_by_nation.values())} EA FC player records "
          f"for {len(eafc_by_nation)} nations.")

    # Step 2: Fetch Wikipedia squads
    print("\n[2] Fetching Wikipedia squad page (2026_FIFA_World_Cup_squads)...")
    html = get_wiki_page_html("2026_FIFA_World_Cup_squads")
    if not html:
        print("    ERROR: Could not fetch Wikipedia page. Aborting.")
        return

    print(f"    HTML length: {len(html)} chars")
    print("    Parsing squad tables...")
    wiki_squads = parse_squads_from_main_article(html)
    print(f"\n    Found squads for {len(wiki_squads)} nations:")
    for nation, players in sorted(wiki_squads.items()):
        print(f"      {nation:<30} {len(players):>2} players")

    if not wiki_squads:
        print("\n    WARNING: No squads found in Wikipedia page! Aborting update.")
        return

    # Save the raw Wikipedia squads
    wc_squad_rows = []
    for nation, players in sorted(wiki_squads.items()):
        for p in players:
            wc_squad_rows.append({
                'Nation': nation,
                'PlayerName': p['Name'],
                'Position': p['Position'],
                'ShirtNo': p['ShirtNo'],
            })
    with open('wc2026_squads.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['Nation', 'PlayerName', 'Position', 'ShirtNo'])
        w.writeheader()
        w.writerows(wc_squad_rows)
    print(f"\n    Saved {len(wc_squad_rows)} players to wc2026_squads.csv")

    # Step 3: Cross-reference and compute corrected team stats
    print("\n[3] Cross-referencing Wikipedia squads with EA FC ratings...")

    def avg(lst, key):
        vals = [x[key] for x in lst if isinstance(x.get(key, 0), (int, float)) and x.get(key, 0) > 0]
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    summary_rows = []
    unmatched_log = []

    for nation in sorted(wiki_squads.keys()):
        wiki_players = wiki_squads[nation]
        eafc_players = eafc_by_nation.get(nation, [])

        matched_eafc = []
        unmatched_wiki = []

        for wp in wiki_players:
            ep, score = find_eafc_player(wp['Name'], eafc_players) if eafc_players else (None, 0)
            if ep:
                matched_eafc.append(ep)
            else:
                unmatched_wiki.append(wp['Name'])

        if unmatched_wiki:
            unmatched_log.append((nation, unmatched_wiki))

        squad_size = len(wiki_players)

        if not matched_eafc:
            matched_eafc = eafc_players
            if not matched_eafc:
                print(f"    [WARN] {nation}: No EA FC data at all — skipping")
                continue
            print(f"    [WARN] {nation}: No EA FC matches — using all EA FC as fallback")

        # Sort by OVR, deduplicate by normalised name
        matched_eafc_sorted = sorted(matched_eafc, key=lambda x: x['OVR'], reverse=True)
        seen_names = set()
        deduped_matched = []
        for ep in matched_eafc_sorted:
            k = normalise(ep['Name'])
            if k not in seen_names:
                seen_names.add(k)
                deduped_matched.append(ep)

        top11 = deduped_matched[:11]
        t11_ovr = avg(top11, 'OVR')

        summary_rows.append({
            'Nation':        nation,
            'Squad_Size':    squad_size,
            'Matched_Count': len(deduped_matched),
            'Avg_OVR':       avg(deduped_matched, 'OVR'),
            'Top11_OVR':     t11_ovr,
            'Bench_OVR':     avg(deduped_matched[11:], 'OVR'),
            'Avg_Age':       avg(deduped_matched, 'Age'),
            'Attack_Score':  round((avg(top11, 'SHO') + avg(top11, 'PAC') +
                                    avg(top11, 'Acceleration') +
                                    avg(top11, 'Positioning') +
                                    avg(top11, 'DRI')) / 5, 2),
            'Defense_Score': round((avg(top11, 'DEF') + avg(top11, 'PHY')) / 2, 2),
            'Penalty_Score': avg(deduped_matched, 'Penalties'),
        })

        print(f"    {nation:<30} wiki={squad_size:>2}  eafc_matched={len(deduped_matched):>2}  "
              f"Top11_OVR={t11_ovr:.1f}  unmatched={len(unmatched_wiki)}")

    # Step 4: Add nations not in Wikipedia (use EA FC only)
    print("\n[4] Adding nations missing from Wikipedia (EA FC only)...")
    wiki_nations = set(wiki_squads.keys())
    for nation, players in eafc_by_nation.items():
        if nation not in wiki_nations:
            deduped = []
            seen_names = set()
            for ep in sorted(players, key=lambda x: x['OVR'], reverse=True):
                k = normalise(ep['Name'])
                if k not in seen_names:
                    seen_names.add(k)
                    deduped.append(ep)
            top11 = deduped[:11]
            t11_ovr = avg(top11, 'OVR')
            summary_rows.append({
                'Nation':        nation,
                'Squad_Size':    len(deduped),
                'Matched_Count': 0,
                'Avg_OVR':       avg(deduped, 'OVR'),
                'Top11_OVR':     t11_ovr,
                'Bench_OVR':     avg(deduped[11:], 'OVR'),
                'Avg_Age':       avg(deduped, 'Age'),
                'Attack_Score':  round((avg(top11,'SHO') + avg(top11,'PAC') +
                                        avg(top11,'Acceleration') +
                                        avg(top11,'Positioning') +
                                        avg(top11,'DRI')) / 5, 2),
                'Defense_Score': round((avg(top11,'DEF') + avg(top11,'PHY')) / 2, 2),
                'Penalty_Score': avg(deduped, 'Penalties'),
            })
            print(f"    {nation:<30} [EA FC only]  Top11_OVR={t11_ovr:.1f}")

    # Step 5: Write updated team summary
    print("\n[5] Writing corrected eafc26_wc_team_summary.csv ...")
    summary_rows.sort(key=lambda x: x['Top11_OVR'], reverse=True)

    fieldnames = ['Nation', 'Squad_Size', 'Avg_OVR', 'Top11_OVR', 'Bench_OVR',
                  'Avg_Age', 'Attack_Score', 'Defense_Score', 'Penalty_Score']

    with open('eafc26_wc_team_summary.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in summary_rows:
            w.writerow({k: row[k] for k in fieldnames})
    print(f"    Saved {len(summary_rows)} rows.")

    # Step 6: Report unmatched players
    if unmatched_log:
        print("\n[6] Unmatched Wikipedia players (no EA FC rating found):")
        total_unmatched = 0
        for nation, names in unmatched_log:
            print(f"    {nation} ({len(names)} unmatched):")
            for n in names[:5]:  # show first 5
                print(f"      - {n}")
            if len(names) > 5:
                print(f"      ... and {len(names)-5} more")
            total_unmatched += len(names)
        print(f"    Total unmatched: {total_unmatched}")

    # Step 7: Final table
    print("\n" + "=" * 65)
    print(f"{'Nation':<28} {'Top11':>6} {'ATK':>6} {'DEF':>6} {'PEN':>6} {'Mtch':>5}")
    print("-" * 65)
    for r in summary_rows:
        flag = '' if r['Matched_Count'] > 0 else ' [EA only]'
        print(f"{r['Nation']:<28} {r['Top11_OVR']:>6.1f} "
              f"{r['Attack_Score']:>6.1f} {r['Defense_Score']:>6.1f} "
              f"{r['Penalty_Score']:>6.1f} {r['Matched_Count']:>5}{flag}")

    print("\n" + "=" * 65)
    print("DONE. Updated files:")
    print("  wc2026_squads.csv           — actual WC squads from Wikipedia")
    print("  eafc26_wc_team_summary.csv  — corrected team stats (WC players only)")
    print("=" * 65)


if __name__ == "__main__":
    main()
