import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest  # Timeout handle karne ke liye

from brain.neuro import NeuroCore
from automation.access_chrome import ChromeAccess
from dotenv import load_dotenv

load_dotenv()

# Health Check for Render
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HaNNaH is Online")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
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
        # Server start ho raha hai
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # FIX: Connection timeout settings barha di hain
        t_request = HTTPXRequest(connect_timeout=30, read_timeout=30)
        
        app = (
            ApplicationBuilder()
            .token(self.token)
            .request(t_request)  # Request config yahan add ki hai
            .get_updates_request(t_request)
            .build()
        )

        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        print("HaNNaH is Polling with extended timeouts...")
        app.run_polling(poll_interval=1.0, timeout=30)

if __name__ == "__main__":
    bot = HaNNaHBot()
    bot.run()
 
