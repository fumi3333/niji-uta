import urllib.request
import re
from bs4 import BeautifulSoup

url = "https://wikiwiki.jp/nijisanji/%E6%AD%8C%E5%94%B1%E3%81%BE%E3%81%A8%E3%82%81"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')

sheets = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    text = a.get_text().strip()
    if 'docs.google.com/spreadsheets' in href:
        # シートIDを抽出
        m = re.search(r'/d/([a-zA-Z0-9_-]+)', href)
        sheet_id = m.group(1) if m else ''
        parent_text = a.parent.get_text().strip() if a.parent else ''
        sheets.append({
            'text': text,
            'href': href,
            'sheet_id': sheet_id,
            'context': parent_text[:80]
        })

print(f"Total Google Sheets found: {len(sheets)}")
import json
with open(r"C:\niji-uta\data_sheets_list.json", "w", encoding="utf-8") as f:
    json.dump(sheets, f, ensure_ascii=False, indent=2)

for s in sheets[:10]:
    print(s['sheet_id'], "->", s['context'])
