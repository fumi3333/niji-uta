import urllib.request
import re
from bs4 import BeautifulSoup

url = 'https://wikiwiki.jp/nijisanji/%E6%AD%8C%E5%94%B1%E3%81%BE%E3%81%A8%E3%82%81/%E5%8B%95%E7%94%BB'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all('a')
yt_links = []
for a in links:
    href = a.get('href', '')
    if 'youtu' in href:
        yt_links.append((a.get_text().strip(), href))

print(f"Total YouTube links: {len(yt_links)}")
for t, h in yt_links[:10]:
    print(t, "->", h)
