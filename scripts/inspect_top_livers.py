import urllib.request
import csv
import io
import json

sheets = {
    "町田ちま": "1LI71UN_Wc6t3FJkwdNt2bTgutQb3bHMjxnrdsjs-5a8",
    "葛葉": "12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU",
    "戌亥とこ": "1Ghag7roXXCgbSxANy20R4_0SNDXTRePMIfXc5XcEDJw"
}

summary = {}
for name, sid in sheets.items():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv"
        content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        summary[name] = {
            "total_rows": len(rows),
            "header": rows[0] if rows else [],
            "sample_row": rows[1] if len(rows) > 1 else []
        }
    except Exception as e:
        summary[name] = {"error": str(e)}

with open(r"C:\niji-uta\sheets_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("Saved sheets_summary.json")
