import urllib.request
import json

def open_new_tab(url_to_open):
    url = f"http://127.0.0.1:9223/json/new?{urllib.parse.quote(url_to_open)}"
    req = urllib.request.Request(url, method="PUT")
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print("Opened new tab:", res.get('id'), "->", res.get('url'))
    return res

if __name__ == '__main__':
    open_new_tab("https://vercel.com/new/import?s=https%3A%2F%2Fgithub.com%2Ffumi3333%2Fniji-uta")
    open_new_tab("https://www.name.com/account/domain")
