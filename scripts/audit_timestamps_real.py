import json
import urllib.request
import re

# 1. song_performances.json からタイムスタンプがあるレコードを複数抽出
with open("C:/niji-uta/data/song_performances.json", "r", encoding="utf-8") as f:
    songs = json.load(f)

# タイムスタンプがあり、URLがあるレコードから人気曲・代表ライバーのものを抽出
target_samples = [
    # 白日
    [s for s in songs if s['title'] == '白日' and s['liver'] == '甲斐田晴' and s['timestamp'] != '歌い出し'],
    [s for s in songs if s['title'] == '白日' and s['liver'] == '戌亥とこ' and s['timestamp'] != '歌い出し'],
    [s for s in songs if s['title'] == '白日' and s['liver'] == '加賀美ハヤト' and s['timestamp'] != '歌い出し'],
    # シャルル
    [s for s in songs if s['title'] == 'シャルル' and s['liver'] == '戌亥とこ' and s['timestamp'] != '歌い出し'],
    [s for s in songs if s['title'] == 'シャルル' and s['liver'] == '葛葉' and s['timestamp'] != '歌い出し'],
    [s for s in songs if s['title'] == 'シャルル' and s['liver'] == 'ドーラ' and s['timestamp'] != '歌い出し'],
    # 神っぽいな
    [s for s in songs if s['title'] == '神っぽいな' and s['liver'] == '弦月藤士郎' and s['timestamp'] != '歌い出し'],
    [s for s in songs if s['title'] == '神っぽいな' and s['liver'] == '甲斐田晴' and s['timestamp'] != '歌い出し'],
]

records_to_audit = []
for group in target_samples:
    if group:
        records_to_audit.append(group[0])

print(f"Total audit targets: {len(records_to_audit)}")

# 2. 各動画のYouTubeコメント欄/概要欄を実際にスクレイピングして、その曲が何分何秒と書かれているかを突合
results = []
for r in records_to_audit:
    u = r['youtube_url']
    vid_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', u)
    if not vid_match:
        continue
    vid = vid_match.group(1)
    
    # URLパラメータのt秒数
    url_t = ""
    if 't=' in u:
        m_t = re.search(r't=([^&]+)', u)
        if m_t:
            url_t = m_t.group(1)
            
    # YouTubeからコメント・概要欄取得
    web_url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(web_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    found_matches = []
    video_title = ""
    channel_name = ""
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
        t_m = re.search(r'<title>([^<]+)</title>', html)
        video_title = t_m.group(1).replace(" - YouTube", "") if t_m else ""
        
        # Innertube APIでコメント・概要欄からタイムスタンプ付きセトリを探す
        api_key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
        api_key = api_key_match.group(1) if api_key_match else None
        
        # 概要欄
        desc_match = re.search(r'"shortDescription":"(.*?)"', html)
        desc = desc_match.group(1) if desc_match else ""
        
        all_text = desc
        
        cont_matches = re.findall(r'"continuationCommand":{"token":"([^"]+)"', html)
        if cont_matches and api_key:
            token = cont_matches[0]
            post_data = json.dumps({
                "context": {"client": {"clientName": "WEB", "clientVersion": "2.20230522.01.00"}},
                "continuation": token
            }).encode("utf-8")
            req2 = urllib.request.Request(
                f"https://www.youtube.com/youtubei/v1/next?key={api_key}",
                data=post_data,
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            res_json = json.loads(urllib.request.urlopen(req2, timeout=10).read().decode("utf-8"))
            all_text += " " + json.dumps(res_json, ensure_ascii=False)
            
        # 曲名に関連するタイムスタンプを探す
        # 例: 58:14 白日
        title_esc = re.escape(r['title'])
        # パターン: タイムスタンプ + 曲名、あるいは 曲名 + タイムスタンプ
        ts_patterns = re.findall(r'((?:(?:\d{1,2}:)?\d{2}:\d{2}))[^\n\r\\"]{0,20}' + title_esc, all_text, re.IGNORECASE)
        ts_patterns += re.findall(title_esc + r'[^\n\r\\"]{0,20}((?:(?:\d{1,2}:)?\d{2}:\d{2}))', all_text, re.IGNORECASE)
        
        found_matches = list(set(ts_patterns))
    except Exception as e:
        found_matches = [f"Error: {e}"]

    results.append({
        "song": r['title'],
        "liver": r['liver'],
        "recorded_timestamp": r['timestamp'],
        "url_param": url_t,
        "youtube_url": u,
        "video_title": video_title,
        "youtube_comment_timestamps": found_matches,
        "is_match": any(r['timestamp'] in m or m in r['timestamp'] for m in found_matches) if found_matches else "NO_SETLIST_FOUND"
    })

with open("C:/niji-uta/scratch/detailed_timestamp_audit.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Audit finished. Results:")
for res in results:
    print(f"[{res['song']} / {res['liver']}] Recorded: {res['recorded_timestamp']} | URL param: {res['url_param']} | YT Comment/Desc: {res['youtube_comment_timestamps']} | Match: {res['is_match']}")
