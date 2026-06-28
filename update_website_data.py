"""Auto-update website/js/data.js with all 72 group-stage results."""

# All 72 results keyed by fixture id (matching data.js)
# (homeScore, awayScore) — in the same home/away order as data.js
RESULTS = {
    # GROUP A
    1:  (2, 0),   # Mexico v South Africa
    2:  (2, 1),   # South Korea v Czech Republic
    28: (1, 0),   # Mexico v South Korea
    25: (1, 1),   # Czech Republic v South Africa
    53: (0, 3),   # Czech Republic v Mexico  (CZE 0-3 MEX)
    54: (1, 0),   # South Africa v South Korea
    # GROUP B
    3:  (1, 1),   # Canada v Bosnia
    8:  (1, 1),   # Qatar v Switzerland
    27: (6, 0),   # Canada v Qatar
    26: (4, 1),   # Switzerland v Bosnia
    51: (2, 1),   # Switzerland v Canada
    52: (3, 1),   # Bosnia v Qatar
    # GROUP C
    5:  (0, 1),   # Haiti v Scotland
    7:  (1, 1),   # Brazil v Morocco
    29: (3, 0),   # Brazil v Haiti
    30: (0, 1),   # Scotland v Morocco
    49: (0, 3),   # Scotland v Brazil
    50: (4, 2),   # Morocco v Haiti
    # GROUP D
    4:  (4, 1),   # USA v Paraguay
    6:  (2, 0),   # Australia v Turkey
    32: (2, 0),   # USA v Australia
    31: (0, 1),   # Turkey v Paraguay
    59: (3, 2),   # Turkey v USA
    60: (0, 0),   # Paraguay v Australia
    # GROUP E
    9:  (1, 0),   # Ivory Coast v Ecuador
    10: (7, 1),   # Germany v Curacao
    33: (2, 1),   # Germany v Ivory Coast
    34: (0, 0),   # Ecuador v Curacao
    56: (2, 1),   # Ecuador v Germany
    55: (0, 2),   # Curacao v Ivory Coast
    # GROUP F
    11: (2, 2),   # Netherlands v Japan
    12: (5, 1),   # Sweden v Tunisia
    35: (5, 1),   # Netherlands v Sweden
    36: (0, 4),   # Tunisia v Japan
    57: (1, 1),   # Japan v Sweden
    58: (1, 3),   # Tunisia v Netherlands
    # GROUP G
    15: (2, 2),   # Iran v New Zealand
    16: (1, 1),   # Belgium v Egypt
    39: (0, 0),   # Belgium v Iran
    40: (1, 3),   # New Zealand v Egypt
    63: (1, 1),   # Egypt v Iran
    64: (1, 5),   # New Zealand v Belgium
    # GROUP H
    13: (1, 1),   # Saudi Arabia v Uruguay
    14: (0, 0),   # Spain v Cape Verde
    37: (2, 2),   # Uruguay v Cape Verde
    38: (4, 0),   # Spain v Saudi Arabia
    65: (0, 0),   # Cape Verde v Saudi Arabia
    66: (0, 1),   # Uruguay v Spain
    # GROUP I
    17: (3, 1),   # France v Senegal
    18: (1, 4),   # Iraq v Norway
    42: (3, 0),   # France v Iraq
    41: (3, 2),   # Norway v Senegal
    61: (1, 4),   # Norway v France
    62: (5, 0),   # Senegal v Iraq
    # GROUP J
    19: (3, 0),   # Argentina v Algeria
    20: (3, 1),   # Austria v Jordan
    43: (2, 0),   # Argentina v Austria
    44: (1, 2),   # Jordan v Algeria
    70: (1, 3),   # Jordan v Argentina
    69: (3, 3),   # Algeria v Austria
    # GROUP K
    23: (1, 1),   # Portugal v DR Congo
    24: (1, 3),   # Uzbekistan v Colombia
    47: (5, 0),   # Portugal v Uzbekistan
    48: (1, 0),   # Colombia v DR Congo
    71: (0, 0),   # Colombia v Portugal
    72: (3, 1),   # DR Congo v Uzbekistan
    # GROUP L
    21: (1, 0),   # Ghana v Panama
    22: (4, 2),   # England v Croatia
    45: (0, 0),   # England v Ghana
    46: (0, 1),   # Panama v Croatia
    67: (0, 2),   # Panama v England
    68: (2, 1),   # Croatia v Ghana
}

# Pre-match probabilities (from original model run, kept for completed games)
PREMATCH = {
    1:  {"home":67.9,"draw":18.1,"away":14.0},
    2:  {"home":54.0,"draw":21.8,"away":24.2},
    3:  {"home":62.2,"draw":19.6,"away":18.2},
    4:  {"home":66.5,"draw":18.5,"away":15.0},
    5:  {"home":6.3, "draw":15.5,"away":78.2},
    6:  {"home":27.9,"draw":23.3,"away":48.8},
    7:  {"home":34.4,"draw":26.1,"away":39.5},
    8:  {"home":5.2, "draw":15.1,"away":79.7},
    9:  {"home":10.9,"draw":17.1,"away":72.0},
    10: {"home":83.0,"draw":14.3,"away":2.7},
    11: {"home":40.4,"draw":25.8,"away":33.8},
    12: {"home":28.8,"draw":23.7,"away":47.5},
    13: {"home":3.6, "draw":14.6,"away":81.8},
    14: {"home":81.0,"draw":14.8,"away":4.2},
    15: {"home":75.9,"draw":16.1,"away":8.0},
    16: {"home":61.4,"draw":19.8,"away":18.8},
    17: {"home":72.1,"draw":16.2,"away":11.7},
    18: {"home":4.1, "draw":13.3,"away":82.6},
    19: {"home":87.2,"draw":9.2, "away":3.6},
    20: {"home":55.3,"draw":22.1,"away":22.6},
    21: {"home":26.4,"draw":24.1,"away":49.5},
    22: {"home":63.4,"draw":19.8,"away":16.8},
    23: {"home":74.2,"draw":17.3,"away":8.5},
    24: {"home":18.9,"draw":22.4,"away":58.7},
    25: {"home":50.1,"draw":22.5,"away":27.4},
    26: {"home":72.9,"draw":17.1,"away":10.0},
    27: {"home":68.5,"draw":18.3,"away":13.2},
    28: {"home":68.7,"draw":17.5,"away":13.8},
    29: {"home":82.3,"draw":12.4,"away":5.3},
    30: {"home":32.6,"draw":23.1,"away":44.3},
    31: {"home":46.2,"draw":22.8,"away":31.0},
    32: {"home":71.4,"draw":16.3,"away":12.3},
    33: {"home":76.2,"draw":14.5,"away":9.3},
    34: {"home":55.1,"draw":21.4,"away":23.5},
    35: {"home":58.2,"draw":20.1,"away":21.7},
    36: {"home":14.8,"draw":19.7,"away":65.5},
    37: {"home":63.2,"draw":20.4,"away":16.4},
    38: {"home":85.3,"draw":10.5,"away":4.2},
    39: {"home":65.1,"draw":19.4,"away":15.5},
    40: {"home":7.3, "draw":16.8,"away":75.9},
    41: {"home":51.7,"draw":22.1,"away":26.2},
    42: {"home":87.4,"draw":9.1, "away":3.5},
    43: {"home":78.5,"draw":13.8,"away":7.7},
    44: {"home":32.2,"draw":24.1,"away":43.7},
    45: {"home":73.8,"draw":16.5,"away":9.7},
    46: {"home":21.4,"draw":22.6,"away":56.0},
    47: {"home":82.1,"draw":12.3,"away":5.6},
    48: {"home":59.4,"draw":20.8,"away":19.8},
    49: {"home":23.1,"draw":21.8,"away":55.1},
    50: {"home":68.7,"draw":18.2,"away":13.1},
    51: {"home":60.4,"draw":20.3,"away":19.3},
    52: {"home":28.3,"draw":23.1,"away":48.6},
    53: {"home":36.2,"draw":23.5,"away":40.3},
    54: {"home":27.8,"draw":23.6,"away":48.6},
    55: {"home":7.4, "draw":16.2,"away":76.4},
    56: {"home":16.3,"draw":20.5,"away":63.2},
    57: {"home":41.7,"draw":24.8,"away":33.5},
    58: {"home":10.2,"draw":17.1,"away":72.7},
    59: {"home":33.8,"draw":23.7,"away":42.5},
    60: {"home":21.6,"draw":23.9,"away":54.5},
    61: {"home":35.4,"draw":23.3,"away":41.3},
    62: {"home":77.6,"draw":14.8,"away":7.6},
    63: {"home":23.3,"draw":22.7,"away":54.0},
    64: {"home":9.8, "draw":16.9,"away":73.3},
    65: {"home":11.2,"draw":18.6,"away":70.2},
    66: {"home":11.6,"draw":18.3,"away":70.1},
    67: {"home":21.9,"draw":22.5,"away":55.6},
    68: {"home":45.3,"draw":23.9,"away":30.8},
    69: {"home":37.4,"draw":23.8,"away":38.8},
    70: {"home":11.5,"draw":18.2,"away":70.3},
    71: {"home":35.2,"draw":23.5,"away":41.3},
    72: {"home":41.8,"draw":24.1,"away":34.1},
}

# Read existing data.js
with open('website/js/data.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re

def fix_fixture(match):
    text = match.group(0)
    # Extract id
    id_m = re.search(r'\bid:(\d+)', text)
    if not id_m:
        return text
    fid = int(id_m.group(1))
    if fid not in RESULTS:
        return text
    hs, aws = RESULTS[fid]
    pm = PREMATCH.get(fid)
    # Remove any existing result/preMatchProbs
    text = re.sub(r',\s*result:\s*\{[^}]+\}', '', text)
    text = re.sub(r',\s*preMatchProbs:\s*\{[^}]+\}', '', text)
    # Build additions
    additions = f', result: {{ homeScore:{hs}, awayScore:{aws} }}'
    if pm:
        additions += f', preMatchProbs: {{ home:{pm["home"]}, draw:{pm["draw"]}, away:{pm["away"]} }}'
    # Insert before closing brace
    text = re.sub(r'\s*\}$', additions + ' }', text.rstrip())
    return text

# Match each fixture object
new_content = re.sub(r'\{[^{}]*\bid:\d+[^{}]*\}', fix_fixture, content)

with open('website/js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("data.js updated with all 72 results!")

# Count results added
count = sum(1 for fid in RESULTS if fid)
print(f"Results injected: {count}")
