import websocket
import json
import base64
import time

ws_url = 'ws://localhost:9223/devtools/page/866CB589469261121C8E6FE0CDF790EB'
ws = websocket.create_connection(ws_url)

def send_cmd(method, params=None):
    msg_id = int(time.time() * 1000) % 1000000
    msg = {'id': msg_id, 'method': method}
    if params:
        msg['params'] = params
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get('id') == msg_id:
            return resp

# ページリロード
send_cmd('Page.reload')
time.sleep(1)

# 検索入力
code_input = 'document.getElementById("searchInput").value = "シャルル"; document.getElementById("searchInput").dispatchEvent(new Event("input"));'
send_cmd('Runtime.evaluate', {'expression': code_input})
time.sleep(0.5)

# 調査
check_code = '''
JSON.stringify({
    firstLiverText: document.querySelector('.liver-text') ? document.querySelector('.liver-text').innerText : 'NOT_FOUND',
    cursor: document.querySelector('.liver-text') ? window.getComputedStyle(document.querySelector('.liver-text')).cursor : 'NONE',
    onclick: document.querySelector('.liver-text') ? (document.querySelector('.liver-text').onclick !== null) : false,
    url: window.location.href
})
'''
res = send_cmd('Runtime.evaluate', {'expression': check_code})
print('Evaluation result:', res.get('result', {}).get('value'))

shot_res = send_cmd('Page.captureScreenshot', {'format': 'png'})
img_b64 = shot_res.get('result', {}).get('data')
if img_b64:
    with open('C:/niji-uta/scratch/verify_plain_liver.png', 'wb') as f:
        f.write(base64.b64decode(img_b64))
    print('Screenshot saved successfully to C:/niji-uta/scratch/verify_plain_liver.png')

ws.close()
