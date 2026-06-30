import re
with open('debug_wiki_html.txt', encoding='utf-8') as f:
    html = f.read()

# Test the simple heading pattern
heading_pattern = re.compile(r'<h([234])[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', re.DOTALL)
matches = list(heading_pattern.finditer(html))
print(f'Total headings: {len(matches)}')
for m in matches[:25]:
    level = m.group(1)
    hid = m.group(2)
    text = re.sub(r'<[^>]+>', '', m.group(3)).strip()
    text = re.sub(r'\[.*?\]', '', text).strip()
    print(f'  h{level} id={repr(hid):40} text={repr(text)}')

# Now test table extraction for Mexico
mexico_idx = None
for m in matches:
    if 'Mexico' in m.group(2):
        mexico_idx = m.end()
        print(f'\nMexico heading ends at char {mexico_idx}')
        break

if mexico_idx:
    # Find next heading
    next_h = heading_pattern.search(html, mexico_idx)
    next_start = next_h.start() if next_h else len(html)
    section = html[mexico_idx:next_start]
    print(f'Section length: {len(section)} chars')
    
    # Find table
    table_m = re.search(r'<table[^>]*>(.*?)</table>', section, re.DOTALL)
    if table_m:
        print('Table found!')
        # Count rows
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_m.group(0), re.DOTALL)
        print(f'Rows: {len(rows)}')
        for row in rows[:5]:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            clean = [re.sub(r'<[^>]+>', ' ', c).strip() for c in cells]
            print(f'  cells: {clean[:5]}')
    else:
        print('No table found in section')
        print(f'Section start: {repr(section[:500])}')
