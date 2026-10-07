import os
import json
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "..", "data")
DICT_PATH = os.path.join(DATA_DIR, "precise_artist_dict.json")

PRECISE_MAP = {}
if os.path.exists(DICT_PATH):
    with open(DICT_PATH, "r", encoding="utf-8") as f:
        PRECISE_MAP = json.load(f)

# 主要ボカロP・J-POP著名曲の確定的手動マッピング
MANUAL_MAP = {
    # ピノキオピー（キノピオピー）
    "神っぽいな": "ピノキオピー",
    "魔法少女とチョコレゐト": "ピノキオピー",
    "転生林檎": "ピノキオピー",
    "きみも悪い人でよかった": "ピノキオピー",
    "すろぉもぉしょん": "ピノキオピー",
    "すろぉもぉしょん (Cover)": "ピノキオピー",
    "腐れ外道とチョコレゐト": "ピノキオピー",
    "頓珍漢の宴": "ピノキオピー",
    "ねぇねぇねぇ。": "ピノキオピー",
    "ノンブレス・オブリージュ": "ピノキオピー",
    "ラヴィット": "ピノキオピー",
    "アッカンベーダ": "ピノキオピー",
    "ありふれたせかいせいふく": "ピノキオピー",
    "マッシュルームマザー": "ピノキオピー",
    "匿名M": "ピノキオピー",

    # 有名ボカロ曲
    "シャルル": "バルーン",
    "雨とペトラ": "バルーン",
    "花降らし": "バルーン",
    "レディーレ": "バルーン",
    "フォニイ": "ツミキ",
    "トウキョウ・シャンディ・ランデヴ": "ツミキ",
    "ヴァンパイア": "DECO*27",
    "乙女解剖": "DECO*27",
    "ヒバナ": "DECO*27",
    "ゴーストルール": "DECO*27",
    "愛言葉": "DECO*27",
    "愛言葉Ⅱ": "DECO*27",
    "愛言葉Ⅲ": "DECO*27",
    "愛言葉Ⅳ": "DECO*27",
    "妄想感傷代償連盟": "DECO*27",
    "おじゃま虫": "DECO*27",
    "アニマル": "DECO*27",
    "シンデレラ": "DECO*27",
    "二息歩行": "DECO*27",
    "モザイクロール": "DECO*27",
    "少女レイ": "みきとP",
    "ロキ": "みきとP",
    "いーあるふぁんくらぶ": "みきとP",
    "サリシノハラ": "みきとP",
    "ヨンジュウナナ": "みきとP",
    "心臓デモクラシー": "みきとP",
    "クノイチでも恋がしたい": "みきとP",
    "KING": "Kanaria",
    "QUEEN": "Kanaria",
    "エンヴィーベイビー": "Kanaria",
    "アイデンティティ": "Kanaria",
    "酔いどれ知らず": "Kanaria",
    "百鬼祭": "Kanaria",
    "グッバイ宣言": "Chinozo",
    "ショットガン・ナゴヤ": "Chinozo",
    "シェーマ": "Chinozo",
    "エリート": "Chinozo",
    "ジェラシス": "Chinozo",
    "チーズ": "Chinozo",
    "天ノ弱": "164",
    "残脈": "164",
    "shiningray": "164",
    "タイムマシン": "1640mP",
    "夜咄ディセイブ": "じん",
    "カゲロウデイズ": "じん",
    "サマータイムレコード": "じん",
    "ロスタイムメモリー": "じん",
    "アヤノの幸福理論": "じん",
    "アウターサイエンス": "じん",
    "チルドレンレコード": "じん",
    "ヘッドフォンアクター": "じん",
    "想像フォレスト": "じん",
    "空想フォレスト": "じん",
    "如月アテンション": "じん",
    "オツキミリサイタル": "じん",
    "夕景イエスタデイ": "じん",
    "ロストワンの号哭": "Neru",
    "東京テディベア": "Neru",
    "脱法ロック": "Neru",
    "再教育": "Neru",
    "ハウトゥー世界征服": "Neru",
    "い〜やい〜やい〜や": "Neru",
    "SNOBBISM": "Neru",
    "命に嫌われている。": "カンザキイオリ",
    "命に嫌われている": "カンザキイオリ",
    "あの夏が飽和する。": "カンザキイオリ",
    "死ぬのがいいわ": "藤井風",
    "ボッカデラベリタ": "柊キライ",
    "メビウス": "柊キライ",
    "オートファジー": "柊キライ",
    "エバ": "柊キライ",
    "ラブカ？": "柊キライ",
    "ヴィータ": "柊キライ",
    "風のゆくえ": "Ado",
    "ギラギラ": "Ado",
    "うっせぇわ": "Ado",
    "踊": "Ado",
    "レディメイド": "Ado",
    "夜のピエロ": "Ado",
    "阿修羅ちゃん": "Ado",
    "心という名の不可解": "Ado",
    "行方知れず": "Ado",
    "唱": "Ado",
    "クラクラ": "Ado",
    "ドライフラワー": "優里",
    "ベテルギウス": "優里",
    "シャッター": "優里",
    "レオ": "優里",
    "ビリミリオン": "優里",
    "Pretender": "Official髭男dism",
    "宿命": "Official髭男dism",
    "I LOVE...": "Official髭男dism",
    "115万キロのフィルム": "Official髭男dism",
    "ノーダウト": "Official髭男dism",
    "Stand By You": "Official髭男dism",
    "Cry Baby": "Official髭男dism",
    "ミックスナッツ": "Official髭男dism",
    "Subtitle": "Official髭男dism",
    "TATTOO": "Official髭男dism",
    "Chessboard": "Official髭男dism",
    "日常": "Official髭男dism",
    "ホワイトノイズ": "Official髭男dism",
    "白日": "King Gnu",
    "飛行艇": "King Gnu",
    "Teenager Forever": "King Gnu",
    "雨燦々": "King Gnu",
    "カメレオン": "King Gnu",
    "一途": "King Gnu",
    "逆夢": "King Gnu",
    "三文小説": "King Gnu",
    "SPECIALZ": "King Gnu",
    "Vinyl": "King Gnu",
    "どろん": "King Gnu",
    "傘": "King Gnu",
    "The hole": "King Gnu",
    "Prayer X": "King Gnu",
    "McDonald Romance": "King Gnu",
    "Tokyo Rendez-Vous": "King Gnu"
}

def get_real_artist(title, default_artist=""):
    clean_title = title.strip()
    # 1. 完全一致マニュアル
    if clean_title in MANUAL_MAP:
        return MANUAL_MAP[clean_title]
    # 2. 精密辞書
    if clean_title in PRECISE_MAP:
        return PRECISE_MAP[clean_title]
    # 3. 大文字小文字・部分一致
    for k, v in MANUAL_MAP.items():
        if k.lower() == clean_title.lower():
            return v
    # 4. default_artist が有効ならそれを返す
    if default_artist and default_artist not in ["VOCALOID", "ボカロ", "J-POP", "不明/ボカロP", "アニメ", "総合計"]:
        return default_artist
    return default_artist if default_artist else "ボカロP / 原作者"
