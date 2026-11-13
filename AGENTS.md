# AGENTS.md

## 進捗ハブ：新しいセッションはまずここ（Claude・Antigravity・Muse 共通・最優先）

全プロダクト・大学課題・メール相手の現在地は `C:\Mind sort-log\hub\INDEX.md`（GitHub: `fumi3333/zax-thought-log` の `hub/INDEX.md`）にまとまっている。作業ログや過去メモを全文検索せず、まずここを見る。
- 「〇〇の続き」と言われたら：`hub/INDEX.md` → 該当行の「詳細」1枚だけ読んで着手する
- ローカル環境（Windows）：`C:\Mind sort-log\hub\INDEX.md` を直接読み書きし、終了時は詳細ファイルと `INDEX.md` の該当行を更新して `C:\Mind sort-log` を commit & push する
- クラウド環境（`C:\Mind sort-log` がローカルにない場合）：`gh api repos/fumi3333/zax-thought-log/contents/hub/INDEX.md` や `git clone --depth 1 https://github.com/fumi3333/zax-thought-log.git` で `hub/INDEX.md` と該当詳細ファイルを参照し、終了時に更新＆push（pushできない環境では更新内容を最終回答に明記）
- 数字の正本は `思考/CURRENT_PRODUCTS.md`（`zax-thought-log` 内）
