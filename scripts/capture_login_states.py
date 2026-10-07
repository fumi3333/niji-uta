import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9223")
        ctx = b.contexts[0]
        
        # Name.com tab
        page_name = None
        for pg in ctx.pages:
            if "name.com" in pg.url:
                page_name = pg
                break
                
        if page_name:
            print("Found Name.com page! URL:", page_name.url)
            await page_name.bring_to_front()
            await page_name.screenshot(path="C:/niji-uta/scratch/namecom_real.png")
            print("Saved namecom_real.png")
            
        # Vercel signup/login tab
        page_vercel = None
        for pg in ctx.pages:
            if "vercel.com" in pg.url:
                page_vercel = pg
                break
                
        if page_vercel:
            print("Found Vercel page! URL:", page_vercel.url)
            await page_vercel.bring_to_front()
            await page_vercel.screenshot(path="C:/niji-uta/scratch/vercel_real.png")
            print("Saved vercel_real.png")

if __name__ == '__main__':
    asyncio.run(main())
