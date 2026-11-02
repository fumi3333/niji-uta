# -*- coding: utf-8 -*-
"""アーティスト別静的SEOページ（/artist/<アーティスト名>/）の自動生成スクリプト

- data/song_performances.json から5件以上歌唱データがある主要アーティスト（約880組）を抽出
- /artist/<slug>/index.html を生成
  - 構造化データ（BreadcrumbList, MusicGroup, FAQPage）完全装備
  - レパートリー曲数、歌唱ライバー数、総歌唱数のサマリーボックス
  - 人気曲TOP10ランキング
  - 歌ったライバー一覧タグ
  - タイムスタンプ秒数直飛び再生リンク付き全歌唱一覧テーブル
- sitemap.xml へ全アーティストページを追加
"""

import json
import os
import re
import html
from collections import defaultdict, Counter
from datetime import date
from urllib.parse import quote

ROOT = r"c:\niji-uta"
DATA_PATH = os.path.join(ROOT, "data", "song_performances.json")
BASE_URL = "https://nijiuta.fumiproject.dev"
BAD_SLUG = re.compile(r'[/\\?#%\s:*<>"|]')

e = html.escape

def slugify(s):
    cleaned = BAD_SLUG.sub("_", s.strip()).strip(". ")
    return cleaned or "item"

def parse_time_label(ts):
    if not ts or ts in ['歌い出し', '-', '最初から']:
        return '最初から'
    return f"{ts} から"

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    # アーティストごとにグルーピング
    by_artist = defaultdict(list)
    for r in records:
        a = (r.get("artist") or "").strip()
        if not a or a in ["未設定", "ボカロP / 原作者", "不明", "なし"] or len(a) < 2:
            continue
        by_artist[a].append(r)

    # 5件以上の主要アーティストを対象
    target_artists = {a: rs for a, rs in by_artist.items() if len(rs) >= 5}
    print(f"Target artists count (>= 5 songs): {len(target_artists)}")

    out_base = os.path.join(ROOT, "artist")
    os.makedirs(out_base, exist_ok=True)

    generated_urls = []

    for artist_name, rows in target_artists.items():
        art_slug = slugify(artist_name)
        art_dir = os.path.join(out_base, art_slug)
        os.makedirs(art_dir, exist_ok=True)

        # 統計
        total_songs = len(rows)
        unique_livers = sorted(list({r["liver"] for r in rows if r.get("liver")}))
        liver_count = len(unique_livers)
        song_counts = Counter(r.get("title", "") for r in rows if r.get("title"))
        repertoire_count = len(song_counts)

        # 人気曲TOP10
        top_songs = song_counts.most_common(10)
        top_song_cards = []
        for rank, (song_title, count) in enumerate(top_songs, 1):
            badge_class = "rank-badge top3" if rank <= 3 else "rank-badge"
            song_slug = slugify(song_title)
            top_song_cards.append(f"""
                <div class="ranking-card">
                  <div class="{badge_class}">{rank}</div>
                  <div class="rank-info">
                    <div class="rank-title"><a href="/song/{quote(song_slug)}/">{e(song_title)}</a></div>
                    <div class="rank-artist">{e(artist_name)}</div>
                  </div>
                  <div class="rank-count">{count}回</div>
                </div>
            """)

        # 歌ったライバータグ（上位）
        liver_song_counts = Counter(r.get("liver", "") for r in rows if r.get("liver"))
        top_livers = liver_song_counts.most_common(20)
        liver_chips = []
        for liv, cnt in top_livers:
            liv_slug = slugify(liv)
            liver_chips.append(f'<a href="/liver/{quote(liv_slug)}/" class="tag-chip">{e(liv)} ({cnt}曲)</a>')

        # 全歌唱行（歌唱日降順）
        table_rows = []
        for idx, r in enumerate(rows[:200], 1):  # 最大200件掲載
            t = r.get("title", "")
            song_slug = slugify(t)
            liv = r.get("liver", "")
            liv_slug = slugify(liv)
            d = r.get("date", "-")
            yt_url = r.get("youtube_url", "")
            ts = parse_time_label(r.get("timestamp"))

            play_btn = f'<a href="{e(yt_url)}" target="_blank" rel="noopener" class="btn-play">▶ {e(ts)}</a>' if yt_url else '-'

            table_rows.append(f"""
              <tr>
                <td>{idx}</td>
                <td><a href="/song/{quote(song_slug)}/">{e(t)}</a></td>
                <td><a href="/liver/{quote(liv_slug)}/">{e(liv)}</a></td>
                <td>{e(d)}</td>
                <td>{play_btn}</td>
              </tr>
            """)

        top_songs_str = "、".join([t for t, _ in top_songs[:5]])

        page_title = f"{artist_name}を歌ったにじさんじライバー一覧・歌枠セトリ【全{total_songs}曲】｜にじ歌サーチ"
        page_desc = f"にじさんじ所属ライバーが歌枠や歌ってみたで歌った「{artist_name}」の楽曲一覧（全{total_songs}曲・{liver_count}人歌唱）。よく歌われる人気曲（{top_songs_str}）から各ライバーの歌唱アーカイブ秒数直飛び再生リンクまで完全網羅。"
        canonical_url = f"{BASE_URL}/artist/{quote(art_slug)}/"

        json_ld_breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "ホーム", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "アーティスト一覧", "item": f"{BASE_URL}/#artist-list"},
                {"@type": "ListItem", "position": 3, "name": f"{artist_name} の歌枠セトリ", "item": canonical_url}
            ]
        }

        json_ld_music = {
            "@context": "https://schema.org",
            "@type": "MusicGroup",
            "name": artist_name,
            "description": f"にじさんじ歌枠・歌ってみたで歌唱された本家アーティスト {artist_name}",
            "url": canonical_url
        }

        json_ld_faq = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"にじさんじで「{artist_name}」の曲を最も多く歌っているライバーは誰ですか？",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"最も多く歌っているのは「{top_livers[0][0]}」（{top_livers[0][1]}回）です。続いて{top_livers[1][0]}（{top_livers[1][1]}回）などが歌っています。" if len(top_livers) >= 2 else f"「{top_livers[0][0]}」（{top_livers[0][1]}回）が歌っています。"
                    }
                },
                {
                    "@type": "Question",
                    "name": f"にじさんじ歌枠で最も人気の「{artist_name}」の楽曲は何ですか？",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"最もよく歌われているのは「{top_songs[0][0]}」（{top_songs[0][1]}回）です。続いて「{top_songs[1][0]}」（{top_songs[1][1]}回）などが人気です。" if len(top_songs) >= 2 else f"「{top_songs[0][0]}」（{top_songs[0][1]}回）です。"
                    }
                }
            ]
        }

        html_content = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="vercel-toolbar" content="off">
<title>{e(page_title)}</title>
<meta name="description" content="{e(page_desc)}">
<link rel="canonical" href="{canonical_url}">
<meta property="og:title" content="{e(page_title)}">
<meta property="og:description" content="{e(page_desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical_url}">
<script type="application/ld+json">{json.dumps(json_ld_breadcrumb, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(json_ld_music, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(json_ld_faq, ensure_ascii=False)}</script>
<style>
body{{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;color:#1a1a1a;line-height:1.6;-webkit-text-size-adjust:100%;background:#fcfcfc}}
header,main,footer{{max-width:1100px;margin:0 auto;padding:12px 16px}}
header{{border-bottom:2px solid #333;background:#fff}}
.site-title{{font-size:13px;font-weight:bold;margin-bottom:4px}}.site-title a{{color:#0056b3;text-decoration:none}}
h1{{font-size:22px;margin:8px 0;line-height:1.3;word-break:break-word}}
h2{{font-size:17px;margin:28px 0 10px;padding-left:8px;border-left:4px solid #0056b3}}
a{{color:#0056b3;text-decoration:none}}a:hover{{text-decoration:underline}}
.breadcrumb{{font-size:12px;color:#666;margin:8px 0 16px;padding:6px 0;border-bottom:1px solid #eee}}
.breadcrumb a{{color:#555}}.breadcrumb span{{margin:0 6px;color:#999}}
.summary-box{{background:#fff;border:1px solid #e1e4e8;border-radius:8px;padding:14px 18px;margin:14px 0 24px;box-shadow:0 1px 3px rgba(0,0,0,0.04);display:flex;flex-wrap:wrap;gap:16px}}
.summary-stat{{flex:1 1 120px}}.summary-num{{font-size:22px;font-weight:bold;color:#0056b3;line-height:1.2}}.summary-label{{font-size:11.5px;color:#666}}
.top-ranking{{display:grid;grid-template-columns:repeat(auto-fill, minmax(260px, 1fr));gap:10px;margin:12px 0 20px}}
.ranking-card{{background:#fff;border:1px solid #e1e4e8;border-radius:6px;padding:8px 12px;display:flex;align-items:center;gap:10px}}
.rank-badge{{width:24px;height:24px;background:#f0f4f8;color:#0056b3;font-weight:bold;font-size:12px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.rank-badge.top3{{background:#ffd700;color:#333}}
.rank-info{{flex:1;min-width:0;font-size:13px}}.rank-title{{font-weight:bold;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.rank-artist{{font-size:11px;color:#666;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.rank-count{{font-size:12px;font-weight:bold;color:#444;white-space:nowrap}}
.tag-list{{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 20px}}
.tag-chip{{display:inline-block;background:#eef3f8;color:#0056b3;padding:3px 9px;border-radius:14px;font-size:12px;text-decoration:none}}
.tag-chip:hover{{background:#dfe8f2}}
.table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0;background:#fff;border:1px solid #dcdcdc;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.03)}}
table{{width:100%;border-collapse:collapse;font-size:13px;white-space:nowrap}}th,td{{border-bottom:1px solid #eee;padding:8px 12px;text-align:left}}
th{{background:#f8f9fa;color:#495057;font-weight:600}}
.btn-play{{display:inline-block;padding:3px 10px;background:#0056b3;color:#fff!important;border-radius:4px;font-size:11.5px;text-decoration:none}}
.btn-play:hover{{background:#004085;text-decoration:none}}
footer{{border-top:1px solid #dcdcdc;margin-top:40px;padding:24px 16px;font-size:12px;color:#666;text-align:center;background:#fff}}
@media (max-width:640px){{
  header,main,footer{{padding:10px 12px}}
  h1{{font-size:19px}}h2{{font-size:16px;margin:22px 0 8px}}table{{font-size:12px}}th,td{{padding:6px 8px}}
  .summary-stat{{flex:1 1 45%}}
}}
</style>
</head>
<body>
<header>
  <div class="site-title"><a href="/">← にじ歌サーチ（にじさんじ歌枠セトリ検索）</a></div>
  <h1>{e(artist_name)} の楽曲を歌ったにじさんじライバー一覧</h1>
</header>
<main>
  <nav class="breadcrumb" aria-label="パンくずリスト"><a href="{BASE_URL}/">ホーム</a> <span>&gt;</span> <a href="{BASE_URL}/#artist-list">アーティスト一覧</a> <span>&gt;</span> <strong>{e(artist_name)}</strong></nav>
  
  <div class="summary-box">
    <div class="summary-stat"><div class="summary-num">{total_songs:,}</div><div class="summary-label">総歌唱数（回）</div></div>
    <div class="summary-stat"><div class="summary-num">{repertoire_count:,}</div><div class="summary-label">歌われた楽曲数</div></div>
    <div class="summary-stat"><div class="summary-num">{liver_count:,}</div><div class="summary-label">歌唱ライバー人数</div></div>
  </div>

  <h2>にじさんじ歌枠でよく歌われる {e(artist_name)} の楽曲 TOP10</h2>
  <div class="top-ranking">
    {"".join(top_song_cards)}
  </div>

  <h2>{e(artist_name)} をよく歌うにじさんじライバー</h2>
  <div class="tag-list">
    {"".join(liver_chips)}
  </div>

  <h2>歌唱アーカイブ・セトリ一覧（新着順）</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>No.</th>
          <th>曲名</th>
          <th>歌唱ライバー</th>
          <th>公開日</th>
          <th>YouTube再生</th>
        </tr>
      </thead>
      <tbody>
        {"".join(table_rows)}
      </tbody>
    </table>
  </div>
</main>
<footer>
  <p><a href="{BASE_URL}/">にじ歌サーチ トップへ戻る</a> | <a href="{BASE_URL}/popular/">人気曲ランキング</a> | <a href="{BASE_URL}/utattemita/">歌ってみた一覧</a></p>
  <p style="margin-top:8px;color:#888;">本サイトはにじさんじ非公式ファンメイドサイトです。</p>
</footer>
</body>
</html>
"""
        with open(os.path.join(art_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        generated_urls.append(f"/artist/{quote(art_slug)}/")

    print(f"Generated {len(generated_urls)} artist pages.")

    # トップページ用のアーティスト一覧SSRセクションを作成
    top_artists_list = sorted(target_artists.items(), key=lambda kv: -len(kv[1]))[:60]
    art_chips_top = "".join(
        f'<li><a href="/artist/{quote(slugify(a))}/">{e(a)}</a> <span class="m">({len(rs):,}曲)</span></li>'
        for a, rs in top_artists_list
    )

    artist_ssr_block = f"""
    <section style="max-width:1240px;margin:24px auto;padding:16px;">
      <h2 id="artist-list" style="font-size:18px;margin-bottom:12px;border-left:4px solid #0056b3;padding-left:8px;">原曲アーティスト別 歌枠まとめ・歌唱楽曲一覧（上位60組）</h2>
      <ul class="c">{art_chips_top}</ul>
    </section>
    """

    index_html_path = os.path.join(ROOT, "index.html")
    with open(index_html_path, "r", encoding="utf-8") as f:
        idx_content = f.read()

    # SSR部分（ライバー一覧の後）に挿入
    if 'id="artist-list"' not in idx_content:
        target_pos = idx_content.find('</section>\n    <!--/SSR-->')
        if target_pos != -1:
            idx_content = idx_content[:target_pos+10] + "\n" + artist_ssr_block + idx_content[target_pos+10:]
            with open(index_html_path, "w", encoding="utf-8") as f:
                f.write(idx_content)
            print("Injected artist SSR block into index.html.")

    # sitemap.xml の更新
    sitemap_path = os.path.join(ROOT, "sitemap.xml")
    with open(sitemap_path, "r", encoding="utf-8") as f:
        sm_content = f.read()

    today_str = date.today().isoformat()
    new_urls_xml = []
    for u in generated_urls:
        loc = f"{BASE_URL}{u}"
        if loc not in sm_content:
            new_urls_xml.append(f"  <url><loc>{loc}</loc><lastmod>{today_str}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>\n")

    if new_urls_xml:
        insert_pos = sm_content.rfind("</urlset>")
        if insert_pos != -1:
            sm_content = sm_content[:insert_pos] + "".join(new_urls_xml) + sm_content[insert_pos:]
            with open(sitemap_path, "w", encoding="utf-8") as f:
                f.write(sm_content)
            print(f"Added {len(new_urls_xml)} artist URLs to sitemap.xml.")

if __name__ == "__main__":
    main()
