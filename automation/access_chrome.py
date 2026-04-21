from curl_cffi import requests

class ChromeAccess:
    def __init__(self):
        # DuckDuckGo simpler API for instant data
        self.url = "https://api.duckduckgo.com/?format=json&q="

    async def grab_news(self, query):
        try:
            response = requests.get(f"{self.url}{query}", impersonate="chrome110")
            data = response.json()
            
            # Instant answer ya related topics uthana
            headlines = [data.get("AbstractText", "")]
            if not headlines[0]:
                headlines = [topic.get("Text", "") for topic in data.get("RelatedTopics", [])[:3]]
            
            return headlines if headlines[0] else ["Market data fetching failed."]
        except:
            return ["No live data."]
