#!/usr/bin/env python3
"""YouTube Data API v3 で新着の歌ってみた/歌枠を収集し song_performances.json に統合する。

- 環境変数 YOUTUBE_API_KEY が必須（無ければ何もせず正常終了）
- クォータ節約: playlistItems(1) / videos(1/50件) / commentThreads(1) のみ。search.list は使わない
- 収集結果は data/youtube_records.json に累積保存（auto_update_dataset.py がシート由来で
  song_performances.json を作り直しても失われない）。最後に type="youtube-*" 行を差し替えて統合する
"""
import os, re, sys, json, time, urllib.request, urllib.parse, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PERF = os.path.join(DATA, "song_performances.json")
CHMAP = os.path.join(DATA, "channel_map.json")
STORE = os.path.join(DATA, "youtube_records.json")
API = "https://www.googleapis.com/youtube/v3/"
MAX_COMMENT_VIDEOS = int(os.environ.get("YT_MAX_COMMENT_VIDEOS", "60"))
PER_CHANNEL = 30

COVER_RE = re.compile(r"歌ってみた|うたってみた|cover|covered|【\s*MV\s*】|original\s*song|オリジナル曲", re.I)
STREAM_RE = re.compile(r"歌枠|歌配信|うた枠|歌雑談|karaoke|singing|カラオケ", re.I)
SKIP_RE = re.compile(r"^(op|ed|opening|ending|start|開始|オープニング|エンディング|雑談|休憩|挨拶|告知|終了|おわり|お疲れ)", re.I)
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
        label = label.lstrip("-・●■▶▷►◆◇☆★ 　")
        if label and not SKIP_RE.match(label):
            out.append((sec, label))
    return out if len(out) >= 3 else []


def split_song(label):
    """'曲名 / アーティスト' 等を (title, artist) に。区切りが無ければ artist は空"""
    label = re.sub(r"\s*[【\[(（].{0,12}[】\])）]\s*$", "", label).strip()
    parts = re.split(r"\s+[/／\-－―—]\s+|\s*／\s*|\s+/\s*", label, maxsplit=1)
    t = parts[0].strip(" 　「」『』")
    a = parts[1].strip(" 　") if len(parts) > 1 else ""
    return t, a


def clean_cover_title(title):
    t = re.sub(r"[【\[].*?[】\]]", " ", title)
    t = re.sub(r"(?i)\b(cover|covered by.*|full|ver\.?)\b", " ", t)
    t = re.sub(r"\s*[/／|｜].*$", "", t)  # 「曲名 / 歌ってみた」等の後ろ
    return re.sub(r"\s+", " ", t).strip(" 　-ー")


def iso_secs(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


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
    json.dump(cmap, open(CHMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return cmap


def main():
    if not os.environ.get("YOUTUBE_API_KEY"):
        print("YOUTUBE_API_KEY not set; skip")
        return
    perf = json.load(open(PERF, encoding="utf-8"))
    store = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {"seen": [], "records": []}
    seen = set(store["seen"])
    known_vids = {vid_of(r.get("youtube_url")) for r in perf if not str(r.get("type", "")).startswith("youtube")}
    cmap = resolve_channels(perf)
    print(f"channels resolved: {len(cmap)}")

    new_records, comment_budget = [], MAX_COMMENT_VIDEOS
    for liver, ch in cmap.items():
        pl = call("playlistItems", part="contentDetails", playlistId="UU" + ch[2:], maxResults=PER_CHANNEL)
        ids = [i["contentDetails"]["videoId"] for i in pl.get("items", []) if i["contentDetails"]["videoId"] not in seen]
        if not ids:
            continue
        vids = call("videos", part="snippet,contentDetails", id=",".join(ids)).get("items", [])
        for v in vids:
            vid, sn = v["id"], v["snippet"]
            seen.add(vid)
            title, dur = sn["title"], iso_secs(v["contentDetails"]["duration"])
            url = f"https://youtu.be/{vid}"
            day = sn["publishedAt"][:10]
            if STREAM_RE.search(title) and dur >= 1800 and vid not in known_vids:
                text = sn.get("description", "")
                tss = parse_timestamps(text)
                if not tss and comment_budget > 0:
                    comment_budget -= 1
                    cm = call("commentThreads", part="snippet", videoId=vid, order="relevance", maxResults=20)
                    for c in cm.get("items", []):
                        tss = parse_timestamps(c["snippet"]["topLevelComment"]["snippet"]["textDisplay"].replace("<br>", "\n"))
                        if tss:
                            break
                for sec, label in tss:
                    t, a = split_song(label)
                    if t:
                        new_records.append({"title": t, "artist": a, "liver": liver, "date": day, "timestamp": f"{sec//60}:{sec%60:02d}",
                                            "youtube_url": f"{url}?t={sec}", "type": "youtube-stream"})
            elif COVER_RE.search(title) and 90 <= dur <= 900 and vid not in known_vids:
                t = clean_cover_title(title)
                if t:
                    new_records.append({"title": t, "artist": "", "liver": liver, "date": day, "timestamp": "歌い出し",
                                        "youtube_url": url, "type": "youtube-cover"})
    store["seen"] = sorted(seen)
    store["records"] += new_records
    json.dump(store, open(STORE, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"new records: {len(new_records)}, total api records: {len(store['records'])}")

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
