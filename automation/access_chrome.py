from playwright.async_api import async_playwright
import asyncio

class ChromeAccess:
    def __init__(self):
        self.search_url = "https://www.google.com/search?q="

    async def grab_news(self, query):
        async with async_playwright() as p:
            # Headless=True taaki Render par bina screen ke chale
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Searching for news
            await page.goto(f"{self.search_url}{query}+forex+news", wait_until="networkidle")
            
            # Headlines extract karna
            headlines = await page.locator("h3").all_inner_texts()
            
            await browser.close()
            # Sirf top 5 relevant headlines bhejni hain
            return headlines[:5]

    async def get_forex_calendar(self):
        """Specially for Red Folder news"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.forexfactory.com/calendar", wait_until="networkidle")
            
            # Simple logic to find high impact events
            impacts = await page.locator(".calendar__impact").all_inner_texts()
            events = await page.locator(".calendar__event").all_inner_texts()
            
            await browser.close()
            return list(zip(impacts, events))[:10]
