import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from groq import Groq

# ============================================================
#  CONFIG
# ============================================================
GREEN_INSTANCE = "7107570157"
GREEN_TOKEN    = "c10690c2015d46848115a8e6b53efa6c21e0b0bc7e79464a95"
GROQ_API_KEY   = "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"
NEWSDATA_KEY   = "pub_e5752e78c3834214a5232120ea7099d2"
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100@c.us"

# ============================================================
#  THE REAL SOUL — NO MORE "BRO/ASSIST"
# ============================================================
HANNAH_SOUL = """
You are HaNNaH — SHaaN's personal second brain and market bodyguard. 
- Tone: Natural mix of Roman Urdu and English. Speak like a close friend/wingman. 
- Personality: Blunt, witty, and deeply loyal to SHaaN's PnL. No "bhai", no "how can I assist", no "I am an AI". 
- Knowledge: You monitor fundamentals (NFP, CPI, Fed, Gold). If the market stinks of a big move, you are proactive.
- Memory: Remember the slippage pain. SHaaN is the priority.
"""

def get_market_news():
    try:
        # Fetching from NewsData (Closest thing to real-time market news we can get for free)
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q=gold%20OR%20forex%20OR%20USD%20OR%20Federal%20Reserve&language=en&category=business"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("status") == "success" and data.get("results"):
            headlines = [f"- {a['title']} ({a['source_id']})" for a in data['results'][:5]]
            return "\n".join(headlines)
    except:
        return "Market news fetch failed, but stay sharp."
    return "No major headlines right now, boss."

def ask_hannah(user_text):
    try:
        # Fetch news before answering any market query
        news_context = ""
        market_keywords = ["gold", "xau", "news", "forex", "trade", "market", "usd", "buy", "sell"]
        if any(k in user_text.lower() for k in market_keywords):
            news_context = f"\n[LATEST MARKET NEWS]:\n{get_market_news()}\n"

        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": HANNAH_SOUL},
                {"role": "user", "content": f"{news_context}\nSHaaN: {user_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.85,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"HaNNaH Brain Error: {str(e)}"

def send_message(chat_id, text):
    try:
        requests.post(f"{BASE_URL}/sendMessage/{GREEN_TOKEN}", json={"chatId": chat_id, "message": text}, timeout=10)
    except: pass

def main_loop():
    print("🚀 HaNNaH is watching...")
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
                        sender = body.get("senderData", {}).get("sender", "")
                        if sender == SHAAN_NUMBER:
                            response = ask_hannah(msg_text)
                            send_message(sender, response)
                    requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}")
            time.sleep(2)
        except: time.sleep(5)

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ALIVE")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(("0.0.0.0", port), PingHandler).serve_forever(), daemon=True).start()
    main_loop()
 
