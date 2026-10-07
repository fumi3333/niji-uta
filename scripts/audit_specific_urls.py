import urllib.request
import json
import time

urls = [
    ('白日', '甲斐田晴', 'https://youtu.be/kApOQDclLwM?t=58m14s'),
    ('白日', '加賀美ハヤト', 'https://youtu.be/wf00EkpEahc'),
    ('白日', '戌亥とこ', 'https://youtu.be/r4MFsbwKRRk'),
    ('シャルル', '相羽ういは', 'https://youtu.be/288lEU1UGII'),
    ('シャルル', '剣持刀也', 'https://youtu.be/OTqsCRVfFmQ'),
    ('シャルル', 'ドーラ', 'https://youtu.be/vThdpiyaam4')
]

results = []
for title, liver, u in urls:
    clean_u = u.split('?')[0]
    oembed = f'https://www.youtube.com/oembed?url={clean_u}&format=json'
    try:
        content = urllib.request.urlopen(urllib.request.Request(oembed, headers={'User-Agent': 'Mozilla/5.0'}), timeout=5).read().decode('utf-8')
        d = json.loads(content)
        results.append({
            'song': title,
            'expected_liver': liver,
            'url': u,
            'actual_channel': d.get('author_name'),
            'video_title': d.get('title'),
            'status': 'MATCH' if liver in d.get('author_name', '') or liver in d.get('title', '') else 'DIFFERENT'
        })
    except Exception as e:
        results.append({
            'song': title,
            'expected_liver': liver,
            'url': u,
            'error': str(e),
            'status': 'ERROR'
        })
    time.sleep(0.3)

with open('C:/niji-uta/scratch/audit_hakujitsu_charles.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('Saved audit results!')
