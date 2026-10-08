#!/usr/bin/env python3
"""静的SEOページ生成。

- data/song_performances.json をクリーニング（日付だけの曲名などのゴミ行を除去）
- /liver/<ライバー名>/ と /song/<曲名>/ をクロール可能な静的HTMLとして生成
- index.html / popular/index.html の <!--SSR--> ブロックに上位データを事前描画
- sitemap.xml を再生成
"""
import json, os, re, html, collections
from datetime import date
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "song_performances.json")
BASE = "https://nijiuta.fumiproject.dev"
DATE_RE = re.compile(r"^\d{4}[/.\-]\d{1,2}[/.\-]\d{1,2}$")
BAD_SLUG = re.compile(r'[/\\?#%\s]')
e = html.escape


def clean(rows):
    out = []
    for r in rows:
        t = (r.get("title") or "").strip()
        if not t or DATE_RE.match(t) or not r.get("liver"):
            continue
        out.append(r)
    return out


def slug(s):
    return BAD_SLUG.sub("_", s.strip())


def yt(r):
    return r.get("youtube_url") or ""


STYLE = """<style>body{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;color:#1a1a1a;line-height:1.5}
header,main,footer{max-width:1100px;margin:0 auto;padding:12px 16px}header{border-bottom:2px solid #b0b0b0}
h1{font-size:20px;margin:6px 0}h2{font-size:16px;margin:24px 0 8px}a{color:#0056b3}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{border-bottom:1px solid #dcdcdc;padding:6px 8px;text-align:left}
th{background:#f4f5f7}.m{color:#666;font-size:12px}ul.c{columns:3 220px;list-style:none;padding:0}footer{border-top:1px solid #dcdcdc;margin-top:32px;font-size:12px;color:#666}</style>"""


def page(title, desc, canon, h1, body, ld=None):
    ld_s = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canon}">{ld_s}{STYLE}</head><body>
<header><a href="/">← にじ歌サーチ（にじさんじ歌枠セトリ検索）</a><h1>{e(h1)}</h1></header>
<main>{body}</main>
<footer>当サイトは有志ファンによる非公式ツールです。ANYCOLOR株式会社とは関係ありません。 © 2026 FumiProject</footer>
</body></html>"""


def table(rows, show_liver=True, show_title=True):
    h = "<table><thead><tr>" + ("<th>曲名</th>" if show_title else "") + "<th>本家</th>" + ("<th>歌唱ライバー</th>" if show_liver else "") + "<th>頭出し</th></tr></thead><tbody>"
    for r in rows:
        ts = r.get("timestamp") or ""
        label = "▶ " + (ts if ts and ts != "歌い出し" else "再生")
        h += "<tr>"
        if show_title:
            h += f'<td><a href="/song/{quote(slug(r["title"]))}/">{e(r["title"])}</a></td>'
        h += f'<td>{e(r.get("artist") or "")}</td>'
        if show_liver:
            h += f'<td><a href="/liver/{quote(slug(r["liver"]))}/">{e(r["liver"])}</a></td>'
        h += f'<td><a href="{e(yt(r))}" rel="noopener nofollow" target="_blank">{e(label)}</a></td></tr>'
    return h + "</tbody></table>"


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def inject(path, block):
    full = os.path.join(ROOT, path)
    s = open(full, encoding="utf-8").read()
    new, n = re.subn(r"<!--SSR-->.*?<!--/SSR-->", lambda m: f"<!--SSR-->{block}<!--/SSR-->", s, flags=re.S)
    if n == 0:
        raise SystemExit(f"{path}: <!--SSR--><!--/SSR--> marker missing")
    open(full, "w", encoding="utf-8").write(new)


def main():
    raw = json.load(open(DATA, encoding="utf-8"))
    rows = clean(raw)
    print(f"cleaned: {len(raw)} -> {len(rows)}")
    for i, r in enumerate(rows, 1):
        r["id"] = i
    json.dump(rows, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    by_liver = collections.defaultdict(list)
    by_song = collections.defaultdict(list)
    for r in rows:
        by_liver[r["liver"]].append(r)
        by_song[r["title"]].append(r)
    n_liver, n_rows = len(by_liver), len(rows)

    urls = ["/", "/popular/"]

    # ライバー別ページ
    for liver, rs in by_liver.items():
        songs = collections.Counter(r["title"] for r in rs)
        top = ", ".join(t for t, _ in songs.most_common(5))
        title = f"{liver}の歌枠セトリ・歌った曲一覧（{len(rs)}曲）｜にじ歌サーチ"
        desc = f"にじさんじ {liver} が歌枠で歌った{len(rs)}曲（{len(songs)}曲種）のセトリ一覧。{top} など。曲名から該当秒数へ頭出し再生。"
        body = f'<p class="m">{e(liver)} の歌唱 {len(rs)} 件 / {len(songs)} 曲。リンクはYouTubeの該当秒数です。</p>' + table(rs, show_liver=False)
        write(f"liver/{slug(liver)}/index.html", page(title, desc, f"{BASE}/liver/{quote(slug(liver))}/", f"{liver} の歌枠セトリ・歌唱曲一覧", body))
        urls.append(f"/liver/{quote(slug(liver))}/")

    # 曲別ページ（2ライバー以上 or 2件以上）
    n_song = 0
    for t, rs in by_song.items():
        if len(rs) < 2:
            continue
        livers = sorted({r["liver"] for r in rs})
        art = next((r["artist"] for r in rs if r.get("artist")), "")
        title = f"{t}を歌ったにじさんじライバー一覧（{len(livers)}人）｜歌枠セトリ"
        desc = f"「{t}」{('（' + art + '）') if art else ''}を歌枠で歌ったにじさんじライバー {len(livers)}人・{len(rs)}回分。{'、'.join(livers[:5])} など。秒数頭出しで再生。"
        body = f'<p class="m">歌唱ライバー: {e("、".join(livers))}</p>' + table(rs, show_title=False)
        write(f"song/{slug(t)}/index.html", page(title, desc, f"{BASE}/song/{quote(slug(t))}/", f"「{t}」を歌ったにじさんじライバー", body))
        urls.append(f"/song/{quote(slug(t))}/")
        n_song += 1

    # ライバー索引 / 人気曲を index と popular に事前描画
    liv_list = "".join(f'<li><a href="/liver/{quote(slug(l))}/">{e(l)}</a> <span class="m">({len(rs)})</span></li>'
                       for l, rs in sorted(by_liver.items(), key=lambda kv: -len(kv[1])))
    pop = sorted(((t, rs) for t, rs in by_song.items() if len(rs) >= 2), key=lambda kv: -len(kv[1]))
    pop_li = "".join(f'<li><a href="/song/{quote(slug(t))}/">{e(t)}</a> <span class="m">({len({r["liver"] for r in rs})}人)</span></li>' for t, rs in pop[:120])
    inject("index.html", f'<section style="max-width:1240px;margin:0 auto;padding:16px"><h2>ライバー別 歌枠セトリ</h2><ul class="c">{liv_list}</ul><h2>よく歌われる曲</h2><ul class="c">{pop_li}</ul></section>')
    pop_rows = "".join(f'<tr><td>{i}</td><td><a href="/song/{quote(slug(t))}/">{e(t)}</a></td><td>{e(next((r["artist"] for r in rs if r.get("artist")), ""))}</td><td>{len({r["liver"] for r in rs})}人 / {len(rs)}回</td></tr>' for i, (t, rs) in enumerate(pop[:100], 1))
    inject("popular/index.html", f'<section style="max-width:1240px;margin:0 auto;padding:16px"><h2>歌われた人数ランキング TOP100</h2><table><thead><tr><th>順位</th><th>曲名</th><th>本家</th><th>歌唱</th></tr></thead><tbody>{pop_rows}</tbody></table></section>')

    # サイトマップ
    today = date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        pr = "1.0" if u == "/" else "0.8" if u.count("/") == 2 and u != "/" and not u.startswith(("/liver", "/song")) else "0.6"
        sm += f"  <url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n"
    sm += "</urlset>\n"
    write("sitemap.xml", sm)

    # 件数メタを更新
    for p in ["index.html"]:
        full = os.path.join(ROOT, p)
        s = open(full, encoding="utf-8").read()
        s = re.sub(r"収録データ: [\d,]+件", f"収録データ: {n_rows:,}件", s)
        s = re.sub(r"最終更新: [\d\- :]+", f"最終更新: {today}", s)
        open(full, "w", encoding="utf-8").write(s)
    print(f"livers={n_liver} songs_pages={n_song} urls={len(urls)}")


if __name__ == "__main__":
    main()
