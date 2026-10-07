import urllib.request
import urllib.parse
import csv
import io
import json
import re
import os

print("Fetching Dora歌枠 spreadsheet...")
sheet_id = "1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore')

reader = csv.reader(io.StringIO(content))
rows = list(reader)

print(f"Total rows: {len(rows)}")

# 配信タイトル -> 動画ID のキャッシュ辞書
video_cache = {
    "【歌枠】土曜のお昼にまったり 𓂃˚✦₊˚ KARAOKE🎤STREAM【にじさんじ/ドーラ】": "XSDkh7gX7zI",
    "【歌枠】ハロプロONLY 𓂃˚✦₊˚ KARAOKE🎤STREAM（ドレイクの趣味濃いめ）【にじさんじ/ドーラ】": "Mgk9ztwe-gs"
}

def resolve_video_id(title):
    if not title:
        return ""
    if title in video_cache:
        return video_cache[title]
    
    clean_title = title.split("【にじさんじ")[0].strip()
    query = f"にじさんじ ドーラ {clean_title}"
    try:
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        req = urllib.request.Request(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8', errors='ignore')
        m = re.search(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\"', html)
        if m:
            vid = m.group(1)
            video_cache[title] = vid
            return vid
    except Exception as e:
        print(f"Error resolving {title}: {e}")
    return ""

def parse_time_to_seconds(ts_str):
    if not ts_str:
        return 0
    ts_str = ts_str.strip().replace("：", ":")
    parts = ts_str.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except:
        pass
    return 0

# 各行を走査して歌唱データを抽出
dora_songs = []
current_date = ""
current_title = ""

for row in rows[1:]:
    if len(row) < 5:
        continue
    
    date_val = row[1].strip()
    title_val = row[2].strip()
    ts_val = row[3].strip()
    song_val = row[4].strip()
    
    if date_val:
        current_date = date_val
    if title_val:
        current_title = title_val
        
    if ts_val and song_val and song_val != "曲名":
        sec = parse_time_to_seconds(ts_val)
        vid = resolve_video_id(current_title) if current_title else ""
        
        if vid:
            yt_link = f"https://youtu.be/{vid}?t={sec}s"
            is_direct = True
        else:
            yt_link = f"https://www.youtube.com/results?search_query={urllib.parse.quote(f'にじさんじ ドーラ {song_val} 歌枠')}"
            is_direct = False
            
        dora_songs.append({
            "title": song_val,
            "artist": "歌枠アーカイブ",
            "count": 1,
            "date": current_date,
            "stream_title": current_title,
            "timestamp": ts_val,
            "timestamp_sec": sec,
            "is_direct_timestamp": is_direct,
            "livers": ["ドーラ"],
            "youtube_url": yt_link
        })

print(f"Extracted {len(dora_songs)} songs from Dora sheet! (Direct timestamp resolved: {sum(1 for s in dora_songs if s['is_direct_timestamp'])})")

# 既存の songs.json とマージ
with open(r"C:\niji-uta\data\songs.json", "r", encoding="utf-8") as f:
    main_songs = json.load(f)

# 統合リストを作成（IDを振り直し）
merged_songs = []
id_counter = 1

# まず直接秒数タイムスタンプ付きの歌枠データを先頭付近に配置
for s in dora_songs:
    s["id"] = id_counter
    id_counter += 1
    merged_songs.append(s)

for s in main_songs:
    s["id"] = id_counter
    s["date"] = s.get("date", "アーカイブ")
    s["is_direct_timestamp"] = False
    id_counter += 1
    merged_songs.append(s)

print(f"Total merged songs: {len(merged_songs)}")

with open(r"C:\niji-uta\data\songs.json", "w", encoding="utf-8") as f:
    json.dump(merged_songs, f, ensure_ascii=False, indent=2)

print("Updated data/songs.json successfully!")
