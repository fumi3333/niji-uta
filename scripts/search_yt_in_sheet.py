import urllib.request
import re

sheet_id = "1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# youtu.be や youtube.com のリンクが含まれているか？
yt_links = re.findall(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+', html)
print(f"Total YouTube links in HTML: {len(yt_links)}")
for y in set(yt_links)[:10]:
    print(y)
