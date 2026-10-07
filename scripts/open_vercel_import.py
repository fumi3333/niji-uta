import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    print("Connecting to Chrome on port 9223...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9223")
            context = browser.contexts[0]
            print("Connected! Pages count:", len(context.pages))
            
            # Check open tabs
            for page in context.pages:
                url = page.url
                title = await page.title()
                if "vercel" in url or "name.com" in url or "github" in url:
                    print(f"Tab: {title[:30]} -> {url}")
            
            # Open Vercel Import Page
            print("Opening Vercel import page...")
            page = await context.new_page()
            await page.goto("https://vercel.com/new/import?s=https%3A%2F%2Fgithub.com%2Ffumi3333%2Fniji-uta")
            await page.wait_for_timeout(4000)
            await page.screenshot(path="C:/niji-uta/scratch/vercel_import_page.png")
            print("Saved vercel_import_page.png")
            
        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    asyncio.run(main())
