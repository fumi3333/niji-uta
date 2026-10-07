import urllib.request
import re
import json

def inspect_full_comments(vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    html = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")
    
    t_m = re.search(r'<title>([^<]+)</title>', html)
    print("Video:", vid, t_m.group(1) if t_m else "")
    
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
        res_json = json.loads(urllib.request.urlopen(req2).read().decode("utf-8"))
        res_str = json.dumps(res_json, ensure_ascii=False)
        # すべてのタイムスタンプ行を抽出
        lines = re.findall(r'((?:(?:\d{1,2}:)?\d{2}:\d{2})\s*[^\n\r\\"<]{2,40})', res_str)
        print(f"Total TS lines found in comments: {len(lines)}")
        for l in lines[:15]:
            print("  ", l)

if __name__ == '__main__':
    print("--- 戌亥とこ シャルル (85CYfM79LdE) ---")
    inspect_full_comments('85CYfM79LdE')
    print("\n--- 剣持刀也 幻の歌うたい (OTqsCRVfFmQ) ---")
    inspect_full_comments('OTqsCRVfFmQ')
