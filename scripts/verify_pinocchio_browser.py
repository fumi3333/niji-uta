import urllib.request
import json
import base64
import time
import websocket

req = urllib.request.Request('http://localhost:9223/json')
with urllib.request.urlopen(req) as resp:
    tabs = json.loads(resp.read().decode())
    ws_url = None
    for t in tabs:
        if '8089' in t.get('url', ''):
            ws_url = t.get('webSocketDebuggerUrl')
            break

ws = websocket.create_connection(ws_url, timeout=5)

def send_msg(m):
    ws.send(json.dumps(m))
    while True:
        r = json.loads(ws.recv())
        if r.get('id') == m['id']:
            return r

send_msg({'id': 1, 'method': 'Page.reload'})
time.sleep(1)

# 'ピノキオピー' で検索
code = 'document.getElementById("searchInput").value = "ピノキオピー"; document.getElementById("searchInput").dispatchEvent(new Event("input"));'
send_msg({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': code}})
time.sleep(0.5)

shot = send_msg({'id': 3, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}})
with open('C:/niji-uta/scratch/pinocchio_search_verified.png', 'wb') as f:
    f.write(base64.b64decode(shot['result']['data']))
print('Saved pinocchio screenshot!')

# '神っぽいな' で検索
code2 = 'document.getElementById("searchInput").value = "神っぽいな"; document.getElementById("searchInput").dispatchEvent(new Event("input"));'
send_msg({'id': 4, 'method': 'Runtime.evaluate', 'params': {'expression': code2}})
time.sleep(0.5)

shot2 = send_msg({'id': 5, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}})
with open('C:/niji-uta/scratch/kamippoi_search_verified.png', 'wb') as f:
    f.write(base64.b64decode(shot2['result']['data']))
print('Saved kamippoi screenshot!')

ws.close()
