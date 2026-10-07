import urllib.request
import urllib.parse
import re

title = "【歌枠】土曜のお昼にまったり 𓂃˚✦₊˚ KARAOKE🎤STREAM【にじさんじ/ドーラ】"
url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(title)}"

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
video_ids = re.findall(r'\"videoId\":\"([a-zA-Z0-9_-]{11})\"', html)
print(f"Search results video IDs ({len(video_ids)}):", video_ids[:5])
if video_ids:
    top_id = video_ids[0]
    print(f"Top matched video: https://youtu.be/{top_id}")
    # タイムスタンプ 0:11:05 -> 秒数変換
    ts = "0:11:05"
    parts = list(map(int, ts.split(':')))
    sec = parts[0]*3600 + parts[1]*60 + parts[2]
    print(f"Timestamped URL: https://youtu.be/{top_id}?t={sec}s")
