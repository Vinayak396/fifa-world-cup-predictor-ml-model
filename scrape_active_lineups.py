import requests
import re
import csv
import json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import time

WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

TEAM_MAPPING = {
    'USA': 'United States',
    'IR Iran': 'Iran',
    'Congo DR': 'DR Congo',
    'Cabo Verde': 'Cape Verde',
    'Korea Republic': 'South Korea',
    'Côte d\'Ivoire': 'Ivory Coast',
    'T\u00fcrkiye': 'Turkey',
    'Trkiye': 'Turkey',
    'Czechia': 'Czech Republic',
    'Aotearoa New Zealand': 'New Zealand',
    'Curaao': 'Curacao',
    'Curaçao': 'Curacao'
}

def clean_name(name):
    if not isinstance(name, str):
        return name
    name = name.strip()
    # Remove flags or wiki markup if any
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'^\s*[\u200b-\u200d\ufeff]\s*', '', name)
    name = name.strip()
    if 'Cura' in name:
        return 'Curacao'
    if 'Côte' in name or 'Cte' in name:
        return 'Ivory Coast'
    if 'T\u00fcrk' in name or 'Trkiye' in name or 'Trkiye' in name:
        return 'Turkey'
    return TEAM_MAPPING.get(name, name)

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

def match_player(parsed_name, squad_players):
    p_norm = normalise(parsed_name)
    best_match = None
    best_score = 0.0
    
    # Try exact match first
    for s_player in squad_players:
        s_norm = normalise(s_player)
        if p_norm == s_norm:
            return s_player
            
    # Try substring match or name_similarity
    for s_player in squad_players:
        s_norm = normalise(s_player)
        
        # Check if last name matches or subset of parts
        parts_p = set(p_norm.split())
        parts_s = set(s_norm.split())
        
        common = parts_p.intersection(parts_s)
        if len(common) >= 2 or (len(parts_p) == 1 and len(common) >= 1) or (len(parts_s) == 1 and len(common) >= 1):
            score = SequenceMatcher(None, p_norm, s_norm).ratio()
            if score > best_score:
                best_score = score
                best_match = s_player
                
    if best_score >= 0.75:
        return best_match
        
    return None

def get_wiki_page_html(title):
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": "2"
    }
    
    max_retries = 8
    backoff = 2.0
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if "parse" in data:
                    return data["parse"]["text"]
            elif resp.status_code == 429:
                print(f"    Rate limited (429) on {title}. Retrying in {backoff}s...")
            else:
                print(f"    Received status code {resp.status_code} for {title}")
        except Exception as e:
            print(f"    Error fetching {title} (attempt {attempt+1}/{max_retries}): {e}")
            
        time.sleep(backoff)
        backoff *= 2.0 # Exponential backoff
        
    return None

def parse_single_team_lineup(table):
    """
    Parse a single team's lineup table.
    Returns: list of clean names that played (starts + subbed on)
    """
    players = []
    rows = table.find_all('tr')
    
    is_sub_section = False
    pos_list = {'GK', 'DF', 'MF', 'FW', 'RB', 'LB', 'CB', 'DM', 'CM', 'LM', 'RM', 'AM', 'RW', 'LW', 'CF', 'RF', 'LF', 'RWB', 'LWB'}
    
    for tr in rows:
        tds = tr.find_all('td')
        row_text = tr.get_text(strip=True).lower()
        
        if 'substitutes' in row_text or 'substitutions' in row_text:
            is_sub_section = True
            continue
        elif 'manager' in row_text:
            break
            
        if len(tds) >= 3:
            pos_text = tds[0].get_text(strip=True)
            pos_clean = re.sub(r'\d+', '', pos_text).strip()
            
            if pos_clean in pos_list:
                a = tds[2].find('a')
                if a and a.get('href') and '/wiki/' in a.get('href'):
                    player_name = a.get_text(strip=True)
                    
                    if not is_sub_section:
                        players.append(player_name)
                    else:
                        tds_html = "".join(str(td) for td in tds[3:])
                        is_sub = 'Substituted on' in tds_html or 'Sub_on.svg' in tds_html or 'upward-facing green arrow' in tds_html
                        if is_sub:
                            players.append(player_name)
                            
    return players

def main():
    # 1. Load squads
    squad_players = {} # nation -> list of player names
    with open('wc2026_squads.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nation = clean_name(row['Nation'])
            if nation not in squad_players:
                squad_players[nation] = []
            squad_players[nation].append(row['PlayerName'])
            
    print(f"Loaded squads for {len(squad_players)} nations.")
    
    # 2. Setup pages to scrape
    pages = [f"2026_FIFA_World_Cup_Group_{c}" for c in 'ABCDEFGHIJKL']
    pages.append("2026_FIFA_World_Cup_knockout_stage")
    
    active_players = {nation: set() for nation in squad_players.keys()}
    match_count = 0
    
    for page in pages:
        print(f"Scraping page: {page}...")
        html = get_wiki_page_html(page)
        if not html:
            print(f"  [ERROR] Failed to fetch {page} after retries. Skipping.")
            continue
            
        soup = BeautifulSoup(html, 'html.parser')
        matches = soup.find_all(class_=re.compile(r'footballbox|vevent', re.IGNORECASE))
        print(f"  Found {len(matches)} match boxes on {page}")
        
        for m in matches:
            home_team_el = m.find(class_=re.compile(r'fhome|home', re.IGNORECASE))
            away_team_el = m.find(class_=re.compile(r'faway|away', re.IGNORECASE))
            
            if not home_team_el or not away_team_el:
                continue
                
            home_team = clean_name(home_team_el.get_text(strip=True))
            away_team = clean_name(away_team_el.get_text(strip=True))
            
            # Find lineup table by scanning siblings
            lineup_table = None
            sib = m.next_sibling
            while sib:
                if sib.name == 'div' and 'footballbox' in sib.get('class', []):
                    break
                if sib.name == 'table':
                    has_gk = False
                    for tr in sib.find_all('tr'):
                        tds = tr.find_all('td')
                        if len(tds) >= 3 and tds[0].get_text(strip=True) == 'GK':
                            has_gk = True
                            break
                    if has_gk:
                        lineup_table = sib
                        break
                sib = sib.next_sibling
                
            if lineup_table:
                # Find leaf tables in the lineup table
                lineup_tables = []
                for tbl in lineup_table.find_all('table'):
                    if len(tbl.find_all('table')) == 0:
                        has_gk = False
                        for tr in tbl.find_all('tr'):
                            tds = tr.find_all('td')
                            if len(tds) >= 3 and tds[0].get_text(strip=True) == 'GK':
                                has_gk = True
                                break
                        if has_gk:
                            lineup_tables.append(tbl)
                            
                # Fallback: if no nested tables found, check if the lineup_table itself is a leaf table
                if len(lineup_tables) == 0 and len(lineup_table.find_all('table')) == 0:
                    lineup_tables.append(lineup_table)
                    
                if len(lineup_tables) == 2:
                    h_players = parse_single_team_lineup(lineup_tables[0])
                    a_players = parse_single_team_lineup(lineup_tables[1])
                    match_count += 1
                    
                    # Match to squads
                    home_squad = squad_players.get(home_team, [])
                    away_squad = squad_players.get(away_team, [])
                    
                    matched_home = 0
                    for hp in h_players:
                        matched = match_player(hp, home_squad)
                        if matched:
                            active_players[home_team].add(matched)
                            matched_home += 1
                        
                    matched_away = 0
                    for ap in a_players:
                        matched = match_player(ap, away_squad)
                        if matched:
                            active_players[away_team].add(matched)
                            matched_away += 1
                            
                    print(f"    Match {match_count}: {home_team} ({matched_home}/{len(h_players)}) v {away_team} ({matched_away}/{len(a_players)})")
            else:
                # If no lineup table in this match box, it might not have lineups yet (or unplayed match)
                pass
                
        time.sleep(2.0) # Longer sleep to avoid rate limiting
        
    # Print summary of results
    print("\n" + "="*40)
    print("ACTIVE PLAYERS SUMMARY")
    print("="*40)
    
    output_dict = {}
    for nation, players in sorted(active_players.items()):
        players_list = sorted(list(players))
        output_dict[nation] = players_list
        print(f"  {nation:<30} {len(players_list)} active players matched")
        
    with open('active_players_by_nation.json', 'w', encoding='utf-8') as f:
        json.dump(output_dict, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved active players mapping to active_players_by_nation.json")

if __name__ == '__main__':
    main()
