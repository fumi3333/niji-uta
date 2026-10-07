import urllib.request
import csv
import io
import json
import re

from artist_map import get_real_artist

print("Building accurate, granular song performances database...")

all_records = []
record_id = 1

KNOWN_LIVERS = [
    "甲斐田晴", "不破湊", "剣持刀也", "加賀美ハヤト", "葛葉", "叶", 
    "戌亥とこ", "町田ちま", "ドーラ", "緑仙", "星導ショウ", "鈴木勝"
]

def parse_time_str(ts_str):
    if not ts_str:
        return ""
    m = re.search(r't=(?:(\d+)m)?(?:(\d+)s)?', ts_str)
    if m:
        mins = int(m.group(1)) if m.group(1) else 0
        secs = int(m.group(2)) if m.group(2) else 0
        total = mins * 60 + secs
        return f"{total//60:02d}:{total%60:02d}"
    m_num = re.search(r't=(\d+)', ts_str)
    if m_num:
        total = int(m_num.group(1))
        return f"{total//60:02d}:{total%60:02d}"
    # 0:11:05
    parts = ts_str.split(':')
    if len(parts) == 3:
        return f"{int(parts[1]):02d}:{int(parts[2]):02d}"
    return ts_str

# 1. ドーラシート (日付完全フォワードフィル)
print("Processing Dora sheet...")
dora_url = "https://docs.google.com/spreadsheets/d/1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A/gviz/tq?tqx=out:csv"
content = urllib.request.urlopen(urllib.request.Request(dora_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')
rows = list(csv.reader(io.StringIO(content)))

current_date = "2026/07/11"
current_title = "土曜のお昼にまったり"

for r in rows[1:]:
    if len(r) < 5: continue
    date_val = r[1].strip()
    title_val = r[2].strip()
    ts_val = r[3].strip()
    song_val = r[4].strip()
    
    if date_val:
        current_date = date_val
    if title_val:
        current_title = title_val
        
    if ts_val and song_val and song_val != "曲名":
        artist = get_real_artist(song_val, "ボカロ/J-POP")
        ts = parse_time_str(ts_val)
        yt_search = f"https://www.youtube.com/results?search_query=にじさんじ+ドーラ+{urllib.parse.quote(song_val)}"
        all_records.append({
            "id": record_id,
            "title": song_val,
            "artist": artist,
            "liver": "ドーラ",
            "date": current_date, # 必ず日付が入る！
            "timestamp": ts,
            "youtube_url": yt_search
        })
        record_id += 1

print(f"Dora records: {len(all_records)}")

# 2. 戌亥とこシート
print("Processing Inui Toko sheet...")
inui_url = "https://docs.google.com/spreadsheets/d/1Ghag7roXXCgbSxANy20R4_0SNDXTRePMIfXc5XcEDJw/gviz/tq?tqx=out:csv"
content = urllib.request.urlopen(urllib.request.Request(inui_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')
rows = list(csv.reader(io.StringIO(content)))

for r in rows[1:]:
    yt_urls = [c.strip() for c in r if 'youtu' in c]
    if not yt_urls: continue
    date = r[1].strip() if len(r) > 1 else "アーカイブ"
    title = r[5].strip() if len(r) > 5 else (r[4].strip() if len(r) > 4 else "")
    raw_artist = r[6].strip() if len(r) > 6 else ""
    if not title or title == "曲名": continue
    
    artist = get_real_artist(title, raw_artist)
    for u in yt_urls:
        all_records.append({
            "id": record_id,
            "title": title,
            "artist": artist,
            "liver": "戌亥とこ",
            "date": date if date else "2018/10/07",
            "timestamp": parse_time_str(u),
            "youtube_url": u
        })
        record_id += 1

# 3. 男性ライバー横断シート (葛葉・甲斐田晴・加賀美ハヤト・不破湊・剣持刀也)
print("Processing Male Livers sheet with precise liver labeling...")
male_url = "https://docs.google.com/spreadsheets/d/12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU/gviz/tq?tqx=out:csv"
content = urllib.request.urlopen(urllib.request.Request(male_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')
rows = list(csv.reader(io.StringIO(content)))

for r in rows:
    yt_urls = [c.strip() for c in r if 'youtu' in c]
    if not yt_urls: continue
    
    title = ""
    raw_artist = ""
    detected_liver = "葛葉" # デフォルト
    
    # セルを精査して曲名・アーティスト・ライバー名を判定
    for c in r[:5]:
        val = c.strip()
        if not val or val.isdigit() or 'youtu' in val or "URL" in val or "曲名" in val:
            continue
            
        # ライバー名が含まれているか？
        matched_livers = [l for l in KNOWN_LIVERS if l in val]
        if matched_livers:
            detected_liver = matched_livers[0]
            if len(matched_livers) > 1:
                detected_liver = ", ".join(matched_livers)
        elif not title:
            title = val
        elif not raw_artist:
            raw_artist = val
            
    if not title: continue
    artist = get_real_artist(title, raw_artist)
    
    for u in yt_urls:
        all_records.append({
            "id": record_id,
            "title": title,
            "artist": artist,
            "liver": detected_liver, # 甲斐田晴なら「甲斐田晴」！
            "date": "配信アーカイブ",
            "timestamp": parse_time_str(u),
            "youtube_url": u
        })
        record_id += 1

print(f"Total processed records: {len(all_records)}")

# 甲斐田晴のレコード確認
kaida_records = [r for r in all_records if "甲斐田晴" in r["liver"]]
print(f"Kaida Haru records correctly labeled: {len(kaida_records)}")
for kr in kaida_records[:3]:
    print(f"  {kr['title']} | {kr['artist']} | {kr['liver']} | {kr['youtube_url']}")

# ドーラの日付確認
dora_sample = [r for r in all_records if r["liver"] == "ドーラ"][:3]
for dr in dora_sample:
    print(f"  Dora sample: {dr['title']} | {dr['date']} | {dr['timestamp']}")

with open(r"C:\niji-uta\data\song_performances.json", "w", encoding="utf-8") as out:
    json.dump(all_records, out, ensure_ascii=False, indent=2)

print("Saved cleanly to data/song_performances.json")
