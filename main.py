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
GROQ_API_KEY   = "YOUR_GROQ_API_KEY"
FMP_API_KEY    = "YOUR_FMP_API_KEY"
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100"

# ============================================================
#  AI SOUL
# ============================================================
HANNAH_SOUL = """
You are HaNNaH — SHaaN's market bodyguard and second brain.
- Speak in Roman Urdu + English
- Be sharp, blunt, and proactive
"""

# ============================================================
#  ECONOMIC CALENDAR
# ============================================================
def get_economic_calendar():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()

        events = []
        if isinstance(data, list):
            for event in data[:5]:
                impact = event.get('impact', 'Low')
                if impact in ['High', 'Medium']:
                    events.append(f"⚠️ {event['event']} ({event['country']}) | {impact}")

        return "\n".join(events) if events else "No major news today."

    except Exception as e:
        print("Calendar Error:", e)
        return "Calendar unavailable."

# ============================================================
#  AI RESPONSE
# ============================================================
def ask_hannah(user_text):
    try:
        calendar = get_economic_calendar()

        client = Groq(api_key=GROQ_API_KEY)

        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": HANNAH_SOUL},
                {"role": "user", "content": f"[Market]\n{calendar}\n\nSHaaN: {user_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )

        return resp.choices[0].message.content

    except Exception as e:
        print("AI Error:", e)
        return "Hannah brain glitch..."

# ============================================================
#  SEND MESSAGE
# ============================================================
def send_message(chat_id, text):
    try:
        url = f"{BASE_URL}/sendMessage/{GREEN_TOKEN}"
        requests.post(url, json={
            "chatId": f"{chat_id}@c.us",
            "message": text
        }, timeout=10)
    except Exception as e:
        print("Send Error:", e)

# ============================================================
#  MAIN LOOP
# ============================================================
def main_loop():
    print("🚀 Hannah is LIVE...")

    while True:
        try:
            url = f"{BASE_URL}/receiveNotification/{GREEN_TOKEN}"
            r = requests.post(url, timeout=20)

            if r.status_code == 200 and r.text:
                data = r.json()

                if data:
                    receipt_id = data.get("receiptId")
                    body = data.get("body", {})

                    if body.get("typeWebhook") == "incomingMessageReceived":

                        msg_data = body.get("messageData", {})

                        msg_text = (
                            msg_data.get("textMessageData", {}).get("text") or
                            msg_data.get("extendedTextMessageData", {}).get("text") or
                            ""
                        )

                        sender = body.get("senderData", {}).get("sender", "")

                        print("📩 Sender:", sender)
                        print("💬 Message:", msg_text)

                        if SHAAN_NUMBER in sender and msg_text:
                            print("⚡ Processing...")

                            reply = ask_hannah(msg_text)

                            print("🤖 Reply:", reply)

                            send_message(SHAAN_NUMBER, reply)

                    if receipt_id:
                        requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}")

            time.sleep(1)

        except Exception as e:
            print("Loop Error:", e)
            time.sleep(5)

# ============================================================
#  KEEP ALIVE SERVER
# ============================================================
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ONLINE")

# ============================================================
#  START
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    threading.Thread(
        target=lambda: HTTPServer(("0.0.0.0", port), PingHandler).serve_forever(),
        daemon=True
    ).start()

    main_loop() 
