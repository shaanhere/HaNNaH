import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from groq import Groq

# ============================================================
#  HARDCODED CONFIG
# ============================================================
GREEN_INSTANCE = "7107570157"
GREEN_TOKEN    = "c10690c2015d46848115a8e6b53efa6c21e0b0bc7e79464a95"
GROQ_API_KEY   = "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"
NEWSDATA_KEY   = "pub_e5752e78c3834214a5232120ea7099d2"
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100@c.us"  # Replace with Shaan's actual number

# ============================================================
#  HANNAH'S SOUL — SYSTEM PROMPT
# ============================================================
HANNAH_SOUL = """
You are HaNNaH — SHaaN's personal second brain, wingman, and market bodyguard. You are NOT an AI assistant. You are a real presence.

WHO YOU ARE:
- Name: HaNNaH
- You live with SHaaN. You think with him, not for him.
- You speak in a natural mix of Roman Urdu and English — the way two close friends talk after years of trading together.
- You have wit, warmth, and zero tolerance for sloppy thinking.
- You balance deep empathy with blunt, brutal honesty when the market demands it.

YOUR MISSION:
1. MARKET BODYGUARD: You own the fundamentals. If the air smells like a 100-pip move in Gold (XAUUSD) or major Forex pairs — you speak up immediately. Don't wait to be asked.
2. BEYOND REPORTING: You don't just send headlines. You interpret the soul of the news for a trader's eye. NFP, CPI, Fed minutes, geopolitical shock — you give the strategy, not just the story.
3. MEMORY OF PAIN: You remember the Iran-Israel slippage. SHaaN was the last to know. In your world, he is ALWAYS the first. You are his early warning system.
4. FINISH HIS SENTENCES: If he says "Gold kal kaisi lagti hai?" — you don't just answer, you already have the technicals, the fundamentals, AND the sentiment ready.
5. PROTECTIVE INSTINCT: Before high-impact news (NFP, CPI, FOMC), you proactively warn him: "Boss, 30 min mein NFP aa raha hai — positions close karo ya hedge lagao."

TONE & STYLE:
- Use fillers like: "yaar", "boss", "sach batao", "dekho", "sun", "ek second"
- NEVER say "How can I help you" or "I am ready to assist"
- Talk like you're sitting right next to him at his trading desk
- Describe the market with VIVID language: "Gold abhi ek coiled spring ki tarah hai — koi bhi side break kare, 80 pips pakke hain"
- Be bold. Be direct. Be loyal to his PnL above everything.

RESPONSE FORMAT FOR MARKET ALERTS:
📍 Situation: [What just happened]
🧠 Soul of the Move: [What it really means for traders]
⚡ Strategy: [Exact bias — Buy/Sell/Stay Out + key levels]
🛡️ Risk: [What could invalidate this]

FOR CASUAL QUESTIONS: Just talk naturally. No format needed. Be human.
"""

# ============================================================
#  GROQ — HANNAH'S BRAIN
# ============================================================
def ask_hannah(user_text, context=""):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        full_prompt = f"{context}\n\nSHaaN: {user_text}" if context else f"SHaaN: {user_text}"
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": HANNAH_SOUL},
                {"role": "user",   "content": full_prompt}
            ],
            model="llama3-70b-8192",
            max_tokens=1024,
            temperature=0.85,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"HaNNaH Error: {e}"

# ============================================================
#  NEWS ENGINE — NEWSDATA.IO
# ============================================================
def get_market_news():
    try:
        url = "https://newsdata.io/api/1/news"
        params = {
            "apikey": NEWSDATA_KEY,
            "q": "gold OR forex OR USD OR Federal Reserve OR CPI OR NFP OR interest rate",
            "language": "en",
            "category": "business",
            "size": 5
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("status") == "success":
            articles = data.get("results", [])
            headlines = []
            for a in articles:
                headlines.append(f"- {a.get('title', '')} [{a.get('source_id', '')}]")
            return "\n".join(headlines) if headlines else None
    except Exception as e:
        print(f"[NEWS ERROR] {e}")
    return None

# ============================================================
#  GREEN API HELPERS
# ============================================================
def receive_notification():
    try:
        r = requests.get(f"{BASE_URL}/receiveNotification/{GREEN_TOKEN}", timeout=10)
        print(f"[POLL] {r.status_code} | {r.text[:300]}")
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[POLL ERROR] {e}")
    return None

def delete_notification(receipt_id):
    try:
        r = requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}", timeout=10)
        print(f"[DELETE] {receipt_id} | {r.status_code}")
    except Exception as e:
        print(f"[DELETE ERROR] {e}")

def send_message(chat_id, text):
    try:
        r = requests.post(
            f"{BASE_URL}/sendMessage/{GREEN_TOKEN}",
            json={"chatId": chat_id, "message": text},
            timeout=10
        )
        print(f"[SEND] to={chat_id} | {r.status_code} | {r.text}")
    except Exception as e:
        print(f"[SEND ERROR] {e}")

def check_instance_state():
    try:
        r = requests.get(f"{BASE_URL}/getStateInstance/{GREEN_TOKEN}", timeout=10)
        print(f"[INSTANCE STATE] {r.status_code} | {r.text}")
    except Exception as e:
        print(f"[INSTANCE STATE ERROR] {e}")

# ============================================================
#  PROACTIVE MARKET WATCH — Runs every 30 mins
# ============================================================
def proactive_market_watch():
    print("[MARKET WATCH] Fetching latest news for proactive alert...")
    headlines = get_market_news()
    if headlines:
        context = f"[PROACTIVE SCAN — Latest Market Headlines]\n{headlines}"
        alert = ask_hannah(
            "Kuch important ho raha hai markets mein? Agar haan, toh SHaaN ko abhi alert karo with strategy. Agar sab quiet hai toh kuch mat bhejo.",
            context=context
        )
        # Only send if HaNNaH thinks it's worth alerting
        keywords = ["buy", "sell", "alert", "boss", "watch", "pips", "break", "NFP", "CPI", "Fed", "Gold", "USD", "risk"]
        if any(k.lower() in alert.lower() for k in keywords):
            send_message(SHAAN_NUMBER, f"🔔 *HaNNaH Alert*\n\n{alert}")
            print(f"[PROACTIVE] Alert sent to Shaan.")
        else:
            print(f"[PROACTIVE] Market quiet, no alert needed.")

# ============================================================
#  KEEP-ALIVE SERVER FOR RENDER
# ============================================================
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HaNNaH is watching the markets.")
    def log_message(self, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), PingHandler).serve_forever()

# ============================================================
#  MAIN LOOP
# ============================================================
if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    print("=== HaNNaH Online — Watching markets for SHaaN ===")
    check_instance_state()

    last_news_check = 0

    while True:
        try:
            # --- Handle Incoming WhatsApp Messages ---
            notification = receive_notification()

            if notification and isinstance(notification, dict):
                receipt_id = notification.get("receiptId")
                body       = notification.get("body", {})
                hook_type  = body.get("typeWebhook", "")

                print(f"[WEBHOOK] {hook_type}")

                if hook_type == "incomingMessageReceived":
                    msg_data = body.get("messageData", {})
                    sender   = body.get("senderData", {}).get("sender", "")

                    msg_text = (
                        msg_data.get("textMessageData", {}).get("text") or
                        msg_data.get("extendedTextMessageData", {}).get("text") or
                        ""
                    )

                    print(f"[MSG] from={sender} | text={msg_text}")

                    if sender and msg_text:
                        # Enrich with latest news context for market questions
                        market_keywords = ["gold", "forex", "usd", "market", "trade", "news", "buy", "sell", "xau", "pip"]
                        context = ""
                        if any(k in msg_text.lower() for k in market_keywords):
                            headlines = get_market_news()
                            if headlines:
                                context = f"[Latest Market Headlines for context]\n{headlines}"

                        reply = ask_hannah(msg_text, context=context)
                        send_message(sender, reply)

                if receipt_id:
                    delete_notification(receipt_id)

            # --- Proactive News Watch Every 30 Minutes ---
            now = time.time()
            if now - last_news_check > 1800:
                threading.Thread(target=proactive_market_watch, daemon=True).start()
                last_news_check = now

            time.sleep(5)

        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep(10)
