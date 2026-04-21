import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

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
        user_text = update.message.text
        if not user_text:
            return

        print(f"Log: Shaan says -> {user_text}")

        # Step 1: Brain decides if search is needed
        needs_search = await self.brain.should_i_search(user_text)
        
        context_data = ""
        if needs_search:
            temp_msg = await update.message.reply_text("Ruko Shaan, main zara fresh data dekh loon... 🔍")
            
            try:
                # Step 2: Trigger Chrome Access
                headlines = await self.chrome.grab_news(user_text)
                print(f"Log: Data found -> {headlines}")
                context_data = " | ".join(headlines)
                await temp_msg.delete()
            except Exception as e:
                print(f"Log: Search Error -> {e}")
                context_data = "Web search currently unavailable."

        # Step 3: Brain generates final response with live data
        response = await self.brain.process_thought(user_text, context_data=context_data)
        await update.message.reply_text(response)

    def run(self):
        threading.Thread(target=run_health_server, daemon=True).start()
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        print("HaNNaH is Polling...")
        app.run_polling()

if __name__ == "__main__":
    bot = HaNNaHBot()
    bot.run()
 
