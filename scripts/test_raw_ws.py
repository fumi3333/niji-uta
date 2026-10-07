import websocket
import json
import time

# 既存のタブ（1番目のページタブ）にアタッチして Vercel へ navigate するスクリプト
res = json.loads(websocket.create_connection("ws://127.0.0.1:9223/devtools/page/866CB589469261121C8E6FE0CDF790EB").recv())
print("Connected directly to tab via raw websocket!")
