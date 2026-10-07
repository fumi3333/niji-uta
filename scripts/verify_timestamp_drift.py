import json
import urllib.request
import re
import random

def parse_time_to_seconds(ts_str):
    """'88:16' や '1:28:16' や '58m14s' や '3496' を秒数(int)に変換"""
    if not ts_str: return None
    ts_str = str(ts_str).strip()
    
    # 秒数数値のみ
    if ts_str.isdigit():
        return int(ts_str)
        
    # m / s 形式 (例: 58m14s)
    m_ms = re.match(r'(?:(\d+)m)?(?:(\d+)s)?', ts_str)
    if m_ms and (m_ms.group(1) or m_ms.group(2)):
        mins = int(m_ms.group(1)) if m_ms.group(1) else 0
        secs = int(m_ms.group(2)) if m_ms.group(2) else 0
        return mins * 60 + secs

    # コロン区切り (例: 1:28:16 または 88:16)
    parts = ts_str.split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return None

def format_hms(total_seconds):
    """秒数を HH:MM:SS または MM:SS に統一フォーマット"""
    if total_seconds is None: return "歌い出し"
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

# 1. song_performances.json からタイムスタンプ持ちのレコードを抽出
with open("C:/niji-uta/data/song_performances.json", "r", encoding="utf-8") as f:
    songs = json.load(f)

exact_records = [s for s in songs if s['timestamp'] != '歌い出し' and 'youtu' in s['youtube_url']]
print(f"Total exact records available: {len(exact_records)}")

# ランダムに20件サンプリング
random.seed(42)
samples = random.sample(exact_records, 20)

audit_results = []
for r in samples:
    u = r['youtube_url']
    vid_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', u)
    if not vid_match: continue
    vid = vid_match.group(1)
    
    # DB側の秒数
    db_secs = parse_time_to_seconds(r['timestamp'])
    
    # URLクエリの秒数
    url_secs = None
    if 't=' in u:
        m_t = re.search(r't=([^&]+)', u)
        if m_t:
            url_secs = parse_time_to_seconds(m_t.group(1))
            
    # YouTubeの実機データ（概要欄・コメント）を取得
    yt_url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(yt_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    yt_title = ""
    yt_channel = ""
    yt_timestamps_for_song = []
    
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
        t_m = re.search(r'<title>([^<]+)</title>', html)
        yt_title = t_m.group(1).replace(" - YouTube", "") if t_m else ""
        
        # 概要欄テキスト
        desc_match = re.search(r'"shortDescription":"(.*?)"', html)
        desc = desc_match.group(1) if desc_match else ""
        all_text = desc.replace('\\n', '\n')
        
        # コメント欄
        api_key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
        api_key = api_key_match.group(1) if api_key_match else None
        cont_matches = re.findall(r'"continuationCommand":{"token":"([^"]+)"', html)
        
        if cont_matches and api_key:
            post_data = json.dumps({
                "context": {"client": {"clientName": "WEB", "clientVersion": "2.20230522.01.00"}},
                "continuation": cont_matches[0]
            }).encode("utf-8")
            req2 = urllib.request.Request(
                f"https://www.youtube.com/youtubei/v1/next?key={api_key}",
                data=post_data,
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            res_json = json.loads(urllib.request.urlopen(req2, timeout=10).read().decode("utf-8"))
            all_text += "\n" + json.dumps(res_json, ensure_ascii=False)
            
        # 曲名に関連するタイムスタンプ行を探す
        song_kw = r['title'].replace(" ", "").replace("　", "")
        # 1行ずつ走査
        for line in all_text.splitlines():
            clean_line = line.replace(" ", "").replace("　", "")
            if song_kw in clean_line and (":" in line or "：" in line):
                ts_m = re.search(r'((?:\d{1,2}:)?\d{2}:\d{2})', line)
                if ts_m:
                    found_sec = parse_time_to_seconds(ts_m.group(1))
                    if found_sec is not None:
                        yt_timestamps_for_song.append({
                            "raw_text": line.strip()[:60],
                            "parsed_hms": format_hms(found_sec),
                            "seconds": found_sec
                        })
    except Exception as e:
        yt_title = f"Fetch Error: {e}"

    # 判定
    is_exact = False
    diff_seconds = None
    matched_source = None
    
    # 1. URLクエリとDB秒数の比較
    if url_secs is not None and db_secs is not None:
        if abs(url_secs - db_secs) <= 5: # 5秒以内の微差
            is_exact = True
            diff_seconds = abs(url_secs - db_secs)
            matched_source = f"URL_PARAM ({url_secs}s)"
            
    # 2. 実機セトリとの比較
    if yt_timestamps_for_song and db_secs is not None:
        for item in yt_timestamps_for_song:
            diff = abs(item['seconds'] - db_secs)
            if diff <= 10: # 10秒以内（イントロ/歌い出しの数秒差）
                is_exact = True
                diff_seconds = diff
                matched_source = f"SETLIST ({item['parsed_hms']})"
                break

    audit_results.append({
        "song": r['title'],
        "artist": r['artist'],
        "liver": r['liver'],
        "db_timestamp": r['timestamp'],
        "db_seconds": db_secs,
        "formatted_hms": format_hms(db_secs),
        "url_seconds": url_secs,
        "yt_title": yt_title,
        "setlist_found": yt_timestamps_for_song,
        "matched_source": matched_source,
        "diff_seconds": diff_seconds,
        "judgment": "PERFECT_MATCH" if diff_seconds == 0 else ("MINOR_DIFF_OK" if diff_seconds and diff_seconds <= 10 else ("URL_PARAM_MATCH" if is_exact else "NO_SETLIST_VERIFIED"))
    })

with open("C:/niji-uta/scratch/batch_timestamp_audit_20.json", "w", encoding="utf-8") as out:
    json.dump(audit_results, out, ensure_ascii=False, indent=2)

print("Batch audit completed!")
for a in audit_results:
    print(f"[{a['song']} - {a['liver']}] DB: {a['db_timestamp']} ({a['formatted_hms']}) | YT: {a['matched_source']} | Diff: {a['diff_seconds']}s -> {a['judgment']}")
