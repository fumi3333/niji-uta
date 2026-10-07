import urllib.request
import csv
import io
import json
import re

from artist_map import get_real_artist

# 主要ライバーのスプレッドシート一覧
LIVER_SHEETS = [
    {"name": "戌亥とこ", "id": "1Ghag7roXXCgbSxANy20R4_0SNDXTRePMIfXc5XcEDJw", "format": "inui"},
    {"name": "葛葉", "id": "12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU", "format": "multi_url"},
    {"name": "加賀美ハヤト", "id": "1KXXCBlVy4bV-eCdiyNko_aJSsQE8VxPIhIJkQNqYbDs", "format": "multi_url"},
    {"name": "剣持刀也", "id": "12wcpxh0UkIbgGt0DBU-9wgj3kc-_bJ764ABrZHbOj6U", "format": "multi_url"},
    {"name": "町田ちま", "id": "1LI71UN_Wc6t3FJkwdNt2bTgutQb3bHMjxnrdsjs-5a8", "format": "chima"},
    {"name": "ドーラ", "id": "1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A", "format": "dora"}
]

all_records = []
record_id = 1

def parse_time_str(ts_str):
    if not ts_str:
        return ""
    # t=47m18s or t=710s or 0:11:05
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
    return ts_str

for liver in LIVER_SHEETS:
    name = liver["name"]
    sid = liver["id"]
    fmt = liver["format"]
    print(f"Fetching sheet for {name} ({sid})...")
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv"
        content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        print(f"[{name}] rows: {len(rows)}")

        if fmt == "inui":
            # 戌亥とこ形式: [No, 日付, 形態, 配信名, ..., 曲名, アーティスト, URL]
            for r in rows[1:]:
                # URLセルを探す
                yt_urls = [c.strip() for c in r if 'youtu' in c]
                if not yt_urls:
                    continue
                date = r[1].strip() if len(r) > 1 else ""
                title = r[5].strip() if len(r) > 5 else ""
                raw_artist = r[6].strip() if len(r) > 6 else ""
                
                # 行から曲名を見つける（5列目付近）
                if not title and len(r) > 4:
                    title = r[4].strip()
                if not title:
                    continue
                    
                artist = get_real_artist(title, raw_artist)
                for u in yt_urls:
                    ts = parse_time_str(u)
                    all_records.append({
                        "id": record_id,
                        "title": title,
                        "artist": artist,
                        "liver": name,
                        "date": date if date else "アーカイブ",
                        "timestamp": ts if ts else "歌い出し",
                        "youtube_url": u
                    })
                    record_id += 1

        elif fmt == "multi_url":
            # 葛葉 / 加賀美ハヤト形式: [No, 曲名, アーティスト, URL1, URL2, URL3...]
            for r in rows:
                yt_urls = [c.strip() for c in r if 'youtu' in c]
                if not yt_urls:
                    continue
                title = ""
                raw_artist = ""
                # 通常は2列目か3列目に曲名
                for c in r[:4]:
                    val = c.strip()
                    if val and not val.isdigit() and 'youtu' not in val and len(val) > 1 and "曲名" not in val and "URL" not in val:
                        if not title:
                            title = val
                        elif not raw_artist:
                            raw_artist = val
                            
                if not title:
                    continue
                artist = get_real_artist(title, raw_artist)
                for u in yt_urls:
                    ts = parse_time_str(u)
                    all_records.append({
                        "id": record_id,
                        "title": title,
                        "artist": artist,
                        "liver": name,
                        "date": "歌枠アーカイブ",
                        "timestamp": ts if ts else "歌い出し",
                        "youtube_url": u
                    })
                    record_id += 1

        elif fmt == "dora":
            # ドーラ形式
            current_date = ""
            current_title = ""
            for r in rows[1:]:
                if len(r) < 5: continue
                if r[1].strip(): current_date = r[1].strip()
                if r[2].strip(): current_title = r[2].strip()
                ts_val = r[3].strip()
                song_val = r[4].strip()
                if ts_val and song_val and song_val != "曲名":
                    artist = get_real_artist(song_val, "ボカロ/J-POP")
                    # タイムスタンプ秒数化
                    pts = ts_val.split(":")
                    sec = 0
                    if len(pts) == 3: sec = int(pts[0])*3600 + int(pts[1])*60 + int(pts[2])
                    elif len(pts) == 2: sec = int(pts[0])*60 + int(pts[1])
                    
                    # ドーラの歌枠検索直飛び（または動画リンク）
                    u = f"https://www.youtube.com/results?search_query=にじさんじ+ドーラ+{urllib.parse.quote(song_val)}"
                    all_records.append({
                        "id": record_id,
                        "title": song_val,
                        "artist": artist,
                        "liver": name,
                        "date": current_date if current_date else "歌枠アーカイブ",
                        "timestamp": ts_val,
                        "youtube_url": u
                    })
                    record_id += 1

    except Exception as e:
        print(f"Error parsing {name}: {e}")

print(f"Total detailed records created: {len(all_records)}")

# シャルルのレコード数を確認
charles_records = [r for r in all_records if "シャルル" in r["title"]]
print(f"Charles records count: {len(charles_records)}")
for cr in charles_records:
    print(f"  {cr['title']} | {cr['artist']} | {cr['liver']} | {cr['date']} | {cr['timestamp']} | {cr['youtube_url']}")

with open(r"C:\niji-uta\data\song_performances.json", "w", encoding="utf-8") as out:
    json.dump(all_records, out, ensure_ascii=False, indent=2)

print("Saved to C:\\niji-uta\\data\\song_performances.json")
