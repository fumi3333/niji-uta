import urllib.request
import re

sheet_id = "1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# シート名を探す
matches = re.findall(r'name:\s*\"([^\"]+)\",\s*sheetId:\s*([0-9]+)', html)
print("Found sheets:", matches)
if not matches:
    # 別のパターン
    matches2 = re.findall(r'\"([^\"]+)\",\d+,\d+,\d+,\d+,\"[^\"]*\",null,null,null,null,null,\[\"([0-9]+)\"\]', html)
    print("Matches 2:", matches2[:10])
