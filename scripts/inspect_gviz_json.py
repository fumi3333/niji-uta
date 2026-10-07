import urllib.request
import json
import re

sheet_id = "1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# gviz json は /*O_o*/ google.visualization.Query.setResponse({...}); というラッパーがある
m = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', raw, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    cols = data.get("table", {}).get("cols", [])
    rows = data.get("table", {}).get("rows", [])
    print(f"Total rows in JSON: {len(rows)}")
    
    # 最初の数行のセルオブジェクトを調査（ハイパーリンクやリンクが含まれているか）
    for r_idx in range(min(10, len(rows))):
        c_list = rows[r_idx].get("c", [])
        links_in_row = []
        for c in c_list:
            if c:
                # v (値), f (フォーマット済み), l (リンク?)
                for k, v in c.items():
                    if 'http' in str(v):
                        links_in_row.append((k, v))
        if links_in_row:
            print(f"Row {r_idx} links:", links_in_row)
else:
    print("Could not match json wrapper")
