import urllib.request
import json

def get_current_tabs():
    res = json.loads(urllib.request.urlopen('http://127.0.0.1:9223/json').read().decode('utf-8'))
    for t in res:
        u = t.get('url', '')
        if 'vercel' in u or 'name' in u or 'google' in u:
            # 安全なASCII出力
            safe_title = t.get('title', '').encode('ascii', errors='ignore').decode('ascii')
            print(f"Tab ID: {t.get('id')} | Title: {safe_title[:30]} | URL: {u[:100]}")

if __name__ == '__main__':
    get_current_tabs()
