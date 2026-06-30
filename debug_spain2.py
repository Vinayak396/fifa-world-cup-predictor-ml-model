import re
with open('debug_wiki_html.txt', encoding='utf-8') as f:
    html = f.read()

heading_pattern = re.compile(r'<h([234])\s+id="([^"]*)"[^>]*>(.*?)</h\1>', re.DOTALL)
headings = list(heading_pattern.finditer(html))

# Find Spain
spain_idx = None
for i, m in enumerate(headings):
    if m.group(2) == 'Spain':
        spain_idx = i
        spain_end = m.end()
        break

if spain_idx is not None:
    print(f'Spain heading at index {spain_idx}, html ends at char {spain_end}')
    next_heading_start = headings[spain_idx+1].start() if spain_idx+1 < len(headings) else len(html)
    section = html[spain_end:next_heading_start]
    print(f'Section length: {len(section)} chars')
    print(f'Section start: {repr(section[:300])}')
    
    # Find tables
    tables = re.findall(r'<table[^>]*>(.*?)</table>', section, re.DOTALL)
    print(f'\nTables found: {len(tables)}')
    for i, t in enumerate(tables):
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.DOTALL)
        print(f'  Table {i}: {len(rows)} rows, {len(t)} chars')
        # Show first data row
        for row in rows[:3]:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            clean = [re.sub(r'<[^>]+>', ' ', c).strip()[:30] for c in cells[:4]]
            print(f'    Row: {clean}')
else:
    print('Spain heading NOT found')
