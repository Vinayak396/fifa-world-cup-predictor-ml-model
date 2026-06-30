import re
with open('debug_wiki_html.txt', encoding='utf-8') as f:
    html = f.read()

heading_pattern = re.compile(r'<h([234])\s+id="([^"]*)"[^>]*>(.*?)</h\1>', re.DOTALL)
matches = list(heading_pattern.finditer(html))
print(f'Total headings: {len(matches)}')
for m in matches:
    level = m.group(1)
    hid = m.group(2)
    text = re.sub(r'<[^>]+>', '', m.group(3)).strip()
    text = re.sub(r'\[.*?\]', '', text).strip()
    print(f'  h{level} id={repr(hid):45} text={repr(text)}')
