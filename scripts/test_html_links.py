import urllib.request
import re

url = 'https://docs.google.com/spreadsheets/d/1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A/gviz/tq?tqx=out:html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

links = re.findall(r'href=[\"\'](https?://[^\"\']+)[\"\']', html)
print('Found links:', len(links))
for l in links[:10]:
    print(l)
