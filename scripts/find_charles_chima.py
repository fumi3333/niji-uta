import urllib.request
import csv
import io
import json

sheet_id = "1LI71UN_Wc6t3FJkwdNt2bTgutQb3bHMjxnrdsjs-5a8"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')

reader = csv.reader(io.StringIO(content))
rows = list(reader)

print(f"Total rows in Machita Chima sheet: {len(rows)}")
header = rows[0]
print(f"Header length: {len(header)}")

# シャルルを探す
charles_rows = [r for r in rows if "シャルル" in r[3] or "シャルル" in " ".join(r[:5])]
print(f"Found {len(charles_rows)} Charles rows in Chima sheet:")
for cr in charles_rows:
    non_empty = [(header[idx] if idx < len(header) else str(idx), val) for idx, val in enumerate(cr) if val.strip()]
    print(non_empty[:10])
