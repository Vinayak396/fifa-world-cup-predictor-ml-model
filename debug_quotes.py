import re
with open('debug_wiki_html.txt', encoding='utf-8') as f:
    html = f.read()

# Check quote style around Spain heading
spain_pos = html.find('id=')
# Find the Spain heading specifically  
idx = html.find('<h3')
while idx != -1:
    end = html.find('</h3>', idx)
    chunk = html[idx:end+5]
    if 'Spain' in chunk and 'id=' in chunk:
        print(repr(chunk[:200]))
        break
    idx = html.find('<h3', idx+1)

# Try both quote styles
p1 = re.compile(r'<h([234])\s+id="([^"]*)"[^>]*>(.*?)</h\1>', re.DOTALL)
p2 = re.compile(r"<h([234])\s+id='([^']*)'[^>]*>(.*?)</h\1>", re.DOTALL)
p3 = re.compile(r'<h([234])[^>]+id=["\']([^"\']+)["\'][^>]*>(.*?)</h\1>', re.DOTALL)

m1 = list(p1.finditer(html))
m2 = list(p2.finditer(html))
m3 = list(p3.finditer(html))
print(f'\nDouble-quote pattern matches: {len(m1)}')
print(f'Single-quote pattern matches: {len(m2)}')
print(f'Either-quote pattern matches: {len(m3)}')
