import urllib.request
import json
import base64
import websockets
import asyncio

async def test_ui():
    # 新規タブを開く
    url = "http://localhost:8089/"
    res = urllib.request.urlopen(urllib.request.Request(f"http://localhost:9223/json/new?{url}", method="PUT"))
    tab = json.loads(res.read().decode())
    print("Opened tab:", tab["id"])
    
    ws_url = tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        # 画面レンダリング待機
        await asyncio.sleep(2)
        
        # スクリーンショット撮影
        ss_cmd = {
            "id": 1,
            "method": "Page.captureScreenshot",
            "params": {"format": "png"}
        }
        await ws.send(json.dumps(ss_cmd))
        ss_res = await ws.recv()
        ss_data = json.loads(ss_res)
        img_b64 = ss_data.get("result", {}).get("data", "")
        if img_b64:
            with open(r"C:\Users\hrfmt\.gemini\antigravity\brain\39f64cff-3b02-47c9-9d6a-adc41a23b3fc\scratch\niji_uta_live_preview.png", "wb") as f:
                f.write(base64.b64decode(img_b64))
            print("Saved scratch/niji_uta_live_preview.png")

        # 検索窓に「フォニイ」と入力して絞り込みをテスト
        eval_cmd = {
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                (() => {
                    const input = document.getElementById('searchInput');
                    input.value = 'フォニイ';
                    input.dispatchEvent(new Event('input'));
                    return document.getElementById('countIndicator').innerText;
                })()
                """
            }
        }
        await ws.send(json.dumps(eval_cmd))
        eval_res = await ws.recv()
        eval_data = json.loads(eval_res)
        print("Search count result:", eval_data.get("result", {}).get("result", {}).get("value"))
        
        await asyncio.sleep(1)
        
        # 検索結果のスクリーンショット
        await ws.send(json.dumps(ss_cmd))
        ss_res2 = await ws.recv()
        ss_data2 = json.loads(ss_res2)
        img_b64_2 = ss_data2.get("result", {}).get("data", "")
        if img_b64_2:
            with open(r"C:\Users\hrfmt\.gemini\antigravity\brain\39f64cff-3b02-47c9-9d6a-adc41a23b3fc\scratch\niji_uta_search_phony.png", "wb") as f:
                f.write(base64.b64decode(img_b64_2))
            print("Saved scratch/niji_uta_search_phony.png")

if __name__ == "__main__":
    asyncio.run(test_ui())
