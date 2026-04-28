import os
import asyncio
import threading
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import uvicorn
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from neuro import NeuroCore
from access_chrome import ChromeAccess
from dotenv import load_dotenv

load_dotenv()

# ── FastAPI app (HF Spaces needs a web server on port 7860) ──
api = FastAPI()

@api.get("/", response_class=PlainTextResponse)
async def health():
    return "HaNNaH is Online ✅"

# ── Telegram Bot ──
class HaNNaHBot:
    def __init__(self):
        self.brain = NeuroCore()
        self.chrome = ChromeAccess()
        self.token = os.getenv("TELEGRAM_TOKEN")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        if not user_text:
            return

        print(f"Log: Shaan says -> {user_text}")

        needs_search = await self.brain.should_i_search(user_text)

        context_data = ""
        if needs_search:
            temp_msg = await update.message.reply_text("Ruko Shaan, main zara fresh data dekh loon... 🔍")
            try:
                headlines = await self.chrome.grab_news(user_text)
                print(f"Log: Data found -> {headlines}")
                context_data = " | ".join(headlines)
                await temp_msg.delete()
            except Exception as e:
                print(f"Log: Search Error -> {e}")
                context_data = "Web search currently unavailable."

        response = await self.brain.process_thought(user_text, context_data=context_data)
        await update.message.reply_text(response)

    def start_polling(self):
        """Run bot in its own thread with its own event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        print("HaNNaH is Polling...")
        app.run_polling()


def run_bot():
    bot = HaNNaHBot()
    bot.start_polling()


# ── Start bot in background thread, FastAPI in main thread ──
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=7860)
 
