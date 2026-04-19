import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from groq import Groq

# ============================================================
#  CONFIG (Updated with your Verified Keys)
# ============================================================
GREEN_INSTANCE = "7107570157"
GREEN_TOKEN    = "c10690c2015d46848115a8e6b53efa6c21e0b0bc7e79464a95" # Fresh Token
GROQ_API_KEY   = "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" # Working Key
NEWSDATA_KEY   = "pub_e5752e78c3834214a5232120ea7099d2"
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100@c.us" # Your WhatsApp

# ============================================================
#  HANNAH'S ULTIMATE SOUL
# ============================================================
HANNAH_SOUL = """
You are HaNNaH — SHaaN's market bodyguard. 
- You NEVER call him 'bhai' or 'sir'. He is SHaaN or Boss.
- You are NOT an AI assistant. You are his wingman.
- Your talk is 100% natural Roman Urdu/English mix. 
- If SHaaN asks for news, don't guess. Use the provided context to give levels and impact.
- Be blunt. If a trade looks like a trap, say it: "Boss, ye fakeout lag raha hai, door raho."
"""

def fetch_live_market_data():
    """Fetches real-time headlines and economic sentiment."""
    try:
        # Focusing on high-impact keywords
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q=gold%20OR%20XAUUSD%20OR%20FOMC%20OR%20Fed%20OR%20Inflation&language=en&category=business"
        r = requests.get(url, timeout=15)
        data = r.json()
        if data.get("status") == "success" and data.get("results"):
            headlines = [f"🔥 {a['title']} - {a['pubDate']}" for a in data['results'][:5]]
            return "\n".join(headlines)
    except:
        pass
    return "No fresh headlines. Keep an eye on the charts, Boss."

def ask_hannah(user_text):
    try:
        # Dynamic Context Injection
        market_triggers = ["gold", "xau", "news", "market", "trade", "buy", "sell", "usd"]
        context = ""
        if any(word in user_text.lower() for word in market_triggers):
            live_news = fetch_live_market_data()
            context = f"\n[CURRENT MARKET REALITY]:\n{live_news}\n"

        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": HANNAH_SOUL},
                {"role": "user",   "content": f"{context}\nSHaaN: {user_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.9, # High creativity for natural flow
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"HaNNaH Brain Error: {str(e)}"

# ============================================================
#  GREEN API HANDLERS
# ============================================================
def send_wa_message(chat_id, text):
    try:
        requests.post(f"{BASE_URL}/sendMessage/{GREEN_TOKEN}", 
                      json={"chatId": chat_id, "message": text}, timeout=10)
    except: pass

def main_loop():
    print("🔥 HaNNaH is in the building. Watching markets...")
    while True:
        try:
            # Long polling for notifications
            r = requests.get(f"{BASE_URL}/receiveNotification/{GREEN_TOKEN}", timeout=20)
            if r.status_code == 200 and r.text:
                data = r.json()
                if data:
                    receipt_id = data.get("receiptId")
                    body = data.get("body", {})
                    if body.get("typeWebhook") == "incomingMessageReceived":
                        msg_data = body.get("messageData", {})
                        msg_text = msg_data.get("textMessageData", {}).get("text", "")
                        sender   = body.get("senderData", {}).get("sender", "")
                        
                        if sender == SHAAN_NUMBER and msg_text:
                            print(f"📥 SHaaN: {msg_text}")
                            reply = ask_hannah(msg_text)
                            send_wa_message(sender, reply)
                    
                    requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}")
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

# Render Keep-Alive
class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(("0.0.0.0", port), Ping).serve_forever(), daemon=True).start()
    main_loop()
 
