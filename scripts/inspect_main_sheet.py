import urllib.request
import csv
import io

sheet_id = "1qYAZkLv1fF6SVasf125OzeS9GGfw5y8bnGqAUrsP6p0"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

f = io.StringIO(content)
reader = csv.reader(f)
rows = list(reader)

print(f"Total rows: {len(rows)}")
if rows:
    print("Header:", rows[0])
    for r in rows[1:6]:
        print("Row:", r[:8])
