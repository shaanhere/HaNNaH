import asyncio
import os
from dotenv import load_dotenv
from automation.news_analyser import NewsAnalyser
from brain.neuro import NeuroCore

load_dotenv() # Load your API keys here

class HaNNaH:
    def __init__(self):
        self.name = "HaNNaH"
        self.boss = "SHaaN"
        self.brain = NeuroCore()
        self.news = NewsAnalyser()

    async def background_monitoring(self):
        """Har 5 minute baad market aur news scan karega"""
        while True:
            print(f"[{self.name}]: Monitoring charts for liquidity sweeps...")
            market_update = await self.news.get_latest_sentiment()
            if "High Impact" in market_update:
                print(f"Alert for {self.boss}: Market volatility detected!")
            
            await asyncio.sleep(300) # 5 min wait

    async def chat_interface(self):
        """Tumhare aur HaNNaH ke beech ki conversation"""
        print(f"--- {self.name} is Online ---")
        while True:
            user_input = input(f"{self.boss}: ")
            
            # Brain processing logic
            response = await self.brain.process_thought(user_input)
            
            print(f"{self.name}: {response}")

    async def run(self):
        # Dono tasks ko ek saath chalana hai
        await asyncio.gather(
            self.background_monitoring(),
            self.chat_interface()
        )

if __name__ == "__main__":
    bot = HaNNaH()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nHaNNaH is going to sleep. Take care, Boss.")
 
