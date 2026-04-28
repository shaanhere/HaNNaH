import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest

from brain.neuro import NeuroCore
from automation.access_chrome import ChromeAccess
from dotenv import load_dotenv

load_dotenv()

# Health Check for Hugging Face / Render
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HaNNaH is Online and Breathing")

def run_health_server():
    port = int(os.environ.get("PORT", 7860)) # HF uses 7860
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

class HaNNaHBot:
    def __init__(self):
        self.brain = NeuroCore()
        self.chrome = ChromeAccess()
        self.token = os.getenv("TELEGRAM_TOKEN")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        user_text = update.message.text
        print(f"Log: Shaan says -> {user_text}")

        needs_search = await self.brain.should_i_search(user_text)
        
        context_data = ""
        if needs_search:
            temp_msg = await update.message.reply_text("Ruko Shaan, main zara fresh data dekh loon... 🔍")
            try:
                headlines = await self.chrome.grab_news(user_text)
                context_data = " | ".join(headlines) if headlines else "No fresh data found."
                await temp_msg.delete()
            except Exception as e:
                print(f"Log: Search Error -> {e}")
                context_data = "Web search currently unavailable."

        response = await self.brain.process_thought(user_text, context_data=context_data)
        await update.message.reply_text(response)

    def run(self):
        # Background health server
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # Mazboot network settings for Hugging Face
        t_request = HTTPXRequest(
            connect_timeout=60.0, 
            read_timeout=60.0, 
            write_timeout=60.0, 
            pool_timeout=60.0
        )
        
        app = (
            ApplicationBuilder()
            .token(self.token)
            .request(t_request)
            .get_updates_request(t_request) # Startup handshake fix
            .build()
        )

        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        print("HaNNaH is Polling... Boss, signal green hai!")
        # Long polling timeout barha di hai
        app.run_polling(poll_interval=2.0, timeout=60, bootstrap_retries=5)

if __name__ == "__main__":
    bot = HaNNaHBot()
    bot.run()
 
