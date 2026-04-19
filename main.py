import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from groq import Groq
from datetime import datetime

# ============================================================
#  CONFIG
# ============================================================
GREEN_INSTANCE = "7107570157"
GREEN_TOKEN    = "c10690c2015d46848115a8e6b53efa6c21e0b0bc7e79464a95"
GROQ_API_KEY   = "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"
FMP_API_KEY    = "ogECGJ7AGs4W78mtryA6EGPTiiwH6bok" # Your New Key
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100@c.us"

# ============================================================
#  HANNAH'S UPGRADED PERSONALITY
# ============================================================
HANNAH_SOUL = """
You are HaNNaH — SHaaN's market wingman. 
- You NEVER call him 'bhai' or 'sir'. He is SHaaN or Boss.
- Talk in Roman Urdu/English mix. 
- Use the Economic Calendar data to warn him about 'High' impact events.
- If a news event has a 'High' impact, be aggressive: "Boss, sambhal jao, volatile move aanay wala hai."
"""

def get_economic_calendar():
    """Fetches real-time economic events (NFP, CPI, FOMC, etc.)"""
    try:
        # Fetching for today and tomorrow
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=15)
        data = r.json()
        
        if isinstance(data, list) and len(data) > 0:
            events = []
            for event in data[:8]: # Top 8 events
                impact = event.get('impact', 'Low')
                # We care mostly about High and Medium impact for trading
                if impact in ['High', 'Medium']:
                    events.append(f"⚠️ {event['event']} ({event['country']}) | Impact: {impact} | Actual: {event.get('actual', 'Pending')}")
            
            return "\n".join(events) if events else "No high impact events scheduled for today."
    except Exception as e:
        print(f"FMP Error: {e}")
    return "Calendar fetch failed. Stick to the charts for now."

def ask_hannah(user_text):
    try:
        # Check if user is asking about news/market
        market_triggers = ["news", "calendar", "event", "gold", "market", "move", "impact"]
        calendar_context = ""
        
        if any(word in user_text.lower() for word in market_triggers):
            calendar_data = get_economic_calendar()
            calendar_context = f"\n[ECONOMIC CALENDAR DATA]:\n{calendar_data}\n"

        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": HANNAH_SOUL},
                {"role": "user",   "content": f"{calendar_context}\nSHaaN: {user_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"HaNNaH Brain Error: {str(e)}"

# ============================================================
#  MESSAGE HANDLING
# ============================================================
def send_wa(chat_id, text):
    try:
        requests.post(f"{BASE_URL}/sendMessage/{GREEN_TOKEN}", 
                      json={"chatId": chat_id, "message": text}, timeout=10)
    except: pass

def main_loop():
    print("🔥 HaNNaH is Live with Economic Calendar...")
    while True:
        try:
            r = requests.get(f"{BASE_URL}/receiveNotification/{GREEN_TOKEN}", timeout=20)
            if r.status_code == 200 and r.text:
                data = r.json()
                if data:
                    receipt_id = data.get("receiptId")
                    body = data.get("body", {})
                    if body.get("typeWebhook") == "incomingMessageReceived":
                        msg_text = body.get("messageData", {}).get("textMessageData", {}).get("text", "")
                        sender   = body.get("senderData", {}).get("sender", "")
                        
                        if sender == SHAAN_NUMBER and msg_text:
                            reply = ask_hannah(msg_text)
                            send_wa(sender, reply)
                    
                    requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}")
            time.sleep(1)
        except: time.sleep(5)

class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"CALENDAR_ACTIVE")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(("0.0.0.0", port), Ping).serve_forever(), daemon=True).start()
    main_loop()
 
