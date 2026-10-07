import urllib.request
import re
import json

vid = 'qxU7b1mSwKE'
url = f'https://www.youtube.com/watch?v={vid}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
api_key = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html).group(1)
token = re.findall(r'"continuationCommand":{"token":"([^"]+)"', html)[0]
post_data = json.dumps({'context': {'client': {'clientName': 'WEB', 'clientVersion': '2.20230522.01.00'}}, 'continuation': token}).encode('utf-8')
req2 = urllib.request.Request(f'https://www.youtube.com/youtubei/v1/next?key={api_key}', data=post_data, headers={'Content-Type': 'application/json'})
res_json = json.loads(urllib.request.urlopen(req2).read().decode('utf-8'))
with open('C:/niji-uta/scratch/kaida_comment_raw.json', 'w', encoding='utf-8') as f:
    json.dump(res_json, f, ensure_ascii=False, indent=2)
print('Saved raw comment json!')
