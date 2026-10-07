import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        
        # 開く（ローカルサーバー）
        print("Opening http://localhost:8089/...")
        await page.goto("http://localhost:8089/")
        await page.wait_for_timeout(2000)
        
        # 1. 「かいだ」と入力
        print("Typing 'かいだ' into search input...")
        await page.fill("#searchInput", "かいだ")
        await page.wait_for_timeout(500)
        await page.screenshot(path="C:/niji-uta/scratch/suggest_kaida.png")
        print("Saved suggest_kaida.png")
        
        # 2. Enterキーを押して選択・確定
        print("Pressing Enter to select '甲斐田晴'...")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(500)
        await page.screenshot(path="C:/niji-uta/scratch/suggest_kaida_selected.png")
        print("Saved suggest_kaida_selected.png")
        
        # 3. 「ぴのきお」と入力
        print("Typing 'ぴのきお' into search input...")
        await page.fill("#searchInput", "ぴのきお")
        await page.wait_for_timeout(500)
        await page.screenshot(path="C:/niji-uta/scratch/suggest_pinocchio.png")
        print("Saved suggest_pinocchio.png")

        await b.close()

if __name__ == '__main__':
    asyncio.run(run())
