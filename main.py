import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from brain.neuro import NeuroCore
from dotenv import load_dotenv

load_dotenv()

# --- Health Check for Render ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HaNNaH is Active")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

# --- Bot Logic ---
brain = NeuroCore()

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"Received: {user_text}") # Ye Render logs mein dikhayega
    
    # Direct response for testing
    try:
        response = await brain.process_thought(user_text)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Dimaag thora garam hai, error: {e}")

if __name__ == "__main__":
    # Start Web Server
    threading.Thread(target=run_server, daemon=True).start()
    
    # Start Telegram Bot
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Error: No Token found in Environment Variables!")
    else:
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
        print("HaNNaH is Polling...")
        app.run_polling()
