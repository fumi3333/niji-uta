import urllib.request
import re
import json

def check_video(vid, song_name):
    url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    html = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")
    
    t_m = re.search(r'<title>([^<]+)</title>', html)
    title = t_m.group(1).replace(" - YouTube", "") if t_m else ""
    
    api_key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
    api_key = api_key_match.group(1) if api_key_match else None
    
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
        try:
            res_json = json.loads(urllib.request.urlopen(req2).read().decode("utf-8"))
            all_text += " " + json.dumps(res_json, ensure_ascii=False)
        except Exception as e:
            pass
            
    # 曲名に関するセトリタイムスタンプ抽出
    matches = re.findall(r'((?:(?:\d{1,2}:)?\d{2}:\d{2}))[^\n\r\\"<]{0,30}' + re.escape(song_name), all_text, re.IGNORECASE)
    matches += re.findall(re.escape(song_name) + r'[^\n\r\\"<]{0,30}((?:(?:\d{1,2}:)?\d{2}:\d{2}))', all_text, re.IGNORECASE)
    
    print(f"Video: {vid} | Title: {title[:40]}")
    print(f"Song: {song_name} | Found TS in Comments/Desc: {list(set(matches))}")

if __name__ == '__main__':
    # 甲斐田晴 シャルル (qxU7b1mSwKE)
    check_video('qxU7b1mSwKE', 'シャルル')
    # 戌亥とこ シャルル (85CYfM79LdE)
    check_video('85CYfM79LdE', 'シャルル')
    # 剣持刀也 シャルル (OTqsCRVfFmQ)
    check_video('OTqsCRVfFmQ', 'シャルル')
