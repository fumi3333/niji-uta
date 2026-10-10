#!/usr/bin/env python3
"""sitemap.xml のURLを IndexNow に通知する（Bing / Yandex など対応検索エンジンに更新を即時に知らせる）。

- キーは ルート直下の <key>.txt（中身がキーそのもの）。無ければ何もしない
- 失敗してもワークフローは止めない
"""
import glob, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "nijiuta.fumiproject.dev"


def main():
    key = next((os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "*.txt"))
                if re.fullmatch(r"[0-9a-f]{16,128}", os.path.basename(p)[:-4])), None)
    if not key:
        print("no IndexNow key file; skip")
        return
    urls = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())
    for i in range(0, len(urls), 10000):
        body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls[i:i + 10000]}).encode()
        req = urllib.request.Request("https://api.indexnow.org/indexnow", body, {"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"IndexNow: submitted {len(urls[i:i + 10000])} urls -> HTTP {r.status}")
        except Exception as ex:  # 202/200 以外（429 など）でも収集自体は成功させる
            print(f"IndexNow failed: {ex}")


if __name__ == "__main__":
    main()
