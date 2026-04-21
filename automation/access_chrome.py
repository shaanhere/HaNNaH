from playwright.async_api import async_playwright
import os

class ChromeAccess:
    def __init__(self):
        self.search_url = "https://www.google.com/search?q="

    async def grab_news(self, query):
        try:
            async with async_playwright() as p:
                # Render compatibility settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                page = await browser.new_page()
                
                # Search query with "latest news" tag
                search_query = f"{query} latest news price"
                await page.goto(f"{self.search_url}{search_query}", wait_until="domcontentloaded", timeout=30000)
                
                # Top headlines and snippets extract karna
                headlines = await page.locator("h3").all_inner_texts()
                snippets = await page.locator("div.VwiC3b").all_inner_texts() # Google snippet class
                
                await browser.close()
                
                # Combine headlines and snippets for more context
                combined_data = headlines[:5] + snippets[:3]
                return combined_data
        except Exception as e:
            print(f"Browser Error: {e}")
            return ["No live data found right now."]
