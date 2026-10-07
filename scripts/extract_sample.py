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

sample = []
for i, r in enumerate(rows[:25]):
    sample.append({
        "row_idx": i,
        "cols": r[:10]
    })

with open(r"C:\niji-uta\sample_chima_rows.json", "w", encoding="utf-8") as out:
    json.dump(sample, out, ensure_ascii=False, indent=2)

print("Saved sample_chima_rows.json")
