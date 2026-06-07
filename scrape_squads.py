"""
FIFA World Cup 2026 Squad Scraper
Uses Wikipedia API + BeautifulSoup to extract all 48 team squads
Saves clean CSV to wc2026_squads.csv
"""

import sys
import io
import re
import csv
import time
import json
import requests
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Wikipedia REST API returns clean parsed HTML — not blocked like direct page access
WIKI_API = "https://en.wikipedia.org/w/api.php"

def get_wiki_page_html(title):
    """Fetch Wikipedia page rendered HTML via the MediaWiki API."""
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": "2"
    }
    resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        if "parse" in data:
            return data["parse"]["text"]
    return None

def extract_age(dob_str):
    """Calculate age from YYYY-MM-DD string."""
    try:
        dob = datetime.strptime(dob_str[:10], "%Y-%m-%d")
        today = datetime(2026, 6, 11)  # Tournament start date
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except:
        return ""

def parse_squad_table(html, team_name):
    """
    Parse player rows from a Wikipedia squad wikitable.
    
    Standard Wikipedia WC squad table columns:
    No. | Pos. | Player | Date of birth (age) | Caps | Goals | Club
    """
    players = []
    
    # Find all table rows with player data
    # A squad row has a shirt number, position code (GK/DF/MF/FW), player name, and DOB
    
    # Pattern: find <tr> blocks containing position codes
    pos_map = {
        'GK': 'GK', 'DF': 'DEF', 'MF': 'MID', 'FW': 'FWD',
        'Goalkeeper': 'GK', 'Defender': 'DEF', 'Midfielder': 'MID', 'Forward': 'FWD'
    }
    
    # Extract all table rows
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows:
        # Clean HTML tags for easier parsing
        clean = re.sub(r'<[^>]+>', ' ', row)
        clean = re.sub(r'\s+', ' ', clean).strip()
        clean = re.sub(r'&amp;', '&', clean)
        clean = re.sub(r'&#160;', ' ', clean)
        clean = re.sub(r'&nbsp;', ' ', clean)
        
        # Try to identify player rows by position code
        # A valid row should have: number, position, name, dob
        # Example: "1 GK Hugo Lloris (1986-12-26) 145 8 Tottenham Hotspur"
        
        # Match: number, position, then content with a date
        match = re.match(
            r'\s*(\d{1,2})\s+(GK|DF|MF|FW)\s+(.+?)\s*\(?\s*(\d{4}-\d{2}-\d{2})',
            clean
        )
        
        if match:
            shirt = match.group(1)
            pos = pos_map.get(match.group(2), match.group(2))
            name_raw = match.group(3).strip()
            dob = match.group(4)
            
            # Clean name: remove trailing "c" (captain marker), extra spaces
            name = re.sub(r'\s*\(c\)\s*$', '', name_raw).strip()
            name = re.sub(r'\s+', ' ', name).strip()
            
            # Extract club - comes after the date/age block, caps, goals
            # Pattern: after dob, skip age, caps, goals, then club name
            after_dob = clean[match.end():]
            # Skip: age in parens, caps number, goals number -> club name
            club_match = re.search(r'\d+\)\s+\d+\s+\d+\s+(.+)', after_dob)
            if not club_match:
                # Try simpler pattern
                club_match = re.search(r'\d+\s+\d+\s+(.+)', after_dob)
            
            club = club_match.group(1).strip() if club_match else ""
            # Remove trailing garbage
            club = re.sub(r'\s*\[.*?\]\s*$', '', club).strip()
            
            age = extract_age(dob)
            
            if name and len(name) > 2 and len(name) < 60:
                players.append({
                    'Nation': team_name,
                    'PlayerName': name,
                    'Position': pos,
                    'Age': str(age),
                    'Club': club,
                    'ShirtNumber': shirt
                })
    
    return players

# The main Wikipedia article with all 48 squads
MAIN_ARTICLE = "2026_FIFA_World_Cup_squads"

# Per-team Wikipedia article naming (some teams have dedicated pages)
TEAM_ARTICLES = {
    "Mexico":               "Mexico_at_the_2026_FIFA_World_Cup",
    "Jamaica":              "Jamaica_at_the_2026_FIFA_World_Cup",
    "Ecuador":              "Ecuador_at_the_2026_FIFA_World_Cup",
    "Venezuela":            "Venezuela_at_the_2026_FIFA_World_Cup",
    "Canada":               "Canada_at_the_2026_FIFA_World_Cup",
    "Uruguay":              "Uruguay_at_the_2026_FIFA_World_Cup",
    "Panama":               "Panama_at_the_2026_FIFA_World_Cup",
    "New Zealand":          "New_Zealand_at_the_2026_FIFA_World_Cup",
    "Morocco":              "Morocco_at_the_2026_FIFA_World_Cup",
    "Brazil":               "Brazil_at_the_2026_FIFA_World_Cup",
    "Scotland":             "Scotland_at_the_2026_FIFA_World_Cup",
    "Haiti":                "Haiti_at_the_2026_FIFA_World_Cup",
    "United States":        "United_States_at_the_2026_FIFA_World_Cup",
    "Turkey":               "Turkey_at_the_2026_FIFA_World_Cup",
    "Australia":            "Australia_at_the_2026_FIFA_World_Cup",
    "Paraguay":             "Paraguay_at_the_2026_FIFA_World_Cup",
    "Germany":              "Germany_at_the_2026_FIFA_World_Cup",
    "Ivory Coast":          "Ivory_Coast_at_the_2026_FIFA_World_Cup",
    "Curacao":              "Cura%C3%A7ao_at_the_2026_FIFA_World_Cup",
    "Netherlands":          "Netherlands_at_the_2026_FIFA_World_Cup",
    "Japan":                "Japan_at_the_2026_FIFA_World_Cup",
    "Sweden":               "Sweden_at_the_2026_FIFA_World_Cup",
    "Tunisia":              "Tunisia_at_the_2026_FIFA_World_Cup",
    "Belgium":              "Belgium_at_the_2026_FIFA_World_Cup",
    "Iran":                 "Iran_at_the_2026_FIFA_World_Cup",
    "Egypt":                "Egypt_at_the_2026_FIFA_World_Cup",
    "Spain":                "Spain_at_the_2026_FIFA_World_Cup",
    "Cape Verde":           "Cape_Verde_at_the_2026_FIFA_World_Cup",
    "Saudi Arabia":         "Saudi_Arabia_at_the_2026_FIFA_World_Cup",
    "France":               "France_at_the_2026_FIFA_World_Cup",
    "Norway":               "Norway_at_the_2026_FIFA_World_Cup",
    "Senegal":              "Senegal_at_the_2026_FIFA_World_Cup",
    "Iraq":                 "Iraq_at_the_2026_FIFA_World_Cup",
    "Argentina":            "Argentina_at_the_2026_FIFA_World_Cup",
    "Austria":              "Austria_at_the_2026_FIFA_World_Cup",
    "Algeria":              "Algeria_at_the_2026_FIFA_World_Cup",
    "Jordan":               "Jordan_at_the_2026_FIFA_World_Cup",
    "Portugal":             "Portugal_at_the_2026_FIFA_World_Cup",
    "Colombia":             "Colombia_at_the_2026_FIFA_World_Cup",
    "DR Congo":             "Democratic_Republic_of_the_Congo_at_the_2026_FIFA_World_Cup",
    "Uzbekistan":           "Uzbekistan_at_the_2026_FIFA_World_Cup",
    "England":              "England_at_the_2026_FIFA_World_Cup",
    "Croatia":              "Croatia_at_the_2026_FIFA_World_Cup",
    "Ghana":                "Ghana_at_the_2026_FIFA_World_Cup",
    "South Korea":          "South_Korea_at_the_2026_FIFA_World_Cup",
    "South Africa":         "South_Africa_at_the_2026_FIFA_World_Cup",
    "Czech Republic":       "Czech_Republic_at_the_2026_FIFA_World_Cup",
    "Bosnia and Herzegovina": "Bosnia_and_Herzegovina_at_the_2026_FIFA_World_Cup",
}

def scrape_all_from_main_article():
    """
    Try to get all squads from the single Wikipedia article
    '2026 FIFA World Cup squads' which has all teams in one page.
    """
    print("Trying main Wikipedia article (all teams in one page)...")
    html = get_wiki_page_html(MAIN_ARTICLE)
    if not html:
        print("  Main article not found or not yet created on Wikipedia.")
        return {}
    
    print("  Main article found! Parsing...")
    
    # The main article has sections per team. Find team headers then parse tables below them.
    # Team headers look like: <h3><span class="mw-headline" id="Group_A">Group A</span></h3>
    # followed by team subsections
    
    teams_data = {}
    
    # Split by team headings - h4 or h3 level with team names
    team_sections = re.split(r'<h[34][^>]*>\s*<span[^>]*>(.*?)</span>', html)
    
    current_team = None
    for i, section in enumerate(team_sections):
        clean = re.sub(r'<[^>]+>', '', section).strip()
        # Check if this is a team name heading
        if clean in TEAM_ARTICLES or any(t.lower() == clean.lower() for t in TEAM_ARTICLES):
            current_team = clean
        elif current_team and '<table' in section:
            players = parse_squad_table(section, current_team)
            if players:
                teams_data[current_team] = players
                print(f"  Found {len(players)} players for {current_team}")
    
    return teams_data

def scrape_per_team():
    """
    Fallback: scrape each team's individual Wikipedia page.
    """
    all_players = []
    failed = []
    
    for team_name, article_title in TEAM_ARTICLES.items():
        print(f"  Fetching {team_name}...", end=" ", flush=True)
        
        html = get_wiki_page_html(article_title.replace('%C3%A7', 'ç'))
        
        if not html:
            print("[not found]")
            failed.append(team_name)
            time.sleep(0.5)
            continue
        
        players = parse_squad_table(html, team_name)
        
        if players:
            all_players.extend(players)
            print(f"[OK] {len(players)} players")
        else:
            print("[parsed but 0 players - page may not have squad table yet]")
            failed.append(team_name)
        
        time.sleep(0.4)  # Polite rate limiting
    
    if failed:
        print(f"\nFailed/empty for {len(failed)} teams: {', '.join(failed)}")
    
    return all_players

def main():
    print("=" * 60)
    print("FIFA World Cup 2026 Squad Scraper (Wikipedia API)")
    print("=" * 60)
    
    all_players = []
    
    # Step 1: Try the single main article first (most efficient)
    main_data = scrape_all_from_main_article()
    if main_data:
        for team_players in main_data.values():
            all_players.extend(team_players)
        print(f"\nGot {len(all_players)} players from main article.")
    
    # Step 2: For teams not found in main article, scrape individually
    teams_found = set(main_data.keys())
    teams_needed = set(TEAM_ARTICLES.keys())
    missing_teams = teams_needed - teams_found
    
    if missing_teams or not all_players:
        if missing_teams:
            print(f"\nScraping {len(missing_teams)} teams individually...")
        else:
            print(f"\nScraping all {len(TEAM_ARTICLES)} teams individually...")
        
        # Override TEAM_ARTICLES to only missing ones if main succeeded partially
        remaining = {k: v for k, v in TEAM_ARTICLES.items() if k in missing_teams} if missing_teams else TEAM_ARTICLES
        
        for team_name, article_title in remaining.items():
            print(f"  Fetching {team_name}...", end=" ", flush=True)
            html = get_wiki_page_html(article_title)
            
            if not html:
                print("[not found]")
                time.sleep(0.5)
                continue
            
            players = parse_squad_table(html, team_name)
            if players:
                all_players.extend(players)
                print(f"[OK] {len(players)} players")
            else:
                print("[page exists but no squad table found yet]")
            
            time.sleep(0.4)
    
    # Step 3: Save results
    print(f"\n{'=' * 60}")
    if all_players:
        output_file = "wc2026_squads.csv"
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = ['Nation', 'PlayerName', 'Position', 'Age', 'Club', 'ShirtNumber']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_players)
        
        from collections import Counter
        team_counts = Counter(p['Nation'] for p in all_players)
        
        print(f"SUCCESS: Saved {len(all_players)} players from {len(team_counts)} teams")
        print(f"Output file: {output_file}\n")
        print("Teams scraped:")
        for team, count in sorted(team_counts.items()):
            print(f"  {team}: {count} players")
    else:
        print("No data collected.")
        print("Wikipedia may not have the 2026 squad articles published yet.")
        print("In that case, the model will use EA FC 26 ratings as the squad quality source.")

if __name__ == "__main__":
    main()
