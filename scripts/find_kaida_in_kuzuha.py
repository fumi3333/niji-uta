import urllib.request
import csv
import io
import json

sheet_id = "12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')

reader = csv.reader(io.StringIO(content))
rows = list(reader)

print(f"Total rows in Kuzuha sheet: {len(rows)}")

# 甲斐田晴を含む行を探す
kaida_rows = []
for i, r in enumerate(rows):
    line_str = " ".join(r)
    if "甲斐田" in line_str:
        kaida_rows.append((i, r[:8]))

print(f"Found {len(kaida_rows)} rows mentioning 甲斐田 in Kuzuha sheet:")
for idx, r in kaida_rows[:10]:
    print(f"  Row {idx}: {r}")
