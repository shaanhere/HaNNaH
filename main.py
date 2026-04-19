import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from groq import Groq
from datetime import datetime

# ============================================================
#  FINAL VERIFIED CONFIG
# ============================================================
GREEN_INSTANCE = "7107570157"
GREEN_TOKEN    = "c10690c2015d46848115a8e6b53efa6c21e0b0bc7e79464a95"
GROQ_API_KEY   = "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"
FMP_API_KEY    = "ogECGJ7AGs4W78mtryA6EGPTiiwH6bok"
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100@c.us"

HANNAH_SOUL = """
You are HaNNaH — SHaaN's market bodyguard. No 'bhai', no 'sir', no robotic AI talk.
Talk in Roman Urdu/English mix. Be blunt and proactive about high impact news.
"""

def get_economic_calendar():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=5) # Tight timeout
        data = r.json()
        if isinstance(data, list):
            events = [f"⚠️ {e['event']} ({e['impact']})" for e in data if e.get('impact') in ['High', 'Medium']][:5]
            return "\n".join(events) if events else "No major events right now."
    except: return "Calendar busy, watch the charts."
    return "No major events."

def ask_hannah(user_text):
    try:
        context = ""
        if any(k in user_text.lower() for k in ["news", "gold", "market", "calendar"]):
            context = f"\n[LIVE CALENDAR]:\n{get_economic_calendar()}\n"

        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            messages=[{"role": "system", "content": HANNAH_SOUL}, {"role": "user", "content": f"{context}\nSHaaN: {user_text}"}],
            model="llama-3.3-70b-versatile",
            temperature=0.8
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"!!! GROQ ERROR: {e}")
        return "Brain fog ho gaya, thora wait karo boss."

def send_wa(chat_id, text):
    try:
        url = f"{BASE_URL}/sendMessage/{GREEN_TOKEN}"
        requests.post(url, json={"chatId": chat_id, "message": text}, timeout=10)
        print(f"📤 Sent to {chat_id}")
    except Exception as e: print(f"!!! SEND ERROR: {e}")

def main_loop():
    print("🔥 HaNNaH is starting the engine...")
    while True:
        try:
            # Poll for new messages
            r = requests.get(f"{BASE_URL}/receiveNotification/{GREEN_TOKEN}", timeout=20)
            if r.status_code == 200 and r.text:
                data = r.json()
                if data and "receiptId" in data:
                    receipt_id = data["receiptId"]
                    body = data.get("body", {})
                    
                    if body.get("typeWebhook") == "incomingMessageReceived":
                        msg_text = body.get("messageData", {}).get("textMessageData", {}).get("text", "")
                        sender = body.get("senderData", {}).get("sender", "")
                        
                        if sender == SHAAN_NUMBER and msg_text:
                            print(f"📥 Received: {msg_text}")
                            reply = ask_hannah(msg_text)
                            send_wa(sender, reply)
                    
                    # MANDATORY: Delete notification to move to the next one
                    requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}", timeout=10)
                    print(f"✅ Notification {receipt_id} cleared.")
            
            time.sleep(1)
        except Exception as e:
            print(f"!!! LOOP ERROR: {e}")
            time.sleep(5)

class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ALIVE")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(("0.0.0.0", port), Ping).serve_forever(), daemon=True).start()
    main_loop()
 
