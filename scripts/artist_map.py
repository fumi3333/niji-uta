# ボカロ曲・有名曲の正確な本家アーティスト辞書
ARTIST_MAP = {
    "シャルル": "バルーン",
    "フォニイ": "ツミキ",
    "ヴァンパイア": "DECO*27",
    "少女レイ": "みきとP",
    "KING": "Kanaria",
    "神っぽいな": "ピノキオピー",
    "グッバイ宣言": "Chinozo",
    "ロキ": "みきとP",
    "天ノ弱": "164",
    "ヒバナ": "DECO*27",
    "乙女解剖": "DECO*27",
    "ゴーストルール": "DECO*27",
    "夜咄ディセイブ": "じん",
    "カゲロウデイズ": "じん",
    "ロストワンの号哭": "Neru",
    "東京テディベア": "Neru",
    "脱法ロック": "Neru",
    "命に嫌われている。": "カンザキイオリ",
    "命に嫌われている": "カンザキイオリ",
    "ボッカデラベリタ": "柊キライ",
    "メビウス": "柊キライ",
    "ギラギラ": "Ado",
    "うっせぇわ": "Ado",
    "踊": "Ado",
    "ドライフラワー": "優里",
    "Pretender": "Official髭男dism",
    "宿命": "Official髭男dism",
    "丸の内サディスティック": "椎名林檎",
    "歌うたいのバラッド": "斉藤和義",
    "怪物": "YOASOBI",
    "夜に駆ける": "YOASOBI",
    "群青": "YOASOBI",
    "アイドル": "YOASOBI",
    "残響散歌": "Aimer",
    "カタオモイ": "Aimer",
    "春を告げる": "yama",
    "点描の唄": "Mrs. GREEN APPLE",
    "青と夏": "Mrs. GREEN APPLE",
    "インフェルノ": "Mrs. GREEN APPLE",
    "ファンサ": "HoneyWorks",
    "金曜日のおはよう": "HoneyWorks",
    "可愛くてごめん": "HoneyWorks",
    "星間飛行": "ランカ・リー",
    "ライオン": "May'n / 中島愛",
    "紅蓮華": "LiSA",
    "炎": "LiSA",
    "crossing field": "LiSA",
    "God knows...": "涼宮ハルヒ (平野綾)",
    "God knows": "涼宮ハルヒ (平野綾)",
    "君の知らない物語": "supercell",
    "シュガーソングとビターステップ": "UNISON SQUARE GARDEN"
}

def get_real_artist(title, default_artist=""):
    for k, v in ARTIST_MAP.items():
        if k.lower() == title.lower() or k in title:
            return v
    if default_artist and default_artist not in ["VOCALOID", "ボカロ", "J-POP", "不明/ボカロP", "アニメ"]:
        return default_artist
    return default_artist if default_artist else "ボカロP / 原作者"
