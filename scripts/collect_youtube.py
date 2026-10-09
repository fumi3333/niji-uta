#!/usr/bin/env python3
"""YouTube Data API v3 で新着の歌ってみた/歌枠を収集し song_performances.json に統合する。

- 環境変数 YOUTUBE_API_KEY が必須（無ければ何もせず正常終了）
- クォータ節約: playlistItems(1) / videos(1/50件) / commentThreads(1) のみ。search.list は使わない
- 収集結果は data/youtube_records.json に累積保存（auto_update_dataset.py がシート由来で
  song_performances.json を作り直しても失われない）。最後に type="youtube-*" 行を差し替えて統合する
"""
import os, re, sys, json, time, html, datetime, urllib.request, urllib.parse, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PERF = os.path.join(DATA, "song_performances.json")
CHMAP = os.path.join(DATA, "channel_map.json")
STORE = os.path.join(DATA, "youtube_records.json")
API = "https://www.googleapis.com/youtube/v3/"
# クォータ(1日10,000)の目安: チャンネル解決 search 100×未解決数(初回のみ) + 一覧/詳細 約42×94 + コメント 1×この値
MAX_COMMENT_VIDEOS = int(os.environ.get("YT_MAX_COMMENT_VIDEOS", "1000"))
PER_CHANNEL = 30
BACKFILL_PAGES = int(os.environ.get("YT_BACKFILL_PAGES", "20"))  # 1ページ=50本。1日あたり1チャンネル最大1000本ずつ過去へ遡る
# 配信直後はセトリコメントがまだ無いことが多いので、この日数が経つまでは seen にせず再挑戦する
RETRY_DAYS = int(os.environ.get("YT_RETRY_DAYS", "7"))

COVER_RE = re.compile(r"歌ってみた|うたってみた|\bcover(?:ed)?\b|【\s*MV\s*】|original\s*song|オリジナル曲", re.I)
STREAM_RE = re.compile(r"歌枠|歌配信|うた枠|歌雑談|karaoke|singing|カラオケ", re.I)
# 歌枠っぽいタイトルでも曲以外のタイムスタンプが並ぶ企画
STREAM_NG_RE = re.compile(r"凸待ち|パワポ|同時視聴|ウォッチパーティ|watch\s*party", re.I)
SKIP_RE = re.compile(r"^(?:(?:op|ed|opening|ending|start|mc|end|intro|outro|q&a)(?![a-z])|開始|配信開始|待機|オープニング|エンディング|雑談|"
                     r"休憩|挨拶|告知|お知らせ|終了|おわり|お疲れ|スパチャ|スーパーチャット|sc読み|メン限|乾杯|フリートーク|トーク|声入り|スタート|開演|開場|自己紹介|感謝|見に来|凸|\d{1,2}:\d{2})", re.I)
# 曲名ではなくトーク・企画の区間を示す語（行のどこかに含まれていたら捨てる）
TALK_RE = re.compile(r"MC|エピソード|お話|話し|感想|告知|雑談|休憩|トーク|ありがとう|おつかれ|お疲れ|スパチャ|コメント|振り返り|……|\.\.\.", re.I)
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u2669\u266C-\u27BF\uFE0F\u200D]+")  # ♪♫ は残す
TS_RE = re.compile(r"^\s*(?:(?:\d{1,3}[.)）]|[-・●■▶▷►◆◇☆★]+)\s*)?(\d{1,2}:)?(\d{1,3}):(\d{2})\s*[-~〜:：)）\]】\s]*\s*(.+?)\s*$")


def call(endpoint, **params):
    params["key"] = os.environ["YOUTUBE_API_KEY"]
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 404) and endpoint == "commentThreads":
                return {"items": []}  # コメント無効など
            if e.code == 403:
                raise SystemExit(f"quota/permission error on {endpoint}: {e.read()[:200]}")
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return {"items": []}


def vid_of(url):
    m = re.search(r"(?:youtu\.be/|v=|/live/|/embed/)([\w-]{11})", url or "")
    return m.group(1) if m else None


def parse_timestamps(text):
    """概要欄/コメントから (秒, 'ラベル') を抽出。連続2行以上あるときだけ採用する"""
    out = []
    for line in (text or "").splitlines():
        m = TS_RE.match(line)
        if not m:
            continue
        h = int(m.group(1)[:-1]) if m.group(1) else 0
        sec = h * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        label = m.group(4).strip()
        label = label.lstrip("-・●■▶▷►◆◇☆★▼▽ 　")
        label = re.sub(r"^(?:\d{1,3}[.)）]|#\d{1,3}|[①-⑳])\s*", "", label)  # 「0:12 01. 曲名」「②曲名」の通し番号
        label = EMOJI_RE.sub("", label).strip(" 　/／♪♫")
        if out and out[-1][0] == sec:
            continue  # 「曲名」「Romanized」が同じ秒で並ぶ二言語セトリは先頭だけ
        if label and not SKIP_RE.match(label) and not is_talk(label):
            out.append((sec, label))
    # 「曲名/アーティスト」や「♪曲名」の行が過半なら、そうでない行（実況・トーク等）は捨てる
    songish = [(sec, l.lstrip("♪♫ ")) for sec, l in out if re.search(r"[/／]|^[♪♫]", l)]
    if len(songish) >= 3 and len(songish) * 2 >= len(out):
        out = songish
    return out if len(out) >= 3 else []


def is_talk(label):
    """「曲名 / アーティスト」形式でない行のうち、明らかに会話・企画の行"""
    if re.search(r"[/／]", label) or label.lower() in KNOWN_TITLES:
        return False
    if TALK_RE.search(label):
        return True
    # 長い日本語の感嘆・疑問文はトークとみなす（英語の曲名「Will You Marry Me?」等は残す）
    return len(label) > 14 and re.search(r"[！？。]$", label) is not None and not re.search(r"[A-Za-z]{3}", label)


def setlist_score(tss):
    return (sum(1 for _, l in tss if re.search(r"[/／]", l)), len(tss))


def split_song(label):
    """'曲名 / アーティスト' 等を (title, artist) に。区切りが無ければ artist は空"""
    label = re.sub(r"\s*[【\[(（].{0,12}[】\])）]\s*$", "", label).strip()
    parts = re.split(r"\s+[/／\-－―—]\s+|\s*／\s*|\s+/\s*", label, maxsplit=1)
    if len(parts) == 1:
        parts = label.split("/", 1)  # 「烈火/niki」のような詰めた表記
    t = parts[0].strip(" 　「」『』")
    a = parts[1].strip(" 　♪♫") if len(parts) > 1 else ""
    return t, a


def _load_known():
    """既存データの曲名・アーティスト名（「A - B」のどちらが曲名かの判定用）"""
    titles, artists = set(), set()
    try:
        for r in json.load(open(os.path.join(DATA, "songs.json"), encoding="utf-8")):
            titles.add(r.get("title", "").lower())
            artists.add(r.get("artist", "").lower())
        artists |= {a.lower() for a in json.load(open(os.path.join(DATA, "precise_artist_dict.json"), encoding="utf-8")).values()}
    except (OSError, ValueError):
        pass
    return titles - {""}, artists - {""}


KNOWN_TITLES, KNOWN_ARTISTS = _load_known()


def clean_cover_title(title, liver=""):
    t = re.sub(r"[【\[].*?[】\]]", " ", title)
    t = re.sub(r"[(（]\s*(?i:covered by.*?|cover|full|short|ver\.?.*?)\s*[)）]", " ", t)
    t = re.sub(r"(?i)\b(covered by.*|cover|full|ver\.?)\b", " ", t)
    head, *tail = re.split(r"歌ってみた|うたってみた", t, maxsplit=1)
    t = head if head.strip(" 　-") or not tail else tail[0]  # 「曲名 歌ってみた Buono!」→ 曲名
    # 「曲名 / アーティスト」等の後ろを落とす（「D/N/A / xx」のように空白付き区切りを優先）
    t = re.split(r"\s+[/|｜]\s*|\s*[／￤]\s*", t, maxsplit=1)[0] if re.search(r"\s+[/|｜]|[／￤]", t) else t.split("/", 1)[0]
    t = re.sub(r"\s+", " ", t).strip(" 　-－")  # 「ー」は曲名末尾の長音なので削らない
    m = re.search(r"[「『](.+?)[」』]", t)  # 「オリジナル曲『xxx』」『曲名』歌ってみた 等は括弧の中を曲名とする
    if m:
        return m.group(1).strip()
    parts = [x.strip() for x in re.split(r"\s+[-–—－]\s+", t, maxsplit=1)]
    if len(parts) == 2:  # 「曲名 - アーティスト」か「アーティスト - 曲名」かを既知データで判定
        a, b = parts
        is_liver = lambda x: liver and (x in liver or liver in x)
        if a.lower() in KNOWN_TITLES or is_liver(b):
            t = a
        elif b.lower() in KNOWN_TITLES or is_liver(a) or a.lower() in KNOWN_ARTISTS:
            t = b
        else:
            t = a
    return t


def iso_secs(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def _norm(s):
    return re.sub(r"[\s・.　]", "", s or "").lower()


def search_channel(liver):
    """既存データから推定できないライバーは search.list(100ユニット) で一度だけ公式チャンネルを探す"""
    res = call("search", part="snippet", type="channel", q=f"{liver} にじさんじ", maxResults=5)
    for it in res.get("items", []):
        if _norm(liver) in _norm(it["snippet"]["title"]):
            return it["snippet"]["channelId"]
    return None


def resolve_channels(perf):
    """既存データの動画IDから投稿チャンネルを多数決で推定（videos.list=1ユニット/50件）"""
    cmap = json.load(open(CHMAP, encoding="utf-8")) if os.path.exists(CHMAP) else {}
    by_liver = collections.defaultdict(list)
    for r in perf:
        v = vid_of(r.get("youtube_url"))
        if v and r.get("liver") and not str(r.get("type", "")).startswith("youtube"):
            by_liver[r["liver"]].append(v)
    for liver, vids in by_liver.items():
        if liver in cmap:
            continue
        uniq = list(dict.fromkeys(vids))[:50]
        items = call("videos", part="snippet", id=",".join(uniq)).get("items", [])
        c = collections.Counter(i["snippet"]["channelId"] for i in items)
        if c:
            ch, n = c.most_common(1)[0]
            if n >= 2 or len(items) == 1:
                cmap[liver] = ch
    missing = sorted({r["liver"] for r in perf if r.get("liver")} - set(cmap))
    for liver in missing:
        if "引退" in liver or "非公開" in liver:
            continue
        ch = search_channel(liver)
        print(f"  channel search: {liver} -> {ch}")
        if ch:
            cmap[liver] = ch
    json.dump(cmap, open(CHMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return cmap


def batches(liver, ch, cursors, seen):
    """新着(先頭30件) + 過去分バックフィル(カーソルを保存して毎回続きから BACKFILL_PAGES ページ)"""
    pl_id = "UU" + ch[2:]
    pl = call("playlistItems", part="contentDetails", playlistId=pl_id, maxResults=PER_CHANNEL)
    ids = [i["contentDetails"]["videoId"] for i in pl.get("items", []) if i["contentDetails"]["videoId"] not in seen]
    if ids:
        yield ids
    cur = cursors.setdefault(ch, {"token": None, "done": False, "started": False})
    if cur["done"]:
        return
    token = cur["token"]
    if not cur["started"]:  # 初回: 先頭ページを飛ばして2ページ目以降へ
        pl = call("playlistItems", part="contentDetails", playlistId=pl_id, maxResults=50)
        token, cur["started"] = pl.get("nextPageToken"), True
        first = [i["contentDetails"]["videoId"] for i in pl.get("items", []) if i["contentDetails"]["videoId"] not in seen]
        if first:
            yield first
    for _ in range(BACKFILL_PAGES):
        if not token:
            cur["done"] = True
            break
        pg = call("playlistItems", part="contentDetails", playlistId=pl_id, maxResults=50, pageToken=token)
        token = pg.get("nextPageToken")
        ids = [i["contentDetails"]["videoId"] for i in pg.get("items", []) if i["contentDetails"]["videoId"] not in seen]
        if ids:
            yield ids
    cur["token"] = token
    if not token:
        cur["done"] = True


def main():
    if not os.environ.get("YOUTUBE_API_KEY"):
        print("YOUTUBE_API_KEY not set; skip")
        return
    perf = json.load(open(PERF, encoding="utf-8"))
    store = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {"seen": [], "records": []}
    seen = set(store["seen"])
    cursors = store.setdefault("cursors", {})
    known_vids = {vid_of(r.get("youtube_url")) for r in perf if not str(r.get("type", "")).startswith("youtube")}
    cmap = resolve_channels(perf)
    print(f"channels resolved: {len(cmap)}")

    new_records, comment_budget = [], MAX_COMMENT_VIDEOS
    stats = collections.Counter()
    recent_cutoff = datetime.date.today() - datetime.timedelta(days=RETRY_DAYS)
    for liver, ch in cmap.items():
        for ids in batches(liver, ch, cursors, seen):
            vids = call("videos", part="snippet,contentDetails", id=",".join(ids)).get("items", [])
            for v in vids:
                vid, sn = v["id"], v["snippet"]
                # 配信予定・配信中は duration が無い/未確定なので、アーカイブ化してから拾う（seen にしない）
                if sn.get("liveBroadcastContent", "none") != "none" or "duration" not in v.get("contentDetails", {}):
                    stats["live/upcoming"] += 1
                    continue
                title, dur = sn["title"], iso_secs(v["contentDetails"]["duration"])
                url = f"https://youtu.be/{vid}"
                day = sn["publishedAt"][:10]
                seen.add(vid)
                if STREAM_RE.search(title) and not STREAM_NG_RE.search(title) and dur >= 1800 and vid not in known_vids:
                    text = sn.get("description", "")
                    tss, src = parse_timestamps(text), "desc"
                    if not tss and comment_budget > 0:
                        comment_budget -= 1
                        src = "comment"
                        cm = call("commentThreads", part="snippet", videoId=vid, order="relevance", maxResults=20, textFormat="plainText")
                        for c in cm.get("items", []):  # 最初に見つかったものではなく一番セトリらしいコメントを採用
                            c_sn = c["snippet"]["topLevelComment"]["snippet"]
                            cand = parse_timestamps(html.unescape(c_sn.get("textOriginal") or c_sn.get("textDisplay", "")))
                            if cand and setlist_score(cand) > setlist_score(tss):
                                tss = cand
                    if not tss and src == "desc":  # コメント取得枠が尽きた: 次回以降に回す
                        stats["stream: deferred (comment budget)"] += 1
                        seen.discard(vid)
                        continue
                    if not tss:
                        stats["stream: no setlist"] += 1
                        if datetime.date.fromisoformat(day) > recent_cutoff:
                            seen.discard(vid)  # セトリコメントが付くのを待って次回再挑戦
                        print(f"  [stream x] {liver} {vid} {title[:60]}")
                        continue
                    stats["stream: parsed"] += 1
                    print(f"  [stream {len(tss):>2} {src}] {liver} {vid} {title[:50]} :: " + " | ".join(l for _, l in tss[:4]))
                    for sec, label in tss:
                        t, a = split_song(label)
                        if t:
                            new_records.append({"title": t, "artist": a, "liver": liver, "date": day, "timestamp": f"{sec//60}:{sec%60:02d}",
                                                "youtube_url": f"{url}?t={sec}", "type": "youtube-stream"})
                elif COVER_RE.search(title) and 90 <= dur <= 900 and vid not in known_vids:
                    t = clean_cover_title(title, liver)
                    if t:
                        stats["cover"] += 1
                        print(f"  [cover] {liver} {vid} {title[:60]} -> {t}")
                        new_records.append({"title": t, "artist": "", "liver": liver, "date": day, "timestamp": "歌い出し",
                                            "youtube_url": url, "type": "youtube-cover"})
    store["seen"] = sorted(seen)
    print("backfill done: %d/%d channels" % (sum(1 for c in cursors.values() if c["done"]), len(cmap)))
    store["records"] += new_records
    json.dump(store, open(STORE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"new records: {len(new_records)}, total api records: {len(store['records'])}")
    print("summary: " + ", ".join(f"{k}={n}" for k, n in sorted(stats.items())))

    merge(perf, store["records"])


def merge(perf, api_records):
    try:
        import pykakasi
        kks = pykakasi.kakasi()
        hira = lambda s: "".join(i["hira"] for i in kks.convert(s or ""))
    except ImportError:
        hira = lambda s: ""
    base = [r for r in perf if not str(r.get("type", "")).startswith("youtube")]
    liver_kana = {r["liver"]: r.get("kana_liver", "") for r in base}
    have = {(vid_of(r["youtube_url"]), r["timestamp"]) for r in base}
    add = []
    for r in api_records:
        key = (vid_of(r["youtube_url"]), r["timestamp"])
        if key in have:
            continue
        if r.get("type") == "youtube-stream" and is_talk(r["title"]):
            continue  # 過去に取り込んだトーク行もここで除外
        have.add(key)
        r = dict(r)
        h = hira(r["title"])
        r["kana_title"] = h if h != r["title"] else ""
        r["kana_artist"] = ""
        r["kana_liver"] = liver_kana.get(r["liver"], "")
        add.append(r)
    out = base + add
    for i, r in enumerate(out, 1):
        r["id"] = i
    json.dump(out, open(PERF, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"merged: base={len(base)} + youtube={len(add)} -> {len(out)}")


if __name__ == "__main__":
    main()
