import urllib.request
import csv
import io

sheet_ids = {
    "戌亥とこ": "1Ghag7roXXCgbSxANy20R4_0SNDXTRePMIfXc5XcEDJw",
    "葛葉": "12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU",
    "加賀美ハヤト": "1KXXCBlVy4bV-eCdiyNko_aJSsQE8VxPIhIJkQNqYbDs"
}

for name, sid in sheet_ids.items():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv"
        content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        matches = [r for r in rows if any("シャルル" in cell for cell in r)]
        print(f"[{name}] Total rows: {len(rows)}, Charles matches: {len(matches)}")
        for m in matches[:2]:
            print("  ", [(idx, val) for idx, val in enumerate(m[:8]) if val.strip()])
    except Exception as e:
        print(f"[{name}] error: {e}")
