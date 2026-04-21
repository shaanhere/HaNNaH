import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Importing your modules
from brain.neuro import NeuroCore
from automation.access_chrome import ChromeAccess
from dotenv import load_dotenv

load_dotenv()

# --- Health Check for Render (Fake Port Binding) ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HaNNaH is Active and Online")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

# --- Core Bot Logic ---
class HaNNaHBot:
    def __init__(self):
        self.brain = NeuroCore()
        self.chrome = ChromeAccess()
        self.token = os.getenv("TELEGRAM_TOKEN")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        if not user_text:
            return

        print(f"Shaan says: {user_text}")

        # Check if we need to search the web
        search_keywords = ["news", "search", "check", "headlines", "what is", "situation", "latest"]
        context_data = ""

        if any(word in user_text.lower() for word in search_keywords):
            # Tell the user we are looking it up
            temp_msg = await update.message.reply_text("Ruko Shaan, main zara check kar loon kya scene hai...")
            
            try:
                # 1. Grab headlines from Chrome
                headlines = await self.chrome.grab_news(user_text)
                context_data = " | ".join(headlines)
                
                # 2. Delete the temporary message
                await temp_msg.delete()
            except Exception as e:
                print(f"Chrome Error: {e}")
                context_data = "Live data fetch nahi ho saka, purani knowledge use karo."

        # 3. Process with Neuro (Groq Llama-3.3-70b)
        response = await self.brain.process_thought(user_text, context_data=context_data)
        
        # 4. Final Reply to Telegram
        await update.message.reply_text(response)

    def run(self):
        # Start health check in background
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # Build Telegram App
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        print("HaNNaH is Polling for messages...")
        app.run_polling()

if __name__ == "__main__":
    bot = HaNNaHBot()
    bot.run()
 
