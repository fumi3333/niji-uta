import os
import sys
import json
import csv
import io
import re
import urllib.request
import pykakasi

from artist_map import get_real_artist

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "..", "data")
LIVER_COLS_FILE = os.path.join(DATA_DIR, "all_liver_cols.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "song_performances.json")

kks = pykakasi.kakasi()

def to_hira(text):
    if not text: return ""
    return "".join([it['hira'] for it in kks.convert(str(text))])

def to_kana(text):
    if not text: return ""
    return "".join([it['kana'] for it in kks.convert(str(text))])

# 94名ライバーの愛称・ひらがな読み仮名マッピング
LIVER_KANA_MAP = {
    "甲斐田晴": "かいだはる",
    "緑仙": "りゅーしぇん りゅうしぇん りゅくせん",
    "弦月藤士郎": "げんづきとうしろう げんづき とうしろう",
    "ドーラ": "どーら",
    "長尾景": "ながおけい ながお けい",
    "シスタークレア": "しすたーくれあ くれあ",
    "ジョー・力一": "じょーりきいち りきいち じょー・りきいち",
    "レヴィ・エリファ": "れゔぃえりふぁ れびぃえりふぁ れゔぃ えりふぁ",
    "夢追翔": "ゆめおいかける ゆめおい かける",
    "童田明治": "わらべだめいじ わらべだ めいじ",
    "早瀬走": "はやせそう はやせ そう",
    "出雲霞": "いずもかすみ いずも かすみ",
    "轟京子": "とどろききょうこ とどろき きょうこ",
    "神田笑一": "かんだしょういち かんだ しょういち",
    "竜胆尊": "りんどうみこと りんどう みこと",
    "町田ちま": "まちたちま まちだちま まちた ちま",
    "葉加瀬冬雪": "はかせふゆき はかせ ふゆき",
    "鷹宮リオン": "たかみやりおん たかみや りおん",
    "山神カルタ": "やまがみかるた やまがみ かるた",
    "葉山舞鈴": "はやままりん はやま まりん",
    "相羽ういは": "あいばういは あいば ういは",
    "物述有栖": "もののべありす もののべ ありす",
    "鈴谷アキ": "すずやあき すずや あき",
    "勇気ちひろ": "ゆうきちひろ ゆうき ちひろ",
    "白雪巴": "しらゆきともえ しらゆき ともえ",
    "フレン・E・ルスタリオ": "ふれんいーるすたりお ふれん・いー・るすたりお ふれん",
    "星川サラ": "ほしかわさら ほしかわ さら",
    "家長むぎ": "いえながむぎ いえなが むぎ",
    "戌亥とこ": "いぬいとこ いぬい とこ",
    "三枝明那": "さえぐさあきな さえぐさ あきな",
    "飛鳥ひな": "あすかひな あすか ひな",
    "渋谷ハジメ": "しぶやはじめ しぶや はじめ",
    "鈴鹿詩子": "すずかうたこ すずか うたこ",
    "森中花咲": "もりなかかざき もりなか かざき",
    "剣持刀也": "けんもちとうや けんもち とうや けんもち",
    "雨森小夜": "あめもりさよ あめもり さよ",
    "月ノ美兎": "つきのみと つきの みと みと 委員長 いいんちょう",
    "雪城眞尋": "ゆきしろまひろ ゆきしろ まひろ",
    "健屋花那": "すこやかな すこや かな",
    "文野環": "ふみのたまき ふみの たまき のらねこ 野良猫",
    "宇志海いちご": "うしかみいちご うしかみ いちご",
    "メリッサ・キンレンカ": "めりっさきんれんか めりっさ きんれんか",
    "鈴原るる": "すずはらるる すずはら るる",
    "エリー・コニファー": "えりーこにふぁー えりー こにふぁー",
    "鈴木勝": "すずきまさる すずき まさる",
    "ラトナ・プティ": "らとなぷてぃ らとな ぷてぃ",
    "でびでび・でびる": "でびでびでびる でびる",
    "える": "える エル",
    "社築": "やしろきずく やしろ きずく やしきず",
    "加賀美ハヤト": "かがみはやと かがみ はやと 社長 しゃちょう",
    "御伽原江良": "おとぎばらえら おとぎばら えら ぎばら ギバラ",
    "ニュイ・ソシエール": "にゅいそしえーる にゅい そしえーる",
    "小野町春香": "おのまちはるか おのまち はるか",
    "瀬戸美夜子": "せとみやこ せと みやこ",
    "フミ": "ふみ フミ",
    "黒井しば": "くろいしば くろい しば",
    "桜凛月": "さくらりつき さくら りつき",
    "アンジュ・カトリーナ": "あんじゅかとりーな あんじゅ かとりーな アンジュ",
    "えま★おうがすと": "えまおうがすと えま",
    "笹木咲": "ささきさく ささき さく",
    "椎名唯華": "しいなゆいか しいな ゆいか しぃしぃ",
    "樋口楓": "ひぐちかえで ひぐち かえで でろーん デローン",
    "安土桃": "あづちもも あづち もも",
    "来栖夏芽": "くるすなつめ くるす なつめ",
    "舞元啓介": "まいもとけいすけ まいもと けいすけ まいもと",
    "リゼ・ヘルエスタ": "りぜへるえすた リゼ",
    "魔界ノりりむ": "まかいのりりむ りりむ",
    "シェリン・バーガンディ": "しぇりん・ばーがんでぃ しぇりん",
    "伏見ガク": "ふしみがく ふしみ がく",
    "本間ひまわり": "ほんまひまわり ひまちゃん",
    "夜見れな": "よるみれな",
    "ベルモンド・バンデラス": "べるもんどばんでらす べるもんど",
    "天宮こころ": "あまみやこころ あまみゃ",
    "郡道美玲": "ぐんどうみれい",
    "静凛": "しずかりん しずりん",
    "モイラ": "もいら",
    "叶": "かなえ カナエ かなかな",
    "不破湊": "ふわみなと ふわっち",
    "花畑チャイカ": "はなばたけちゃいか チャイカ",
    "夕陽リリ": "ゆうひりり",
    "葛葉": "くずは クズハ ずしり",
    "ましろ": "ましろ",
    "春崎エアル": "はるさきえある",
    "ルイス・キャミー": "るいすきゃみー",
    "赤羽葉子": "あかばねようこ",
    "夢月ロア": "ゆづきろあ ロア",
    "奈羅花": "ならか",
    "グウェル・オス・ガール": "ぐうぇるおすがーる ぐうぇる",
    "黛灰": "まゆずみかい まゆゆ"
}

def update_all_songs():
    print("Step 1: Loading Master spreadsheet...")
    master_url = 'https://docs.google.com/spreadsheets/d/1qYAZkLv1fF6SVasf125OzeS9GGfw5y8bnGqAUrsP6p0/gviz/tq?tqx=out:csv'
    req = urllib.request.Request(master_url, headers={'User-Agent': 'Mozilla/5.0'})
    content = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
    rows = list(csv.reader(io.StringIO(content)))

    with open(LIVER_COLS_FILE, 'r', encoding='utf-8') as f:
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

    print(f"Master records loaded: {len(all_records)}")

    # Step 2: Individual granular sheets
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
            s_content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf-8', errors='ignore')
            s_rows = list(csv.reader(io.StringIO(s_content)))
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
            print(f"Error loading {liver_name}: {e}")

    print(f"Added {added_count} records from individual sheets. Total: {len(all_records)}")

    # Step 3: Enrich with kana readings
    print("Step 3: Enriching with kana readings...")
    for r in all_records:
        t = r.get('title', '')
        ht = to_hira(t)
        kt = to_kana(t)
        r['kana_title'] = f"{ht} {kt}" if ht != t else ""

        a = r.get('artist', '')
        ha = to_hira(a)
        ka = to_kana(a)
        r['kana_artist'] = f"{ha} {ka}" if ha != a else ""

        l = r.get('liver', '')
        hl = to_hira(l)
        kl = to_kana(l)
        manual_l = LIVER_KANA_MAP.get(l, '')
        r['kana_liver'] = f"{manual_l} {hl} {kl}".strip()

    # Step 4: Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {len(all_records)} records to {OUTPUT_FILE}!")

if __name__ == '__main__':
    update_all_songs()
