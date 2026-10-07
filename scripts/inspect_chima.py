import urllib.request
import csv
import io

sheet_id = "1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

f = io.StringIO(content)
reader = csv.reader(f)
rows = list(reader)

print(f"Total rows in Machita Chima sheet: {len(rows)}")
for i, r in enumerate(rows[:10]):
    print(f"Row {i}: {r[:8]}")
