from playwright.async_api import async_playwright

class ChromeAccess:
    def __init__(self):
        self.browser = None

    async def search_and_extract(self, query):
        """Google search karke top results aur images nikalna."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"Searching for: {query}...")
            await page.goto(f"https://www.google.com/search?q={query}")
            
            # Extracting titles
            titles = await page.locator("h3").all_inner_texts()
            
            await browser.close()
            return titles[:5] # Top 5 results

    async def download_image(self, img_url, save_path):
        """Trading charts ya news images save karne ke liye."""
        # Image extraction logic here
        pass
