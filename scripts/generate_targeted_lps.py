import os
import json
import urllib.parse
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(CURRENT_DIR, "..")
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "song_performances.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    songs = json.load(f)

print(f"Loaded {len(songs)} songs.")

# 1. ターゲット固定LP（一般クエリの需要TOP5）
STATIC_PAGES = [
    {
        "dir": "setlist",
        "slug": "index.html",
        "url_path": "setlist/",
        "title": "にじさんじ 歌枠セトリ検索 - 全ライバーのセットリスト一覧データベース",
        "h1": "にじさんじ 歌枠セトリ検索・セットリスト一覧",
        "desc": "にじさんじ所属ライバーの歌枠セットリスト（セトリ）を網羅検索。曲名・ライバー・歌い出しタイムスタンプ付きで即座に試聴可能。",
        "filter_type": "all",
        "filter_val": ""
    },
    {
        "dir": "archive",
        "slug": "index.html",
        "url_path": "archive/",
        "title": "にじさんじ 歌枠アーカイブ一覧 - 過去の歌配信タイムスタンプまとめ",
        "h1": "にじさんじ 歌枠アーカイブ・歌配信一覧",
        "desc": "にじさんじライバーの過去の歌枠配信アーカイブを時系列順に検索。YouTubeの該当歌唱秒数へ直飛び再生。",
        "filter_type": "all",
        "filter_val": ""
    },
    {
        "dir": "utattemita",
        "slug": "index.html",
        "url_path": "utattemita/",
        "title": "にじさんじ 歌ってみた一覧 - カバー曲・動画まとめデータベース",
        "h1": "にじさんじ 歌ってみた一覧・カバー曲まとめ",
        "desc": "にじさんじライバーの歌ってみた動画・カバー曲をアーティスト・曲名から横断検索。原曲情報・歌唱者一覧を網羅。",
        "filter_type": "all",
        "filter_val": ""
    },
    {
        "dir": "summary",
        "slug": "index.html",
        "url_path": "summary/",
        "title": "にじさんじ 歌唱曲まとめ - 所属ライバーが歌った全楽曲一覧",
        "h1": "にじさんじ 歌唱曲まとめ・歌唱履歴データベース",
        "desc": "にじさんじライバーがこれまでに歌った13,000曲以上の歌唱履歴を完全集約。ボカロ・J-POP・アニソンを爆速検索。",
        "filter_type": "all",
        "filter_val": ""
    },
    {
        "dir": "popular",
        "slug": "index.html",
        "url_path": "popular/",
        "title": "にじさんじ 歌枠定番曲・人気曲一覧 - よく歌われている曲ランキング",
        "h1": "にじさんじ 歌枠定番曲・よく歌われる人気曲一覧",
        "desc": "にじさんじの歌枠で最も多く歌われている人気曲・定番曲（シャルル、ヴァンパイア、KING、フォニイ等）の歌唱ライバー一覧。",
        "filter_type": "popular",
        "filter_val": ""
    }
]

# 2. テンプレートHTML生成
def generate_html(page_meta):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_meta['title']}</title>
  <meta name="description" content="{page_meta['desc']}">
  <meta name="keywords" content="にじさんじ,歌枠,セトリ,歌ってみた,セトリ検索,アーカイブ,VTuber,にじ歌">
  <meta property="og:title" content="{page_meta['title']}">
  <meta property="og:description" content="{page_meta['desc']}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://nijiuta.fumiproject.dev/{page_meta['url_path']}">
  <link rel="canonical" href="https://nijiuta.fumiproject.dev/{page_meta['url_path']}">
  
  <style>
    :root {{
      --bg: #ffffff;
      --text: #1a1a1a;
      --text-muted: #666666;
      --border: #dcdcdc;
      --border-dark: #b0b0b0;
      --header-bg: #f4f5f7;
      --row-hover: #f0f4f9;
      --row-alt: #fafbfc;
      --link: #0056b3;
      --accent: #d32f2f;
      --font-mono: "SF Mono", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: var(--font-sans); background: var(--bg); color: var(--text); line-height: 1.4; font-size: 14px; }}
    header {{ border-bottom: 2px solid var(--border-dark); background: #fff; padding: 12px 16px; }}
    .header-inner {{ max-width: 1240px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }}
    h1 {{ font-size: 18px; font-weight: 700; color: #111; }}
    .nav-link {{ color: var(--link); text-decoration: none; font-size: 13px; font-weight: 600; }}
    .nav-link:hover {{ text-decoration: underline; }}
    
    .intro-banner {{ max-width: 1240px; margin: 12px auto 0 auto; padding: 0 16px; }}
    .intro-box {{ background: #f8f9fa; border: 1px solid var(--border); border-radius: 4px; padding: 12px 16px; font-size: 13px; color: #444; }}
    
    .controls-wrapper {{ background: #fff; border-bottom: 1px solid var(--border); padding: 10px 16px; position: sticky; top: 0; z-index: 10; }}
    .controls {{ max-width: 1240px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
    .search-box {{ flex: 1 1 260px; }}
    input[type="text"] {{ width: 100%; padding: 8px 10px; font-size: 14px; border: 1px solid var(--border-dark); border-radius: 3px; outline: none; }}
    input[type="text"]:focus {{ border-color: var(--link); box-shadow: 0 0 0 2px rgba(0,86,179,0.15); }}
    
    .tag-btn {{ background: #f1f3f5; border: 1px solid #ced4da; border-radius: 12px; padding: 3px 10px; font-size: 11px; color: #333; cursor: pointer; }}
    .tag-btn:hover {{ background: #e2e6ea; color: var(--link); }}

    main {{ max-width: 1240px; margin: 0 auto; padding: 16px; }}
    .table-container {{ border: 1px solid var(--border-dark); background: #fff; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }}
    th {{ background: var(--header-bg); border-bottom: 2px solid var(--border-dark); border-right: 1px solid var(--border); padding: 8px 12px; font-weight: 600; white-space: nowrap; }}
    td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); vertical-align: middle; }}
    tr:nth-child(even) {{ background: var(--row-alt); }}
    tr:hover {{ background: var(--row-hover) !important; }}
    tr.row-playing {{ background: #e8f0fe !important; border-left: 3px solid var(--link); }}

    .btn-play {{ display: inline-block; background: #fff; color: var(--accent); border: 1px solid var(--accent); font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 3px; cursor: pointer; text-decoration: none; }}
    .btn-play:hover {{ background: var(--accent); color: #fff; }}
    .btn-play.playing {{ background: var(--accent); color: #fff; animation: pulse 1.5s infinite; }}
    @keyframes pulse {{
      0% {{ opacity: 1; }}
      50% {{ opacity: 0.7; }}
      100% {{ opacity: 1; }}
    }}

    /* フローティングミニプレーヤー */
    .mini-player-container {{ position: fixed; bottom: 20px; right: 20px; width: 360px; background: #1e1e1e; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); z-index: 1000; overflow: hidden; display: none; border: 1px solid #333; }}
    .mini-player-header {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #2d2d2d; color: #fff; font-size: 12px; }}
    .mini-player-title {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 190px; font-weight: 500; color: #eee; }}
    .mini-player-btn {{ cursor: pointer; background: #444; border: 1px solid #555; color: #fff; border-radius: 3px; padding: 2px 6px; font-size: 11px; line-height: 1; display: inline-flex; align-items: center; justify-content: center; transition: background 0.1s; }}
    .mini-player-btn:hover {{ background: #666; }}
    .mini-player-close {{ cursor: pointer; background: none; border: none; color: #aaa; font-size: 16px; line-height: 1; padding: 0 4px; }}
    .mini-player-close:hover {{ color: #fff; }}
    .mini-player-iframe-wrap {{ position: relative; width: 100%; padding-top: 56.25%; }}
    .mini-player-iframe-wrap iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }}

    footer {{ border-top: 1px solid var(--border); margin-top: 40px; padding: 24px 16px; background: #fafafa; font-size: 12px; color: var(--text-muted); text-align: center; }}
    .footer-links {{ margin-top: 8px; display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }}
    .footer-links a {{ color: var(--text-muted); text-decoration: none; }}
    .footer-links a:hover {{ text-decoration: underline; color: var(--link); }}
  </style>
</head>
<body>

  <header>
    <div class="header-inner">
      <h1>{page_meta['h1']}</h1>
      <div>
        <a href="../" class="nav-link">← にじ歌サーチ トップへ</a>
      </div>
    </div>
  </header>

  <div class="intro-banner">
    <div class="intro-box">
      <strong>{page_meta['h1']}</strong><br>
      {page_meta['desc']} 曲名やライバー名でリアルタイム絞り込みが可能です。
    </div>
  </div>

  <div class="controls-wrapper">
    <div class="controls">
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="曲名、アーティスト、ライバー名で絞り込み (ひらがな対応)" autocomplete="off">
      </div>
      <div style="font-size: 12px; font-family: var(--font-mono); color: var(--text-muted);" id="countIndicator">
        表示: 0 / 0 件
      </div>
    </div>
    <div style="max-width: 1240px; margin: 8px auto 0 auto; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 12px;">
      <span style="color: var(--text-muted); font-size: 11px;">人気の曲:</span>
      <button type="button" class="tag-btn" onclick="setQuick('シャルル')">シャルル</button>
      <button type="button" class="tag-btn" onclick="setQuick('ヴァンパイア')">ヴァンパイア</button>
      <button type="button" class="tag-btn" onclick="setQuick('KING')">KING</button>
      <button type="button" class="tag-btn" onclick="setQuick('フォニイ')">フォニイ</button>
      <button type="button" class="tag-btn" onclick="setQuick('')" style="background:#fff;">クリア</button>
    </div>
  </div>

  <main>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 45px; text-align: right;">No.</th>
            <th>曲名</th>
            <th>本家アーティスト</th>
            <th>歌唱ライバー</th>
            <th>配信日</th>
            <th>開始秒数</th>
            <th style="width: 100px; text-align: center;">再生</th>
          </tr>
        </thead>
        <tbody id="tableBody">
          <tr><td colspan="7" style="text-align: center; padding: 30px; color: #888;">データを読み込み中...</td></tr>
        </tbody>
      </table>
    </div>
  </main>

  <div id="miniPlayer" class="mini-player-container">
    <div class="mini-player-header">
      <div style="display:flex; align-items:center; gap:6px; overflow:hidden;">
        <button type="button" class="mini-player-btn" onclick="playPrevSong()" title="前の曲">⏮</button>
        <button type="button" class="mini-player-btn" onclick="playNextSong()" title="次の曲">⏭</button>
        <span id="miniPlayerTitle" class="mini-player-title">再生中...</span>
      </div>
      <div style="display:flex; align-items:center; gap:6px;">
        <a id="miniPlayerYtLink" href="#" target="_blank" rel="noopener" class="mini-player-btn" title="YouTubeで開く" style="text-decoration:none; font-size:11px;">↗</a>
        <button type="button" class="mini-player-close" onclick="closePlayer()" title="閉じる">✕</button>
      </div>
    </div>
    <div class="mini-player-iframe-wrap">
      <div id="playerSlot"></div>
    </div>
  </div>

  <footer>
    <p>当サイトは有志ファンによる非公式検索ツールです。ANYCOLOR株式会社とは一切関係ありません。</p>
    <div class="footer-links">
      <a href="../">トップページ</a>
      <a href="../setlist/">歌枠セトリ検索</a>
      <a href="../archive/">歌枠アーカイブ</a>
      <a href="../utattemita/">歌ってみた一覧</a>
      <a href="../summary/">歌唱曲まとめ</a>
      <a href="../popular/">定番曲ランキング</a>
    </div>
  </footer>

  <script>
    let records = [];
    let filtered = [];
    let currentPlayingIndex = -1;

    async function init() {{
      const res = await fetch('../data/song_performances.json');
      records = await res.json();
      applyFilter();
    }}

    function setQuick(w) {{
      document.getElementById('searchInput').value = w;
      applyFilter();
    }}

    function applyFilter() {{
      const q = document.getElementById('searchInput').value.trim().toLowerCase();
      filtered = records.filter(r => {{
        if (!q) return true;
        const norm = (str) => String(str || '').toLowerCase().replace(/[\\s\\u3000\\-_]+/g, '');
        const nq = norm(q);
        return norm(r.title).includes(nq) || 
               norm(r.artist).includes(nq) || 
               norm(r.liver).includes(nq) || 
               norm(r.kana_title).includes(nq) || 
               norm(r.kana_artist).includes(nq) || 
               norm(r.kana_liver).includes(nq);
      }});

      document.getElementById('countIndicator').textContent = `表示: ${{filtered.length.toLocaleString()}} / ${{records.length.toLocaleString()}} 件`;
      render();
    }}

    function render() {{
      const tbody = document.getElementById('tableBody');
      const rows = filtered.slice(0, 150);
      if (rows.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:30px; color:#888;">該当する曲が見つかりませんでした</td></tr>';
        return;
      }}
      tbody.innerHTML = rows.map((r, i) => {{
        const isCurrent = currentPlayingIndex === i;
        const timeLabel = r.timestamp && r.timestamp !== '歌い出し' ? escapeHtml(r.timestamp) : '再生';
        return `
          <tr class="${{isCurrent ? 'row-playing' : ''}}" data-idx="${{i}}">
            <td style="text-align:right; color:#666; font-family:var(--font-mono);">${{i+1}}</td>
            <td style="font-weight:600; color:#111;">${{escapeHtml(r.title)}}</td>
            <td style="color:#444;">${{escapeHtml(r.artist)}}</td>
            <td><span style="font-weight:500;">${{escapeHtml(r.liver)}}</span></td>
            <td style="color:#666; font-family:var(--font-mono); font-size:12px;">${{escapeHtml(r.date || '-')}}</td>
            <td style="color:#333; font-family:var(--font-mono); font-size:12px;">${{escapeHtml(r.timestamp || '-')}}</td>
            <td style="text-align:center;">
              <button type="button" class="btn-play ${{isCurrent ? 'playing' : ''}}" onclick="playRow(${{i}})">
                ${{isCurrent ? '● 再生中' : '▶ ' + timeLabel}}
              </button>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function escapeHtml(s) {{
      return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    function playRow(idx) {{
      if (idx >= 0 && idx < filtered.length) {{
        currentPlayingIndex = idx;
        const item = filtered[idx];
        playSong(item.youtube_url, item.title, item.liver);
        render();
      }}
    }}

    function playNextSong() {{
      if (filtered.length === 0) return;
      const nextIdx = (currentPlayingIndex + 1) % Math.min(filtered.length, 150);
      playRow(nextIdx);
    }}

    function playPrevSong() {{
      if (filtered.length === 0) return;
      const maxLen = Math.min(filtered.length, 150);
      const prevIdx = (currentPlayingIndex - 1 + maxLen) % maxLen;
      playRow(prevIdx);
    }}

    function playSong(u, t, l) {{
      const m = u.match(/(?:youtu\\.be\\/|v=|\\/embed\\/|\\/watch\\?v=)([a-zA-Z0-9_-]{{11}})/);
      if (!m) return window.open(u, '_blank');
      let start = 0;
      if (u.includes('t=')) {{
        const ms = u.match(/t=(?:(\\d+)m)?(?:(\\d+)s)?/);
        if (ms && (ms[1] || ms[2])) {{
          start = (ms[1] ? parseInt(ms[1])*60 : 0) + (ms[2] ? parseInt(ms[2]) : 0);
        }} else {{
          const sec = u.match(/t=(\\d+)/);
          if (sec) start = parseInt(sec[1]);
        }}
      }}
      document.getElementById('miniPlayerTitle').textContent = `${{t}} / ${{l}}`;
      const ytLinkEl = document.getElementById('miniPlayerYtLink');
      if (ytLinkEl) ytLinkEl.href = u;
      document.getElementById('playerSlot').innerHTML = `<iframe src="https://www.youtube.com/embed/${{m[1]}}?autoplay=1&start=${{start}}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
      document.getElementById('miniPlayer').style.display = 'block';
    }}

    function closePlayer() {{
      document.getElementById('playerSlot').innerHTML = '';
      document.getElementById('miniPlayer').style.display = 'none';
      currentPlayingIndex = -1;
      render();
    }}

    document.getElementById('searchInput').addEventListener('input', applyFilter);
    init();
  </script>
</body>
</html>
"""

# HTML書き出し & sitemap.xml 更新
sitemap_urls = [
    "https://nijiuta.fumiproject.dev/",
]

for p in STATIC_PAGES:
    target_dir = os.path.join(PROJECT_ROOT, p["dir"])
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, p["slug"])
    html_content = generate_html(p)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated: {target_file}")
    sitemap_urls.append(f"https://nijiuta.fumiproject.dev/{p['url_path']}")

# 更新された sitemap.xml を書き出し
today_str = datetime.now().strftime("%Y-%m-%d")
sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in sitemap_urls:
    sitemap_xml.append(f"""  <url>
    <loc>{u}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{'1.0' if u == 'https://nijiuta.fumiproject.dev/' else '0.8'}</priority>
  </url>""")
sitemap_xml.append('</urlset>')

with open(os.path.join(PROJECT_ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write("\n".join(sitemap_xml))

print(f"Updated sitemap.xml with {len(sitemap_urls)} pages!")
