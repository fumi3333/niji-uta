import urllib.request
import re
import json

def fetch_youtube_comments_and_desc(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    html = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")
    
    api_key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
    api_key = api_key_match.group(1) if api_key_match else None
    
    # Check description timestamps
    desc_match = re.search(r'"shortDescription":"(.*?)"', html)
    desc = desc_match.group(1) if desc_match else ""
    desc_ts = re.findall(r'(?:(?:(\d{1,2}):)?(\d{2}):(\d{2}))\s*([^\n\r\\"]+)', desc)
    
    print(f"Video {video_id}:")
    print(f" - Description TS count: {len(desc_ts)}")
    for t in desc_ts[:5]:
        print("   ", t)
        
    # Check comment continuation
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
        try:
            res_json = json.loads(urllib.request.urlopen(req2).read().decode("utf-8"))
            res_str = json.dumps(res_json, ensure_ascii=False)
            comment_ts = re.findall(r'(?:(?:(\d{1,2}):)?(\d{2}):(\d{2}))\s*([^\n\r\\"]{2,30})', res_str)
            print(f" - Comments TS count: {len(comment_ts)}")
            for c in comment_ts[:10]:
                print("   Comment TS:", c)
        except Exception as e:
            print(" - Error fetching comments:", e)

if __name__ == '__main__':
    # 甲斐田晴の歌枠
    fetch_youtube_comments_and_desc('kApOQDclLwM')
    # 戌亥とこの歌枠
    fetch_youtube_comments_and_desc('r4MFsbwKRRk')
