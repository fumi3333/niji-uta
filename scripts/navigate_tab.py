import urllib.request
import json

def navigate_tab(tab_id, target_url):
    url = f"http://127.0.0.1:9223/json/navigate?targetId={tab_id}&url={urllib.parse.quote(target_url)}"
    req = urllib.request.urlopen(url)
    res = json.loads(req.read().decode('utf-8'))
    print(f"Navigated tab {tab_id} to {target_url}")
    return res

if __name__ == '__main__':
    # 既存のローカルサーバータブ（866CB589469261121C8E6FE0CDF790EB）をVercel新規作成へナビゲート
    tab_id = "866CB589469261121C8E6FE0CDF790EB"
    navigate_tab(tab_id, "https://vercel.com/new/import?s=https%3A%2F%2Fgithub.com%2Ffumi3333%2Fniji-uta")
