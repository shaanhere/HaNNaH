from curl_cffi import requests
from bs4 import BeautifulSoup

class ChromeAccess:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def grab_news(self, query):
        try:
            # Google Search URL
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}+latest+news"
            
            # Fetching data without a real browser (Render friendly)
            response = requests.get(url, headers=self.headers, impersonate="chrome110")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extracting headlines (h3 tags)
                headlines = [h.get_text() for h in soup.find_all('h3')[:5]]
                
                if not headlines:
                    return ["Yaar, search results nahi mil sakay."]
                
                return headlines
            else:
                return [f"Google ne mana kar diya. Status: {response.status_code}"]
                
        except Exception as e:
            print(f"Search Error: {e}")
            return [f"Connection error hua: {str(e)}"]
