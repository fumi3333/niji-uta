import urllib.request
import re
from bs4 import BeautifulSoup

url = "https://wikiwiki.jp/nijisanji/%E6%AD%8C%E5%94%B1%E3%81%BE%E3%81%A8%E3%82%81"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')

print("Page heading:", soup.find('h1'))
links = soup.find_all('a')
print("Total links:", len(links))

# ライバー別ページへのリンクやテーブル構造を調査
sub_links = []
for a in links:
    text = a.get_text().strip()
    href = a.get('href', '')
    if any(k in href or k in text for k in ['歌唱', '歌枠', '楽曲', '歌ってみた', 'あ行', 'か行', 'さ行']):
        sub_links.append((text, href))

print(f"Relevant links ({len(sub_links)}):")
for t, h in sub_links[:20]:
    print(f"  {t} -> {h}")
