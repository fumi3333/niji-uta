import urllib.request
import json
import csv
import io
import re

from artist_map import get_real_artist

print("Building ultimate, accurate song performances dataset from official master summary...")

master_url = "https://docs.google.com/spreadsheets/d/1qYAZkLv1fF6SVasf125OzeS9GGfw5y8bnGqAUrsP6p0/gviz/tq?tqx=out:csv"
req = urllib.request.Request(master_url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
rows = list(csv.reader(io.StringIO(content)))

header = rows[0]
liver_columns = {}
for idx, col in enumerate(header):
    c = col.strip()
    if c and not c.isdigit() and c not in ['曲名', 'ジャンルorアーティスト名', '形態', '備考', '総合計', '総計', '五十音']:
        liver_columns[idx] = c

print(f"Mapped {len(liver_columns)} livers across header columns.")

# 個別歌唱タイムスタンプを持つ詳細シート（ドーラ、甲斐田晴、弦月藤士郎、長尾景、夢追翔等）から
# 詳細タイムスタンプ辞書を作成: (曲名, ライバー) -> {"date": ..., "timestamp": ..., "url": ...}
detailed_timestamp_cache = {}

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
    parts = ts_str.split(':')
    if len(parts) == 3:
        return f"{int(parts[1]):02d}:{int(parts[2]):02d}"
    return ts_str

# 1. ドーラ詳細
print("Caching Dora timestamps...")
try:
    dora_url = "https://docs.google.com/spreadsheets/d/1soex7TClfo8nTZPeXjgfV34JEURL6hEDQThPs6evk9A/gviz/tq?tqx=out:csv"
    dora_rows = list(csv.reader(io.StringIO(urllib.request.urlopen(urllib.request.Request(dora_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore'))))
    cur_date = "2026/07/11"
    for r in dora_rows[1:]:
        if len(r) < 5: continue
        if r[1].strip(): cur_date = r[1].strip()
        ts_val = r[3].strip()
        song_val = r[4].strip()
        if ts_val and song_val and song_val != "曲名":
            key = (song_val, "ドーラ")
            if key not in detailed_timestamp_cache:
                detailed_timestamp_cache[key] = {
                    "date": cur_date,
                    "timestamp": parse_time_str(ts_val)
                }
except Exception as e:
    print(f"Error caching Dora: {e}")

# 2. 甲斐田晴詳細
print("Caching Kaida Haru timestamps...")
try:
    kaida_url = "https://docs.google.com/spreadsheets/d/12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU/gviz/tq?tqx=out:csv"
    kaida_rows = list(csv.reader(io.StringIO(urllib.request.urlopen(urllib.request.Request(kaida_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore'))))
    for r in kaida_rows[1:]:
        if len(r) < 4: continue
        song_val = r[2].strip()
        if not song_val or song_val == "曲名": continue
        yt_urls = [c.strip() for c in r[4:] if 'youtu' in c or 'twitcasting' in c]
        if yt_urls:
            ts = parse_time_str(yt_urls[0])
            detailed_timestamp_cache[(song_val, "甲斐田晴")] = {
                "date": "配信アーカイブ",
                "timestamp": ts if ts else "歌い出し",
                "url": yt_urls[0]
            }
except Exception as e:
    print(f"Error caching Kaida: {e}")

# 3. 夢追翔詳細
print("Caching Yumeoi timestamps...")
try:
    yumeoi_url = "https://docs.google.com/spreadsheets/d/1Ghag7roXXCgbSxANy20R4_0SNDXTRePMIfXc5XcEDJw/gviz/tq?tqx=out:csv"
    yumeoi_rows = list(csv.reader(io.StringIO(urllib.request.urlopen(urllib.request.Request(yumeoi_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore'))))
    for r in yumeoi_rows[2:]:
        if len(r) < 8: continue
        date_val = r[1].strip()
        song_val = r[5].strip()
        url_val = r[7].strip()
        if song_val and url_val:
            ts = parse_time_str(url_val)
            detailed_timestamp_cache[(song_val, "夢追翔")] = {
                "date": date_val if date_val else "配信アーカイブ",
                "timestamp": ts if ts else "歌い出し",
                "url": url_val
            }
except Exception as e:
    print(f"Error caching Yumeoi: {e}")

print(f"Total cached detailed timestamps: {len(detailed_timestamp_cache)}")

# 全行のレコード構築
all_records = []
rec_id = 1

for r in rows[1:]:
    if len(r) < 3: continue
    title = r[1].strip()
    raw_artist = r[2].strip()
    if not title: continue
    
    artist = get_real_artist(title, raw_artist)

    for idx, liver_name in liver_columns.items():
        if idx < len(r) and r[idx].strip():
            val = r[idx].strip()
            # 複数URLが入っている場合もある
            urls = [u.strip() for u in val.split() if any(k in u for k in ['youtu', 'nicovideo', 'bilibili', 'twitcasting'])]
            if not urls:
                continue

            cache_key = (title, liver_name)
            cached = detailed_timestamp_cache.get(cache_key)

            for u in urls:
                final_date = "歌枠アーカイブ"
                final_ts = "歌い出し"
                final_url = u

                # キャッシュがあれば優先
                if cached:
                    final_date = cached.get("date", final_date)
                    final_ts = cached.get("timestamp", final_ts)
                    if "t=" in cached.get("url", ""):
                        final_url = cached.get("url", final_url)
                
                # URLにt=が含まれていればパース
                url_ts = parse_time_str(u)
                if url_ts and url_ts != u:
                    final_ts = url_ts

                all_records.append({
                    "id": rec_id,
                    "title": title,
                    "artist": artist,
                    "liver": liver_name,
                    "date": final_date,
                    "timestamp": final_ts,
                    "youtube_url": final_url
                })
                rec_id += 1

print(f"Total structured song performance records: {len(all_records)}")

# 白日 と シャルル の検証
hakujitsu_recs = [r for r in all_records if r["title"] == "白日"]
charles_recs = [r for r in all_records if r["title"] == "シャルル"]
print(f"Hakujitsu total records: {len(hakujitsu_recs)} (Singers: {len(set(r['liver'] for r in hakujitsu_recs))})")
print(f"Charles total records: {len(charles_recs)} (Singers: {len(set(r['liver'] for r in charles_recs))})")

with open(r"C:\niji-uta\data\song_performances.json", "w", encoding="utf-8") as out:
    json.dump(all_records, out, ensure_ascii=False, indent=2)

print("Saved cleanly to C:\\niji-uta\\data\\song_performances.json!")
