import urllib.request
import re
import json

u = 'https://docs.google.com/spreadsheets/d/12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU/htmlview'
req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

title = re.findall(r'<title>([^<]+)</title>', content)
tabs = re.findall(r'<li[^>]*id="sheet-button-([^"]+)"[^>]*><a[^>]*>([^<]+)</a>', content)

info = {
    'doc_title': title,
    'tabs': tabs
}
with open('C:/niji-uta/scratch/sheet_info.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

print("Saved sheet info!")
