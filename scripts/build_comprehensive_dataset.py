import urllib.request
import json
import csv
import io
import re

from artist_map import get_real_artist

print("Rebuilding ultimate song dataset with PinocchioP and thousands of accurate artists...")

# 1. マスターシート (9,358件)
master_url = 'https://docs.google.com/spreadsheets/d/1qYAZkLv1fF6SVasf125OzeS9GGfw5y8bnGqAUrsP6p0/gviz/tq?tqx=out:csv'
rows = list(csv.reader(io.StringIO(urllib.request.urlopen(urllib.request.Request(master_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore'))))
with open('C:/niji-uta/scratch/all_liver_cols.json', 'r', encoding='utf-8') as f:
    liver_cols = json.load(f)

all_records = []
rec_id = 1

for r in rows[1:]:
    if len(r) < 3: continue
    title = r[1].strip()
    raw_artist = r[2].strip()
    if not title: continue
    artist = get_real_artist(title, raw_artist)
    for idx_s, liver_name in liver_cols.items():
        idx = int(idx_s)
        if idx < len(r) and r[idx].strip():
            val = r[idx].strip()
            urls = [u.strip() for u in val.split() if any(k in u for k in ['youtu', 'nicovideo', 'bilibili', 'twitcasting'])]
            for u in urls:
                all_records.append({
                    'id': rec_id,
                    'title': title,
                    'artist': artist,
                    'liver': liver_name,
                    'date': '歌枠アーカイブ',
                    'timestamp': '歌い出し',
                    'youtube_url': u
                })
                rec_id += 1

print('Master records loaded:', len(all_records))

# 個別シートから最新曲（神っぽいな等のボカロ最新曲）を追加
individual_sheets = [
    ('1KXXCBlVy4bV-eCdiyNko_aJSsQE8VxPIhIJkQNqYbDs', '弦月藤士郎'),
    ('12CwwvYKcp0ZiByRGclPVL1OfK_daUwckbv5j7Nf6puU', '甲斐田晴'),
    ('12-JFD94eh5G80EK1wPPn3MCCP_3ANXr3tHJ5sBvAIos', '長尾景'),
    ('1Ghag7roXXCgbSxANy20R4_0SNDXTRePMIfXc5XcEDJw', '夢追翔')
]

existing_pairs = set((r['title'], r['liver'], r['youtube_url'].split('?')[0]) for r in all_records)

added_count = 0
for sid, liver_name in individual_sheets:
    try:
        url = f'https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv'
        s_rows = list(csv.reader(io.StringIO(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', errors='ignore'))))
        for r in s_rows:
            urls = [c.strip() for c in r if any(k in c for k in ['youtu', 'nicovideo', 'twitcasting'])]
            if not urls: continue
            song_title = ''
            raw_art = ''
            for c in r[:5]:
                val = c.strip()
                if val and not val.isdigit() and 'youtu' not in val and 'URL' not in val and '曲名' not in val and len(val)>1:
                    if not song_title: song_title = val
                    elif not raw_art: raw_art = val
            if not song_title: continue
            art = get_real_artist(song_title, raw_art)
            for u in urls:
                key = (song_title, liver_name, u.split('?')[0])
                if key not in existing_pairs:
                    ts = '歌い出し'
                    if 't=' in u:
                        m_min = re.search(r't=(?:(\d+)m)?(?:(\d+)s)?', u)
                        if m_min and (m_min.group(1) or m_min.group(2)):
                            mins = int(m_min.group(1)) if m_min.group(1) else 0
                            secs = int(m_min.group(2)) if m_min.group(2) else 0
                            tot = mins * 60 + secs
                            ts = f"{tot//60:02d}:{tot%60:02d}"
                        else:
                            m_num = re.search(r't=(\d+)', u)
                            if m_num:
                                tot = int(m_num.group(1))
                                ts = f"{tot//60:02d}:{tot%60:02d}"
                    all_records.append({
                        'id': rec_id,
                        'title': song_title,
                        'artist': art,
                        'liver': liver_name,
                        'date': '配信アーカイブ',
                        'timestamp': ts,
                        'youtube_url': u
                    })
                    rec_id += 1
                    existing_pairs.add(key)
                    added_count += 1
    except Exception as e:
        print(f'Error adding {liver_name}: {e}')

print(f'Added {added_count} new granular records from individual sheets!')
print('Total combined records:', len(all_records))

# ピノキオピーの曲数確認
pin_records = [r for r in all_records if 'ピノキオ' in r['artist']]
print(f'PinocchioP records count: {len(pin_records)}')

with open('C:/niji-uta/data/song_performances.json', 'w', encoding='utf-8') as out:
    json.dump(all_records, out, ensure_ascii=False, indent=2)

print('Saved all records to song_performances.json!')
