import asyncio
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Sites to skip (paywalls / login walls — waste of time)
BLOCKED_DOMAINS = [
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "wsj.com", "ft.com", "bloomberg.com/subscription",
]

class ChromeAccess:
    def __init__(self):
        self._browser = None
        self._playwright = None

    # ─────────────────────────────────────────────
    # PUBLIC METHOD — called from main.py
    # ─────────────────────────────────────────────
    async def grab_news(self, query: str) -> list[str]:
        """
        1. Google pe query search karo
        2. Top 3 real URLs open karo
        3. Har page ka clean text extract karo
        4. Saara content return karo HaNNaH ke liye
        """
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                    ]
                )
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                    locale="en-US",
                )

                # Step 1: Google search se top URLs nikalo
                urls = await self._google_search(context, query)

                if not urls:
                    await browser.close()
                    return ["No search results found for this query."]

                # Step 2: Har URL kholo aur content nikalo
                results = []
                for url in urls[:3]:  # Top 3 sites enough hain
                    content = await self._read_page(context, url)
                    if content:
                        results.append(f"[Source: {url}]\n{content}")

                await browser.close()

                return results if results else ["Could not extract content from search results."]

        except Exception as e:
            return [f"Browser error: {str(e)}"]

    # ─────────────────────────────────────────────
    # STEP 1: Google search → real URLs
    # ─────────────────────────────────────────────
    async def _google_search(self, context, query: str) -> list[str]:
        page = await context.new_page()
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en&num=10"
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)

            # Google result links uthao — actual website URLs
            links = await page.evaluate("""
                () => {
                    const anchors = document.querySelectorAll('a[href]');
                    const urls = [];
                    for (const a of anchors) {
                        const href = a.href;
                        if (
                            href.startsWith('http') &&
                            !href.includes('google.com') &&
                            !href.includes('accounts.') &&
                            !href.includes('support.') &&
                            !href.includes('webcache')
                        ) {
                            urls.push(href);
                        }
                    }
                    return [...new Set(urls)].slice(0, 6);
                }
            """)

            # Blocked domains filter karo
            filtered = [
                url for url in links
                if not any(blocked in url for blocked in BLOCKED_DOMAINS)
            ]

            await page.close()
            return filtered

        except Exception as e:
            await page.close()
            return []

    # ─────────────────────────────────────────────
    # STEP 2: URL kholo → clean text nikalo
    # ─────────────────────────────────────────────
    async def _read_page(self, context, url: str) -> str:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)

            # JS render hone do thoda
            await page.wait_for_timeout(1500)

            # Page ka visible text nikalo — ads, nav, footer hata ke
            raw_text = await page.evaluate("""
                () => {
                    // Remove clutter
                    const remove = ['script','style','nav','footer',
                                    'header','aside','iframe','noscript',
                                    'form','button','[class*="ad"]',
                                    '[class*="cookie"]','[class*="popup"]'];
                    remove.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => el.remove());
                    });

                    // Main content prefer karo
                    const main = document.querySelector(
                        'article, main, [role="main"], .post-content, .article-body, .entry-content'
                    );
                    const target = main || document.body;
                    return target.innerText || '';
                }
            """)

            await page.close()
            return self._clean_text(raw_text)

        except PlaywrightTimeout:
            await page.close()
            return ""
        except Exception:
            await page.close()
            return ""

    # ─────────────────────────────────────────────
    # HELPER: Text saaf karo
    # ─────────────────────────────────────────────
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Extra whitespace hata do
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)
        text = text.strip()
        # Sirf pehle 1500 characters — LLM ke liye enough
        return text[:1500]
