import json
import websockets
import asyncio
import base64

async def test_fixes():
    import urllib.request
    res = urllib.request.urlopen("http://localhost:9223/json")
    tabs = json.loads(res.read().decode())
    target_tab = next((t for t in tabs if "localhost:8089" in t["url"]), None)
    if not target_tab:
        return
        
    ws_url = target_tab["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        # リロード
        await ws.send(json.dumps({"id": 1, "method": "Page.reload"}))
        await ws.recv()
        await asyncio.sleep(2)
        
        # 1. 甲斐田晴で検索
        await ws.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                (() => {
                    const input = document.getElementById('searchInput');
                    input.value = '甲斐田晴';
                    input.dispatchEvent(new Event('input'));
                    return document.getElementById('countIndicator').innerText;
                })()
                """
            }
        }))
        res = await ws.recv()
        print("Kaida search count:", json.loads(res).get("result", {}).get("result", {}).get("value"))
        await asyncio.sleep(1)
        
        # 甲斐田晴のスクショ
        ss_cmd = {"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}
        await ws.send(json.dumps(ss_cmd))
        ss_res = await ws.recv()
        img_b64 = json.loads(ss_res).get("result", {}).get("data", "")
        with open(r"C:\Users\hrfmt\.gemini\antigravity\brain\39f64cff-3b02-47c9-9d6a-adc41a23b3fc\scratch\kaida_search_verified.png", "wb") as f:
            f.write(base64.b64decode(img_b64))
        print("Saved kaida_search_verified.png")
        
        # 2. ドーラで検索して日付を確認
        await ws.send(json.dumps({
            "id": 4,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                (() => {
                    const input = document.getElementById('searchInput');
                    input.value = 'ドーラ';
                    input.dispatchEvent(new Event('input'));
                    return document.getElementById('countIndicator').innerText;
                })()
                """
            }
        }))
        res = await ws.recv()
        print("Dora search count:", json.loads(res).get("result", {}).get("result", {}).get("value"))
        await asyncio.sleep(1)
        
        await ws.send(json.dumps(ss_cmd))
        ss_res2 = await ws.recv()
        img_b64_2 = json.loads(ss_res2).get("result", {}).get("data", "")
        with open(r"C:\Users\hrfmt\.gemini\antigravity\brain\39f64cff-3b02-47c9-9d6a-adc41a23b3fc\scratch\dora_search_verified.png", "wb") as f:
            f.write(base64.b64decode(img_b64_2))
        print("Saved dora_search_verified.png")

if __name__ == "__main__":
    asyncio.run(test_fixes())
