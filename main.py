import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Modules import
from brain.neuro import NeuroCore
from automation.news_analyser import NewsAnalyser
from automation.access_chrome import ChromeAccess

load_dotenv()

class HaNNaH_Bot:
    def __init__(self):
        self.brain = NeuroCore()
        self.chrome = ChromeAccess()
        self.news = NewsAnalyser()
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.boss_id = os.getenv("TELEGRAM_CHAT_ID")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_chat.id)
        user_text = update.message.text

        # Security Check: Sirf SHaaN baat kar sake
        if user_id != self.boss_id:
            await update.message.reply_text("Access Denied. You are not my Boss.")
            return

        # Web Search Logic
        search_context = ""
        if any(word in user_text.lower() for word in ["search", "news", "check"]):
            await update.message.reply_text("Searching the web... hold on Boss.")
            results = await self.chrome.search_and_extract(user_text)
            search_context = " | ".join(results)

        # Brain Processing
        response = await self.brain.process_thought(user_text, context_data=search_context)
        
        # Reply to Telegram
        await update.message.reply_text(response)

    def run(self):
        application = ApplicationBuilder().token(self.token).build()
        
        # Message handler setup
        text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        application.add_handler(text_handler)
        
        print("HaNNaH is active on Telegram. Go talk to her there!")
        application.run_polling()

if __name__ == "__main__":
    bot = HaNNaH_Bot()
    bot.run()
 
