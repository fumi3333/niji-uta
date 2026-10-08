# にじ歌サーチ（niji-uta）Claude Code 完全引き継ぎ仕様・開発レポート

> **更新日時**: 2026-10-08  
> **本番URL**: [https://nijiuta.fumiproject.dev/](https://nijiuta.fumiproject.dev/)  
> **GitHub Remote**: `https://github.com/fumi3333/niji-uta.git` (branch: `master`)  
> **ホスティング**: Vercel (Production連動)  
> **DNS / ドメイン**: Name.com (`fumiproject.dev`) CNAME → `cname.vercel-dns.com`

---

## 1. プロジェクト概要・理念・開発目的（Why）

### 1-1. 解決したい課題と背景
- **現状のVTuber歌動画・歌枠アクセスの分断**:
  - にじさんじ公式や非公式Wiki、個人ファン作成のGoogleスプレッドシートは存在するが、各ライバーごとに個別のWikiページや別々のシートに分断されている。
  - 「**この曲（例: ヴァンパイア、フォニイ、神っぽいな）を過去に歌ったにじさんじライバー全員を一覧で見たい**」
  - 「**あのライバーが歌枠の何分何秒で歌っていたか、秒数頭出しで今すぐ聴きたい**」
  - 「**ひらがな・カタカナ・ローマ字・あいまい検索で爆速に探したい**」
  というファンの根源的欲求を一括で満たす検索エンジンがWeb上に存在しなかった。
- **YouTube検索の限界**:
  - YouTube本体の検索では、歌枠（生配信アーカイブ）内の「何分何秒に歌ったか（セトリ）」は動画概要欄やコメント欄にしか記載されておらず、動画内の個別楽曲を横断的に検索することが極めて困難。

### 1-2. サービス理念とコア提供価値
- **「秒速で探せて、その場で秒数頭出し再生できる」全曲横断データベース**:
  1. **13,334件の歌唱パフォーマンスデータ**（歌枠アーカイブの歌い出しタイムスタンプ＋歌ってみた公式動画）を一箇所に集約。
  2. **クライアントサイド超爆速インクリメンタルサーチ**: 1文字打つごとにミリ秒単位で結果が絞り込まれる。
  3. **ひらがな・カタカナ・漢字・ローマ字の完全対応**: `pykakasi` による事前ヨミ付与により、「ふぉにい」でも「Phony」でも「フォニイ」でもヒット。
  4. **YouTube埋め込みインラインミニプレイヤー**: 外部に飛ばされず、ページ内で秒数頭出し即座再生＋次曲への連続再生対応。

### 1-3. ビジネス・SEO・収益化の狙い
- **ビッグキーワードのオーガニック流入獲得**:
  - 月間検索ボリューム数万規模のクエリ（「にじさんじ 歌枠」「にじさんじ 歌ってみた」「にじさんじ セトリ」「にじさんじ アーカイブ」等）をターゲットにしたSEO専用LP群を構築。
- **Google AdSenseによる収益化基盤**:
  - 高い滞在時間（連続再生機能）とページ内回遊により、Google AdSense審査を通過させ、安定的なアドセンス収益・ポートフォリオ実績を生み出す。
- **公式へのリスペクトと規約遵守**:
  - 動画ファイル自体の再配布・転載は一切行わず、公式YouTube API / iframe埋め込みを使用。公式チャンネル側の再生数・視聴時間に完全貢献する設計。

---

## 2. システムアーキテクチャ（How）

```
[GitHub Repo: fumi3333/niji-uta] (master)
       │
       ├─ Auto Cron Pipeline (.github/workflows/auto_update_songs.yml)
       │    └─ scripts/auto_update_dataset.py ──(毎日 JST 04:00)──> data/song_performances.json
       │
       └─ Vercel Webhook Auto-Deployment
            │
            ├─ 独自ドメイン: https://nijiuta.fumiproject.dev/
            │    ├─ index.html (メイン総合検索)
            │    ├─ /setlist/ (セトリ特化LP)
            │    ├─ /archive/ (アーカイブ特化LP)
            │    ├─ /utattemita/ (歌ってみた特化LP)
            │    ├─ /summary/ (まとめ特化LP)
            │    └─ /popular/ (人気ランキング特化LP)
            │
            └─ 旧ドメインリダイレクト (vercel.json)
                 └─ niji-uta.vercel.app/*  ──(301 Permanent)──>  nijiuta.fumiproject.dev/*
```

### 2-1. フロントエンド構成
- **ノーフレームワーク（Vanilla HTML / CSS / JavaScript）**:
  - React/Next.jsなどの過剰なビルドステップを廃し、HTML1枚・ブラウザネイティブの高速性を最重視。
  - 軽量JSON（約3.5MB gzip圧縮後で数百KB）を初回ロード時に非同期フェッチ（キャッシュ最適化）。
  - クライアント側メモリ内インデックスによる、ゼロレイテンシの爆速検索。

### 2-2. インフラ・DNS・ルーティング
- **ホスティング**: Vercel（Static File Hosting）
- **ドメイン**: `fumiproject.dev`（Name.comにて管理）
  - DNS設定: `nijiuta` CNAME → `cname.vercel-dns.com`
  - Vercel側設定: `nijiuta.fumiproject.dev` を Production Domain として紐付け済み。
- **SEO重複防止リダイレクト (`vercel.json`)**:
  - `niji-uta.vercel.app` へのアクセスをすべて `https://nijiuta.fumiproject.dev/$1` に301恒久転送し、検索エンジンの評価を独自ドメインに一本化。

---

## 3. データ基盤・クローリング・名寄せロジック

### 3-1. データセット仕様 (`data/song_performances.json`)
- **総レコード数**: 13,334件
- **収録ライバー数**: 94名（主要ライバー完全網羅）
- **ユニーク楽曲タイトル数**: 5,146曲
- **JSONスキーマ**:
```json
{
  "id": 1,
  "title": "亡国覚醒カタルシス",
  "artist": ".hack//Roots",
  "liver": "鈴木勝",
  "date": "歌枠アーカイブ",
  "timestamp": "歌い出し",
  "youtube_url": "https://youtu.be/tw8SrjLW5IQ",
  "kana_title": "ぼうこくかくせいかたるしす ボウコクカクセイカタルシス",
  "kana_artist": "",
  "kana_liver": "すずきまさる すずき まさる すずきかち スズキカチ"
}
```

### 3-2. 名寄せ・ヨミ付与パイプライン (`scripts/auto_update_dataset.py`)
- **`pykakasi` によるヨミ自動生成**:
  - 楽曲名・ライバー名の「ひらがな・カタカナ・ヘボン式ローマ字」を事前にすべて展開し、`kana_title`, `kana_liver` に結合して保存。
  - フロントエンド側で「ふぉにい」と打った瞬間に、タイトル「フォニイ」が正規表現・部分一致で即座にヒットする。
- **ストップワード自動除外ロジック**:
  - 検索窓に「にじさんじ 歌枠」「歌ってみた」などのビッグキーワードが入力された際、無用なフィルタリングで全件消滅しないよう、フロントエンド側で「にじさんじ」「歌枠」「歌ってみた」「まとめ」「セトリ」をストップワードとして抽出し、クエリから除外して検索する。

---

## 4. SEO戦略・全URLマップ・構造化データ

### 4-1. 6大ページ構成とターゲットクエリ
| URLパス | H1見出し | ターゲット検索クエリ |
| :--- | :--- | :--- |
| `/` (`index.html`) | にじさんじ 歌ってみた・歌枠 全曲横断データベース | `にじさんじ 歌`, `にじさんじ 歌枠 検索` |
| `/setlist/` | にじさんじ 歌枠 セトリ（セットリスト）一覧まとめ | `にじさんじ セトリ`, `にじさんじ 歌枠 セットリスト` |
| `/archive/` | にじさんじ 歌枠 アーカイブ・歌唱楽曲一覧検索 | `にじさんじ 歌枠 アーカイブ`, `にじさんじ 配信 歌` |
| `/utattemita/` | にじさんじ 歌ってみた 一覧・カバー楽曲まとめ | `にじさんじ 歌ってみた`, `にじさんじ カバー曲` |
| `/summary/` | にじさんじ 歌ってみた・歌枠 おすすめ楽曲まとめ一覧 | `にじさんじ 歌 まとめ`, `にじさんじ おすすめ 歌枠` |
| `/popular/` | にじさんじ 歌枠 人気曲・定番カバー曲ランキング一覧 | `にじさんじ 歌 定番`, `にじさんじ 人気曲` |

### 4-2. SEO技術要素
- **Canonical URL**: 全ページに絶対パス（`https://nijiuta.fumiproject.dev/...`）を明記。
- **sitemap.xml / robots.txt**: 全6ページを登録済み。優先度（priority 1.0 〜 0.8）を指定。
- **構造化データ (JSON-LD)**:
  - `Dataset` スキーマ（13,334件の楽曲データセットとしてGoogleに認識させる）
  - `WebSite` + `SearchAction` スキーマ（検索窓付きサイトリンクの獲得を狙う）
- **Search Console登録状況**:
  - `fumiproject.dev` ドメインプロパティにてDNS TXT認証済み。
  - サイトマップ送信完了、URL検査およびインデックスリクエスト送信済み。

---

## 5. UI/UX実装詳細

### 5-1. 爆速インクリメンタルサーチ
- 複数単語のスペース区切りAND検索対応。
- ひらがな・カタカナ・漢字・ローマ字のあいまい判定。
- ライバー名クリックで即座にそのライバーの歌唱曲に絞り込み。

### 5-2. YouTubeインラインミニプレイヤー & 連続再生
- 検索結果の「今すぐ聴く」または動画リンクをクリックすると、画面下部（モバイルでは画面下固定、PCでは右下）にミニプレイヤーが出現。
- YouTubeの `t=秒数` パラメータを解釈し、指定タイムスタンプから頭出し再生。
- **連続再生（Sequential Playback）**:
  - 「次の曲」「前の曲」ボタンを完備。
  - 現在再生中の曲がリスト上で青くハイライト（Active Row Highlight）され、自動スクロールで追従。
  - 1曲が終わると次の検索結果を自動再生するループ/連続再生モードを実装済み。

---

## 6. 解析・計測基盤とAdSenseロードマップ

### 6-1. 計測環境
- **Microsoft Clarity**: プロジェクトID `yu9kj4tdga`
  - 全6ページ（トップ + 5大LP）に導入完了。
  - ユーザーのクリック箇所、スクロール深度、離脱ポイントのセッション録画を自動追跡中。
- **Google Search Console**:
  - クロール状況、クリック数、インプレッション数、掲載順位を追跡中。

### 6-2. Google AdSense 審査・収益化ロードマップ
1. **インデックス浸透と初期トラフィック獲得**（1〜2週間）:
   - GSCで各LPがインデックスされ、デイリーで数十〜数百セッションの自然検索流入を確認。
2. **ポリシー準拠ページの整備**:
   - プライバシーポリシーページ、お問い合わせ導線（Google FormまたはTwitter）、運営者情報（ZAX名義）の設置。
   - ※著作権ガイドラインに関する「YouTube公式埋め込みによる還元モデル」の明記。
3. **AdSense審査申請**:
   - 独自ドメイン `fumiproject.dev` 配下、またはサブドメインとして申請。
   - 審査通過後、検索結果上部・下部にレスポンシブ広告ユニットを配置。

---

## 7. 自動更新パイプライン（GitHub Actions）

- **ワークフロー定義**: `.github/workflows/auto_update_songs.yml`
- **YouTube Data API v3 連携状態**:
  - **APIキー発行・制限設定済み**: Google Cloudプロジェクト `gsc-reader-510905` にて YouTube Data API v3 専用の制限付きキーを発行完了。
  - **GitHub Secrets登録済み**: リポジトリの Actions Secrets に `YOUTUBE_API_KEY` として登録完了済み（ワークフロー内から `${{ secrets.YOUTUBE_API_KEY }}` で参照可能）。
- **実行契機**:
  - 毎日 日本時間 午前4:00（UTC 19:00）に定期自動実行。
  - 手動実行（GitHub Web画面の「Run workflow」ボタン）にも対応。
- **動作**:
  1. Python 3.11 環境をセットアップ
  2. `pip install pykakasi google-api-python-client`
  3. `python scripts/auto_update_dataset.py` を実行して最新データ収集・YouTube新着動画（歌枠・歌ってみた）の自動パース・名寄せ
  4. 差分があれば `git commit -m "chore(data): auto-update song database [skip ci]"` して `origin master` へ自動 push
  5. Vercelがmasterへのpushを検知して本番へ自動デプロイ


---

## 8. Claude Code 開発・運用引き継ぎコマンド集

### ローカル開発・確認
```bash
# リポジトリへ移動
cd c:\niji-uta

# ローカルHTTPサーバー起動（任意のポート）
python -m http.server 8080
# ブラウザで http://localhost:8080/ を確認
```

### データ更新・スクリプトテスト
```bash
# データセットの整合性チェック
python -c "import json; d=json.load(open('data/song_performances.json', encoding='utf-8')); print(len(d))"

# データ収集パイプラインの手動実行
python scripts/auto_update_dataset.py
```

### Git デプロイ
```bash
git add .
git commit -m "feat: your change description"
git push origin master
# -> Vercelが自動的に検知して本番更新完了
```

---

## 9. 今後の改修・機能拡張ToDo（Next Steps）

1. **YouTubeコメント欄・概要欄からの自動タイムスタンプ抽出強化**:
   - 新規歌枠アーカイブについて、YouTube Data API v3またはスクレイピングを用い、概要欄・固定コメントの「00:00 曲名」形式のタイムスタンプを自動パースして新規追加するパイプラインの拡充。
2. **お気に入り（ブックマーク）機能のローカルストレージ保存**:
   - ユーザーが気に入った楽曲・歌枠をブラウザの `localStorage` に保存し、自分専用のプレイリストを作れる機能。
3. **Google AdSense / プライバシーポリシー設置**:
   - 審査通過用の固定フッターリンク（プライバシーポリシー、利用規約、問い合わせ）の追加。
4. **ソーシャルシェア（OGP画像自動生成）**:
   - 「葛葉の歌枠全曲一覧」「フォニイを歌ったにじさんじライバー一覧」などの結果画面で動的OGP画像を生成し、X(Twitter)シェアを促進。
