import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9223")
            context = browser.contexts[0]
            page = await context.new_page()
            
            # 1. Open Vercel new project page
            print("Navigating to Vercel new project page...")
            await page.goto("https://vercel.com/new")
            await page.wait_for_timeout(3000)
            await page.screenshot(path="C:/niji-uta/scratch/vercel_new.png")
            print("Saved vercel_new.png")
            
            # 2. Open Name.com domain page
            page2 = await context.new_page()
            print("Navigating to Name.com domain management...")
            await page2.goto("https://www.name.com/account/domain")
            await page2.wait_for_timeout(3000)
            await page2.screenshot(path="C:/niji-uta/scratch/namecom_domains.png")
            print("Saved namecom_domains.png")
            
        except Exception as e:
            print("Error in deployment script:", e)

if __name__ == '__main__':
    asyncio.run(main())
