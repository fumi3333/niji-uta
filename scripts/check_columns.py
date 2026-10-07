import urllib.request
import csv
import io
import json

sheet_id = "1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

f = io.StringIO(content)
reader = csv.reader(f)
rows = list(reader)

results = []
for i in range(min(20, len(rows))):
    non_empty = [(col_idx, val) for col_idx, val in enumerate(rows[i]) if val.strip()]
    results.append({
        "row": i,
        "items": non_empty
    })

with open(r"C:\niji-uta\cols_clean.json", "w", encoding="utf-8") as out:
    json.dump(results, out, ensure_ascii=False, indent=2)

print("Saved cols_clean.json")
