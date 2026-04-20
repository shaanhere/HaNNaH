import asyncio
import os
from dotenv import load_dotenv

# Modules import kar rahe hain
from brain.neuro import NeuroCore
from brain.emotions import Emotions
from automation.news_analyser import NewsAnalyser
from automation.access_chrome import ChromeAccess
from automation.email_access import EmailAccess
from automation.alerts_manager import AlertsManager

# Load environment variables (.env file)
load_dotenv()

class HaNNaH:
    def __init__(self):
        self.name = "HaNNaH"
        self.boss = "SHaaN"
        
        # Initializing all components
        self.brain = NeuroCore()
        self.emotions = Emotions()
        self.news = NewsAnalyser()
        self.chrome = ChromeAccess()
        self.email = EmailAccess()
        self.alerts = AlertsManager()

    async def background_monitoring(self):
        """Background mein market scan aur alerts handle karna"""
        print(f"[{self.name}]: Monitoring started. Market pe nazar hai, Boss.")
        while True:
            try:
                # High Impact News Check
                news_update = await self.news.get_latest_sentiment()
                if "High Impact" in news_update or "Red Folder" in news_update:
                    await self.alerts.send_alert(f"Market Alert: {news_update}")
                
                # Har 10 minute baad check karega
                await asyncio.sleep(600) 
            except Exception as e:
                print(f"Monitoring Error: {e}")
                await asyncio.sleep(60)

    async def chat_interface(self):
        """Live Chat Interface with Groq + Chrome Integration"""
        print(f"\n--- {self.name} is LIVE (Powered by Llama-3.3-70b) ---")
        
        while True:
            user_input = input(f"\n{self.boss}: ").strip()
            if not user_input:
                continue

            # Check if user wants a web search/news
            context = ""
            search_keywords = ["search", "news", "check", "headlines", "latest", "btao"]
            
            if any(word in user_input.lower() for word in search_keywords):
                print(f"[{self.name}]: Searching the web for you...")
                search_results = await self.chrome.search_and_extract(user_input)
                context = " | ".join(search_results) if search_results else "No live data found."

            # Brain processes the input with context and emotions
            self.emotions.update_mood("normal") # Dynamic mood logic yahan aayegi
            raw_response = await self.brain.process_thought(user_input, context_data=context)
            
            # Formatting response with HaNNaH's style
            final_response = self.emotions.format_response(raw_response)
            
            print(f"\n{self.name}: {final_response}")

    async def start(self):
        # Dono tasks ko parallel chalana
        await asyncio.gather(
            self.background_monitoring(),
            self.chat_interface()
        )

if __name__ == "__main__":
    bot = HaNNaH()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print(f"\n[{bot.name}]: Allah Hafiz Boss, take care!")
    except Exception as e:
        print(f"System Crash: {e}")
