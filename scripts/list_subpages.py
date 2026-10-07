import urllib.request
from bs4 import BeautifulSoup

url = 'https://wikiwiki.jp/nijisanji/%E6%AD%8C%E5%94%B1%E3%81%BE%E3%81%A8%E3%82%81'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')
sub_pages = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    if '/nijisanji/' in href and '歌唱まとめ' in href:
        sub_pages.append((a.get_text().strip(), href))

print(f"Total sub pages: {len(sub_pages)}")
for t, h in set(sub_pages):
    print(t, "->", h)
