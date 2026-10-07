import json
import websockets
import asyncio
import base64

async def test_ui_update():
    import urllib.request
    res = urllib.request.urlopen("http://localhost:9223/json")
    tabs = json.loads(res.read().decode())
    target_tab = next((t for t in tabs if "localhost:8089" in t["url"]), None)
    if not target_tab:
        print("Tab not found")
        return
        
    ws_url = target_tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        # リロード
        reload_cmd = {"id": 1, "method": "Page.reload"}
        await ws.send(json.dumps(reload_cmd))
        await ws.recv()
        await asyncio.sleep(2)
        
        # シャルルと入力
        eval_cmd = {
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                (() => {
                    const input = document.getElementById('searchInput');
                    input.value = 'シャルル';
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
        
        # スクリーンショット撮影
        ss_cmd = {"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}
        await ws.send(json.dumps(ss_cmd))
        ss_res = await ws.recv()
        ss_data = json.loads(ss_res)
        img_b64 = ss_data.get("result", {}).get("data", "")
        with open(r"C:\Users\hrfmt\.gemini\antigravity\brain\39f64cff-3b02-47c9-9d6a-adc41a23b3fc\scratch\charles_granular_search.png", "wb") as f:
            f.write(base64.b64decode(img_b64))
        print("Saved scratch/charles_granular_search.png")

if __name__ == "__main__":
    asyncio.run(test_ui_update())
