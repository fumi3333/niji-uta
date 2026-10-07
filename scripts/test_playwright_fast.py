import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Connecting to Chrome port 9223 via Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9223")
        ctx = browser.contexts[0]
        
        # Navigate active page or new page to vercel
        page = await ctx.new_page()
        print("Navigating to Vercel dashboard...")
        await page.goto("https://vercel.com/dashboard", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        url1 = page.url
        print("Vercel URL:", url1)
        await page.screenshot(path="C:/niji-uta/scratch/vercel_test.png")
        
        page2 = await ctx.new_page()
        print("Navigating to Name.com...")
        await page2.goto("https://www.name.com/account/domain", wait_until="domcontentloaded")
        await page2.wait_for_timeout(3000)
        url2 = page2.url
        print("Namecom URL:", url2)
        await page2.screenshot(path="C:/niji-uta/scratch/namecom_test.png")

if __name__ == '__main__':
    asyncio.run(run())
