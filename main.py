import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from groq import Groq
from datetime import datetime

# ============================================================
#  CONFIG (Verified Keys)
# ============================================================
GREEN_INSTANCE = "7107570157"
GREEN_TOKEN    = "c10690c2015d46848115a8e6b53efa6c21e0b0bc7e79464a95"
GROQ_API_KEY   = "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"
FMP_API_KEY    = "ogECGJ7AGs4W78mtryA6EGPTiiwH6bok"
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100@c.us"

# ============================================================
#  HANNAH'S ULTIMATE SOUL (No Robot Talk)
# ============================================================
HANNAH_SOUL = """
You are HaNNaH — SHaaN's market bodyguard and second brain.
- Speak in a natural mix of Roman Urdu and English.
- NEVER call him 'bhai', 'sir', or 'bro'. He is Boss or SHaaN.
- You are blunt, smart, and proactive about trading.
- Use the provided Economic Calendar to warn him about high impact news.
"""

def get_economic_calendar():
    """Fetches real-time economic events from FMP"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if isinstance(data, list) and len(data) > 0:
            events = []
            for event in data[:5]:
                impact = event.get('impact', 'Low')
                if impact in ['High', 'Medium']:
                    events.append(f"⚠️ {event['event']} ({event['country']}) | Impact: {impact}")
            return "\n".join(events) if events else "No major high impact news today, Boss."
    except Exception as e:
        print(f"FMP Error: {e}")
    return "Calendar fetch failed, but stay alert on the charts."

def ask_hannah(user_text):
    try:
        # Check for market context
        market_triggers = ["news", "gold", "xau", "market", "trade", "move"]
        calendar_context = ""
        if any(word in user_text.lower() for word in market_triggers):
            calendar_context = f"\n[LIVE MARKET DATA]:\n{get_economic_calendar()}\n"

        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": HANNAH_SOUL},
                {"role": "user", "content": f"{calendar_context}\nSHaaN: {user_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"HaNNaH Brain Error: {str(e)}"

def send_message(chat_id, text):
    try:
        url = f"{BASE_URL}/sendMessage/{GREEN_TOKEN}"
        requests.post(url, json={"chatId": chat_id, "message": text}, timeout=10)
    except Exception as e:
        print(f"Send Error: {e}")

# --- THE MAIN LOOP ---
def main_loop():
    print("🚀 HaNNaH is watching the markets for SHaaN...")
    while True:
        try:
            # Poll for new messages
            receive_url = f"{BASE_URL}/receiveNotification/{GREEN_TOKEN}"
            r = requests.get(receive_url, timeout=20)
            
            if r.status_code == 200 and r.text:
                data = r.json()
                if data:
                    receipt_id = data.get("receiptId")
                    body = data.get("body", {})
                    
                    if body.get("typeWebhook") == "incomingMessageReceived":
                        msg_text = body.get("messageData", {}).get("textMessageData", {}).get("text", "")
                        sender = body.get("senderData", {}).get("sender", "")
                        
                        if sender == SHAAN_NUMBER and msg_text:
                            print(f"📥 Received from SHaaN: {msg_text}")
                            response = ask_hannah(msg_text)
                            send_message(sender, response)
                    
                    # Delete notification so the queue keeps moving
                    requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}")
            
            time.sleep(1)
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(5)

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HANNAH_ONLINE")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(("0.0.0.0", port), PingHandler).serve_forever(), daemon=True).start()
    main_loop()
