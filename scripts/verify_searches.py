import urllib.request
import json
import base64
import time
import websocket

# CDPで現在の8089タブを取得
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

# リロード
send_msg({'id': 1, 'method': 'Page.reload'})
time.sleep(1)

# テスト1: 'KING gnu'（大文字小文字空白あり）で検索
code1 = 'document.getElementById("searchInput").value = "KING gnu"; document.getElementById("searchInput").dispatchEvent(new Event("input"));'
send_msg({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': code1}})
time.sleep(0.5)

r_count1 = send_msg({'id': 3, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.getElementById("countIndicator").innerText'}})
print('KING gnu count:', r_count1.get('result', {}).get('value'))

# テスト2: 'kinggnu'（空白なし）で検索
code2 = 'document.getElementById("searchInput").value = "kinggnu"; document.getElementById("searchInput").dispatchEvent(new Event("input"));'
send_msg({'id': 4, 'method': 'Runtime.evaluate', 'params': {'expression': code2}})
time.sleep(0.5)

r_count2 = send_msg({'id': 5, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.getElementById("countIndicator").innerText'}})
print('kinggnu (no space) count:', r_count2.get('result', {}).get('value'))

# テスト3: '白日' で検索してライバー一覧をキャプチャ
code3 = 'document.getElementById("searchInput").value = "白日"; document.getElementById("searchInput").dispatchEvent(new Event("input"));'
send_msg({'id': 6, 'method': 'Runtime.evaluate', 'params': {'expression': code3}})
time.sleep(0.5)

r_count3 = send_msg({'id': 7, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.getElementById("countIndicator").innerText'}})
print('Hakujitsu count:', r_count3.get('result', {}).get('value'))

shot = send_msg({'id': 8, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}})
with open('C:/niji-uta/scratch/hakujitsu_search_verified.png', 'wb') as f:
    f.write(base64.b64decode(shot['result']['data']))
print('Saved Hakujitsu screenshot!')

# テスト4: 'kinggnu' でのスクリーンショット
send_msg({'id': 9, 'method': 'Runtime.evaluate', 'params': {'expression': code2}})
time.sleep(0.5)
shot2 = send_msg({'id': 10, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}})
with open('C:/niji-uta/scratch/kinggnu_search_verified.png', 'wb') as f:
    f.write(base64.b64decode(shot2['result']['data']))
print('Saved kinggnu screenshot!')

ws.close()
