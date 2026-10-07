import urllib.request
import json
import base64
import websocket

req = urllib.request.Request('http://localhost:9223/json')
with urllib.request.urlopen(req) as resp:
    tabs = json.loads(resp.read().decode())
    ws_url = None
    for t in tabs:
        if '8089' in t.get('url', ''):
            ws_url = t.get('webSocketDebuggerUrl')
            break

if not ws_url:
    print('Tab not found')
    exit(1)

ws = websocket.create_connection(ws_url, timeout=5)

def send_msg(m):
    ws.send(json.dumps(m))
    while True:
        r = json.loads(ws.recv())
        if r.get('id') == m['id']:
            return r

# スクリーンショット撮影
r = send_msg({'id': 1, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}})
b64 = r['result']['data']
with open('C:/niji-uta/scratch/verify_plain_liver.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('Screenshot saved!')

# DOMの検査
r2 = send_msg({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.querySelector(".liver-text") ? window.getComputedStyle(document.querySelector(".liver-text")).cursor : "NONE"'}})
print('Liver text cursor:', r2.get('result', {}).get('value'))

r3 = send_msg({'id': 3, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.querySelector(".liver-badge") !== null'}})
print('Liver badge exists?:', r3.get('result', {}).get('value'))

r4 = send_msg({'id': 4, 'method': 'Runtime.evaluate', 'params': {'expression': 'window.location.href'}})
print('Current URL:', r4.get('result', {}).get('value'))

ws.close()
