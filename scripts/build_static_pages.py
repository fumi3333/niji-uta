#!/usr/bin/env python3
"""静的SEOページ生成（SEO抜本強化版）。

- data/song_performances.json をクリーニング
- /liver/<ライバー名>/ と /song/<曲名>/ をGoogle検索で圧倒的に勝てるリッチな静的HTMLとして生成
  （パンくずリスト、JSON-LD構造化データ、定番曲ランキング、原曲アーティスト内訳、関連ライバー内部リンク）
- index.html / popular/index.html の <!--SSR--> ブロックに上位データを事前描画
- sitemap.xml を再生成（changefreq, priority を最適化）
"""
import json, os, re, html, collections
from datetime import date
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "song_performances.json")
BASE = "https://nijiuta.fumiproject.dev"
DATE_RE = re.compile(r"^\d{4}[/.\-]\d{1,2}[/.\-]\d{1,2}$")
BAD_SLUG = re.compile(r'[/\\?#%\s:*<>"|]')
MIN_SONG_ROWS = 2  # 曲ページを作る最低件数
SONG_PAGES = set()
e = html.escape


def clean(rows):
    out, seen_keys = [], set()
    for r in rows:
        k = (r.get("liver"), (r.get("title") or "").strip(), r.get("youtube_url"))
        if k in seen_keys:
            continue
        seen_keys.add(k)
        t = (r.get("title") or "").strip()
        if not t or DATE_RE.match(t) or not r.get("liver"):
            continue
        out.append(r)
    return out


def slug(s):
    return BAD_SLUG.sub("_", s.strip()).strip(". ") or "item"


def song_link(t):
    if t in SONG_PAGES:
        return f'<a href="/song/{quote(slug(t))}/">{e(t)}</a>'
    return e(t)


def yt(r):
    return r.get("youtube_url") or ""


STYLE = """<style>body{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;color:#1a1a1a;line-height:1.6;-webkit-text-size-adjust:100%;background:#fcfcfc}
header,main,footer{max-width:1100px;margin:0 auto;padding:12px 16px}header{border-bottom:2px solid #333;background:#fff}
.site-title{font-size:13px;font-weight:bold;margin-bottom:4px}.site-title a{color:#0056b3;text-decoration:none}
h1{font-size:22px;margin:8px 0;line-height:1.3;word-break:break-word}h2{font-size:17px;margin:28px 0 10px;padding-left:8px;border-left:4px solid #0056b3}
h3{font-size:15px;margin:18px 0 6px}a{color:#0056b3;text-decoration:none}a:hover{text-decoration:underline}
.breadcrumb{font-size:12px;color:#666;margin:8px 0 16px;padding:6px 0;border-bottom:1px solid #eee}
.breadcrumb a{color:#555}.breadcrumb span{margin:0 6px;color:#999}
.summary-box{background:#fff;border:1px solid #e1e4e8;border-radius:8px;padding:14px 18px;margin:14px 0 24px;box-shadow:0 1px 3px rgba(0,0,0,0.04);display:flex;flex-wrap:wrap;gap:16px}
.summary-stat{flex:1 1 120px}.summary-num{font-size:22px;font-weight:bold;color:#0056b3;line-height:1.2}.summary-label{font-size:11.5px;color:#666}
.top-ranking{display:grid;grid-template-columns:repeat(auto-fill, minmax(260px, 1fr));gap:10px;margin:12px 0 20px}
.ranking-card{background:#fff;border:1px solid #e1e4e8;border-radius:6px;padding:8px 12px;display:flex;align-items:center;gap:10px}
.rank-badge{width:24px;height:24px;background:#f0f4f8;color:#0056b3;font-weight:bold;font-size:12px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.rank-badge.top3{background:#ffd700;color:#333}
.rank-info{flex:1;min-width:0;font-size:13px}.rank-title{font-weight:bold;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rank-artist{font-size:11px;color:#666;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rank-count{font-size:12px;font-weight:bold;color:#444;white-space:nowrap}
.tag-list{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 20px}
.tag-chip{display:inline-block;background:#eef3f8;color:#0056b3;padding:3px 9px;border-radius:14px;font-size:12px;text-decoration:none}
.tag-chip:hover{background:#dfe8f2}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;touch-action:pan-x pan-y;margin:14px 0;background:#fff;border:1px solid #dcdcdc;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.03)}
table{width:100%;border-collapse:collapse;font-size:13px;white-space:nowrap}th,td{border-bottom:1px solid #eee;padding:8px 12px;text-align:left}
th{background:#f8f9fa;color:#495057;font-weight:600}.m{color:#666;font-size:12px}ul.c{columns:3 220px;list-style:none;padding:0;margin:10px 0}
.btn-play{display:inline-block;padding:3px 10px;background:#0056b3;color:#fff!important;border-radius:4px;font-size:11.5px;text-decoration:none}
.btn-play:hover{background:#004085;text-decoration:none}
footer{border-top:1px solid #dcdcdc;margin-top:40px;padding:24px 16px;font-size:12px;color:#666;text-align:center;background:#fff}
@media (max-width:640px){
header,main,footer{padding:10px 12px}
h1{font-size:19px}h2{font-size:16px;margin:22px 0 8px}table{font-size:12px}th,td{padding:6px 8px}ul.c{columns:1}
.summary-stat{flex:1 1 45%}
}
/* Vercel Toolbar & Feedback overlay 完全非表示 */
vercel-live-feedback,#vercel-toolbar,[data-vercel-toolbar],div:has(> vercel-live-feedback){
display:none!important;visibility:hidden!important;pointer-events:none!important;width:0!important;height:0!important;opacity:0!important}
</style>"""


def build_breadcrumbs_html(items):
    """items: [("名称", "URL"), ...]"""
    parts = []
    for i, (name, url) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<strong>{e(name)}</strong>')
        else:
            parts.append(f'<a href="{e(url)}">{e(name)}</a>')
    return '<nav class="breadcrumb" aria-label="パンくずリスト">' + ' <span>&gt;</span> '.join(parts) + '</nav>'


def build_breadcrumbs_ld(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": url if url.startswith("http") else f"{BASE}{url}"
            }
            for i, (name, url) in enumerate(items)
        ]
    }


def page(title, desc, canon, h1, body, breadcrumbs=None, extra_ld=None):
    ld_list = []
    if breadcrumbs:
        ld_list.append(build_breadcrumbs_ld(breadcrumbs))
    if extra_ld:
        if isinstance(extra_ld, list):
            ld_list.extend(extra_ld)
        else:
            ld_list.append(extra_ld)

    ld_s = "".join(f'<script type="application/ld+json">{json.dumps(item, ensure_ascii=False)}</script>' for item in ld_list)
    bc_html = build_breadcrumbs_html(breadcrumbs) if breadcrumbs else ""

    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="vercel-toolbar" content="off">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canon}">{ld_s}{STYLE}</head><body>
<header>
  <div class="site-title"><a href="/">← にじ歌サーチ（にじさんじ歌枠セトリ検索）</a></div>
  <h1>{e(h1)}</h1>
</header>
<main>
  {bc_html}
  {body}
</main>
<footer>
  <p>当サイトは有志ファンによる非公式ファンメイドツールです。ANYCOLOR株式会社とは一切関係ありません。</p>
  <p>© 2026 にじ歌サーチ (FumiProject)</p>
</footer>
</body></html>"""


def kind(r):
    if r.get("type") == "youtube-cover":
        return "歌ってみた"
    if r.get("type") == "youtube-stream" or re.search(r"[?&]t=\d", r.get("youtube_url") or "") or r.get("date") == "配信アーカイブ":
        return "歌枠"
    return "動画"


def table(rows, show_liver=True, show_title=True):
    h = '<div class="table-wrap"><table><thead><tr>' + ("<th>曲名</th>" if show_title else "") + "<th>原曲アーティスト</th>" + ("<th>歌ったライバー</th>" if show_liver else "") + "<th>歌唱種別</th><th>再生</th></tr></thead><tbody>"
    for r in rows:
        ts = r.get("timestamp") or ""
        label = (ts if ts and ts != "歌い出し" else "再生")
        h += "<tr>"
        if show_title:
            h += f'<td>{song_link(r["title"])}</td>'
        h += f'<td>{e(r.get("artist") or "-")}</td>'
        if show_liver:
            h += f'<td><a href="/liver/{quote(slug(r["liver"]))}/">{e(r["liver"])}</a></td>'
        h += f'<td>{kind(r)}</td>'
        h += f'<td><a href="{e(yt(r))}" rel="noopener nofollow" target="_blank" class="btn-play">▶ {e(label)}</a></td></tr>'
    return h + "</tbody></table></div>"


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
    SONG_PAGES.update(t for t, rs in by_song.items() if len(rs) >= MIN_SONG_ROWS)

    urls = ["/", "/popular/", "/utattemita/"]

    # 全ライバーの人気ランキング（内部リンク生成用）
    sorted_livers = sorted(by_liver.keys(), key=lambda l: len(by_liver[l]), reverse=True)

    # 1. ライバー別ページ生成
    for liver, rs in by_liver.items():
        song_counter = collections.Counter(r["title"] for r in rs)
        art_counter = collections.Counter(r["artist"] for r in rs if r.get("artist"))
        covers = [r for r in rs if r.get("type") == "youtube-cover"]
        streams = [r for r in rs if r.get("type") != "youtube-cover"]

        top_songs = song_counter.most_common(10)
        top_song_names = [t for t, _ in top_songs[:5]]
        top_song_str = "、".join(top_song_names)

        # SEO タイトル & ディスクリプション（ビッグワード完全網羅）
        title = f"{liver}（にじさんじ）歌枠セトリ・歌った曲一覧【全{len(rs)}曲】｜にじ歌サーチ"
        desc = f"にじさんじ所属ライバー「{liver}」が歌枠・歌ってみたで歌った全{len(rs)}曲（レパートリー{len(song_counter)}曲）のセトリ一覧。よく歌う人気曲（{top_song_str}）から最新歌枠まで。YouTube秒数頭出し直再生対応。"

        bc = [
            ("ホーム", f"{BASE}/"),
            ("ライバー一覧", f"{BASE}/#liver-list"),
            (f"{liver} の歌枠セトリ", f"{BASE}/liver/{quote(slug(liver))}/")
        ]

        # サマリー統計
        summary_html = f"""
        <div class="summary-box">
          <div class="summary-stat"><div class="summary-num">{len(rs):,}</div><div class="summary-label">総歌唱数（回）</div></div>
          <div class="summary-stat"><div class="summary-num">{len(song_counter):,}</div><div class="summary-label">レパートリー（曲種）</div></div>
          <div class="summary-stat"><div class="summary-num">{len(covers):,}</div><div class="summary-label">公式歌ってみた（本）</div></div>
          <div class="summary-stat"><div class="summary-num">{len(streams):,}</div><div class="summary-label">歌枠アーカイブ（曲）</div></div>
        </div>
        """

        # 定番曲ランキング TOP 10
        ranking_html = ""
        if top_songs:
            cards = []
            for idx, (song_name, cnt) in enumerate(top_songs, 1):
                badge_cls = "top3" if idx <= 3 else ""
                art = next((r["artist"] for r in rs if r["title"] == song_name and r.get("artist")), "-")
                cards.append(f"""
                <div class="ranking-card">
                  <div class="rank-badge {badge_cls}">{idx}</div>
                  <div class="rank-info">
                    <div class="rank-title">{song_link(song_name)}</div>
                    <div class="rank-artist">{e(art)}</div>
                  </div>
                  <div class="rank-count">{cnt}回</div>
                </div>
                """)
            ranking_html = f"<h2>{e(liver)} がよく歌う人気曲 TOP10</h2>" + f'<div class="top-ranking">{"".join(cards)}</div>'

        # よく歌うアーティスト TOP 8
        art_html = ""
        top_arts = art_counter.most_common(8)
        if top_arts:
            chips = "".join(f'<span class="tag-chip">{e(a)} ({cnt}曲)</span>' for a, cnt in top_arts)
            art_html = f"<h2>よく歌う本家アーティスト</h2>" + f'<div class="tag-list">{chips}</div>'

        # 関連・他の人気ライバーへの内部リンク
        other_livers = [l for l in sorted_livers if l != liver][:15]
        other_chips = "".join(f'<a href="/liver/{quote(slug(ol))}/" class="tag-chip">{e(ol)} ({len(by_liver[ol])}曲)</a>' for ol in other_livers)
        other_html = f"<h2>にじさんじ 他のライバーの歌枠セトリ</h2>" + f'<div class="tag-list">{other_chips}</div>'

        # 全曲テーブル
        table_html = f"<h2>全歌唱履歴・セットリスト一覧（{len(rs)}件）</h2>" + table(rs, show_liver=False)

        body = summary_html + ranking_html + art_html + table_html + other_html

        person_ld = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": liver,
            "description": f"にじさんじ所属バーチャルライバー {liver}",
            "url": f"{BASE}/liver/{quote(slug(liver))}/"
        }

        write(f"liver/{slug(liver)}/index.html", page(title, desc, f"{BASE}/liver/{quote(slug(liver))}/", f"{liver}（にじさんじ）の歌枠セトリ・歌唱曲一覧", body, breadcrumbs=bc, extra_ld=person_ld))
        urls.append(f"/liver/{quote(slug(liver))}/")

    # 2. 曲別ページ生成
    n_song = 0
    for t, rs in by_song.items():
        if t not in SONG_PAGES:
            continue
        livers = sorted({r["liver"] for r in rs})
        art = next((r["artist"] for r in rs if r.get("artist")), "")
        liver_counts = collections.Counter(r["liver"] for r in rs).most_common(8)

        art_label = f"（原曲: {art}）" if art else ""
        title = f"「{t}」{art_label}を歌ったにじさんじライバー一覧【全{len(livers)}人・{len(rs)}回】｜にじ歌サーチ"
        desc = f"「{t}」{art_label}を歌枠・歌ってみたで歌ったにじさんじライバー全{len(livers)}人（{len(rs)}回分）のセトリ一覧。歌唱ライバー: {'、'.join(livers[:6])}。YouTube秒数頭出し直再生対応。"

        bc = [
            ("ホーム", f"{BASE}/"),
            ("人気曲ランキング", f"{BASE}/popular/"),
            (f"「{t}」を歌ったライバー", f"{BASE}/song/{quote(slug(t))}/")
        ]

        summary_html = f"""
        <div class="summary-box">
          <div class="summary-stat"><div class="summary-num">{len(livers):,}</div><div class="summary-label">歌ったライバー（人）</div></div>
          <div class="summary-stat"><div class="summary-num">{len(rs):,}</div><div class="summary-label">総歌唱回数（回）</div></div>
          <div class="summary-stat"><div class="summary-num">{e(art or "-")}</div><div class="summary-label">本家アーティスト</div></div>
        </div>
        """

        # 誰が多く歌っているかランキング
        top_singers_html = ""
        if len(liver_counts) > 1:
            cards = []
            for idx, (l_name, cnt) in enumerate(liver_counts, 1):
                badge_cls = "top3" if idx <= 3 else ""
                cards.append(f"""
                <div class="ranking-card">
                  <div class="rank-badge {badge_cls}">{idx}</div>
                  <div class="rank-info">
                    <div class="rank-title"><a href="/liver/{quote(slug(l_name))}/">{e(l_name)}</a></div>
                  </div>
                  <div class="rank-count">{cnt}回</div>
                </div>
                """)
            top_singers_html = f"<h2>「{e(t)}」を多く歌っているライバー</h2>" + f'<div class="top-ranking">{"".join(cards)}</div>'

        history_html = f"<h2>歌唱履歴一覧（{len(rs)}件）</h2>" + table(rs, show_title=False)

        body = summary_html + top_singers_html + history_html

        music_ld = {
            "@context": "https://schema.org",
            "@type": "MusicRecording",
            "name": t,
            "url": f"{BASE}/song/{quote(slug(t))}/"
        }
        if art:
            music_ld["byArtist"] = {"@type": "MusicGroup", "name": art}

        write(f"song/{slug(t)}/index.html", page(title, desc, f"{BASE}/song/{quote(slug(t))}/", f"「{t}」{art_label}を歌ったにじさんじライバー", body, breadcrumbs=bc, extra_ld=music_ld))
        urls.append(f"/song/{quote(slug(t))}/")
        n_song += 1

    # 3. 歌ってみた一覧ページ
    covers = sorted((r for r in rows if r.get("type") == "youtube-cover"), key=lambda r: r.get("date", ""), reverse=True)
    cc = collections.Counter(r["liver"] for r in covers)
    chips = "".join(f'<a href="/liver/{quote(slug(l))}/" class="tag-chip">{e(l)} ({n})</a>' for l, n in cc.most_common(30))
    ctable = '<div class="table-wrap"><table><thead><tr><th>公開日</th><th>曲名</th><th>歌ったライバー</th><th>動画</th></tr></thead><tbody>' + "".join(
        f'<tr><td>{e(r.get("date",""))}</td><td>{song_link(r["title"])}</td>'
        f'<td><a href="/liver/{quote(slug(r["liver"]))}/">{e(r["liver"])}</a></td>'
        f'<td><a href="{e(yt(r))}" rel="noopener nofollow" target="_blank" class="btn-play">▶ YouTube公式</a></td></tr>' for r in covers) + "</tbody></table></div>"

    bc_cover = [
        ("ホーム", f"{BASE}/"),
        ("歌ってみたまとめ", f"{BASE}/utattemita/")
    ]
    cover_body = f"""
    <div class="summary-box">
      <div class="summary-stat"><div class="summary-num">{len(covers):,}</div><div class="summary-label">公式歌ってみた動画</div></div>
      <div class="summary-stat"><div class="summary-num">{len(cc):,}</div><div class="summary-label">参加ライバー数</div></div>
    </div>
    <h2>ライバー別 歌ってみた動画</h2>
    <div class="tag-list">{chips}</div>
    <h2>新着 歌ってみた動画一覧</h2>
    {ctable}
    """
    write("utattemita/index.html", page(
        f"にじさんじ 歌ってみた・公式カバー曲まとめ（全{len(covers)}本・新着順）｜にじ歌サーチ",
        f"にじさんじ所属ライバーの歌ってみた動画・公式MV・カバー曲（全{len(covers)}本・{len(cc)}人）を新着順に一覧まとめ。毎日自動更新。",
        f"{BASE}/utattemita/", "にじさんじ 歌ってみた・公式カバー曲まとめ", cover_body, breadcrumbs=bc_cover))

    # 4. トップページ & popular の SSR 描画
    liv_list = "".join(f'<li><a href="/liver/{quote(slug(l))}/">{e(l)}</a> <span class="m">({len(rs):,}曲)</span></li>'
                       for l, rs in sorted(by_liver.items(), key=lambda kv: -len(kv[1])))
    pop = sorted(((t, rs) for t, rs in by_song.items() if t in SONG_PAGES), key=lambda kv: -len(kv[1]))
    pop_li = "".join(f'<li><a href="/song/{quote(slug(t))}/">{e(t)}</a> <span class="m">({len({r["liver"] for r in rs})}人 / {len(rs)}回)</span></li>' for t, rs in pop[:120])

    ssr_section = f"""
    <section style="max-width:1240px;margin:24px auto;padding:16px;">
      <h2 id="liver-list" style="font-size:18px;margin-bottom:12px;border-left:4px solid #0056b3;padding-left:8px;">ライバー別 歌枠セトリ・歌唱曲一覧</h2>
      <ul class="c">{liv_list}</ul>
      <h2 style="font-size:18px;margin:28px 0 12px;border-left:4px solid #0056b3;padding-left:8px;">歌枠でよく歌われる定番曲（{len(pop):,}曲中 上位120曲）</h2>
      <ul class="c">{pop_li}</ul>
    </section>
    """
    inject("index.html", ssr_section)

    pop_rows = "".join(f'<tr><td>{i}</td><td><a href="/song/{quote(slug(t))}/">{e(t)}</a></td><td>{e(next((r["artist"] for r in rs if r.get("artist")), "-"))}</td><td><strong>{len({r["liver"] for r in rs})}人</strong> / {len(rs)}回</td></tr>' for i, (t, rs) in enumerate(pop[:100], 1))
    pop_section = f"""
    <section style="max-width:1240px;margin:16px auto;padding:16px">
      <h2>にじさんじ 歌枠で最も歌われた人気曲ランキング TOP100</h2>
      <p class="m">にじさんじ全ライバーの歌枠・歌ってみたアーカイブから集計した、歌唱人数の多い定番ソングランキングです。</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>順位</th><th>曲名</th><th>原曲アーティスト</th><th>歌唱人数 / 回数</th></tr></thead>
          <tbody>{pop_rows}</tbody>
        </table>
      </div>
    </section>
    """
    inject("popular/index.html", pop_section)

    # 5. sitemap.xml の生成（changefreq, priority 配分）
    today = date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        if u == "/":
            pr, freq = "1.0", "daily"
        elif u in ["/popular/", "/utattemita/"]:
            pr, freq = "0.9", "daily"
        elif u.startswith("/liver/"):
            pr, freq = "0.8", "weekly"
        else:
            pr, freq = "0.6", "monthly"
        sm += f"  <url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{pr}</priority></url>\n"
    sm += "</urlset>\n"
    write("sitemap.xml", sm)

    # 6. 件数メタを更新
    for p in ["index.html"]:
        full = os.path.join(ROOT, p)
        s = open(full, encoding="utf-8").read()
        s = re.sub(r"収録データ: [\d,]+件", f"収録データ: {n_rows:,}件", s)
        s = re.sub(r"最終更新: [\d\- :]+", f"最終更新: {today}", s)
        open(full, "w", encoding="utf-8").write(s)
    print(f"livers={n_liver} songs_pages={n_song} urls={len(urls)}")


if __name__ == "__main__":
    main()
