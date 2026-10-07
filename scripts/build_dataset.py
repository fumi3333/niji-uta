import urllib.request
import csv
import io
import json

print("Downloading and refining Nijisanji Song Sheet...")
sheet_id = "1qYAZkLv1fF6SVasf125OzeS9GGfw5y8bnGqAUrsP6p0"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

f = io.StringIO(content)
reader = csv.reader(f)
rows = list(reader)

header = rows[0]
ignore_headers = {"", "曲名", "ジャンルorアーティスト名", "回数", "計", "No.", "No"}

liver_columns = {}
for col_idx, col_name in enumerate(header):
    name = col_name.strip()
    if name and not name.isdigit() and len(name) > 1 and name not in ignore_headers:
        liver_columns[col_idx] = name

print(f"Refined {len(liver_columns)} valid liver names.")

songs = []
for row_idx, row in enumerate(rows[1:], start=1):
    if len(row) < 3:
        continue
    
    title = row[1].strip()
    artist = row[2].strip()
    count_str = row[3].strip() if len(row) > 3 else "1"
    
    if not title or title in ignore_headers:
        continue
        
    try:
        count = int(count_str) if count_str.isdigit() else 1
    except:
        count = 1
        
    sung_by = []
    for col_idx, liver_name in liver_columns.items():
        if col_idx < len(row):
            val = row[col_idx].strip()
            if val and val != "0" and val != "":
                sung_by.append(liver_name)
                
    main_liver = sung_by[0] if sung_by else "にじさんじ"
    yt_query = f"にじさんじ {main_liver} {title} 歌枠"
    
    songs.append({
        "id": row_idx,
        "title": title,
        "artist": artist if artist else "ボカロ/J-POP",
        "count": count,
        "livers": sung_by,
        "youtube_url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(yt_query)}"
    })

print(f"Generated {len(songs)} refined songs!")

import os
os.makedirs(r"C:\niji-uta\data", exist_ok=True)

with open(r"C:\niji-uta\data\songs.json", "w", encoding="utf-8") as out:
    json.dump(songs, out, ensure_ascii=False, indent=2)

print("Saved cleanly to C:\\niji-uta\\data\\songs.json")
