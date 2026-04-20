import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from groq import Groq
from datetime import datetime

# ================= CONFIG =================
GREEN_INSTANCE = "7107570157"
GREEN_TOKEN    = "c10690c2015d46848115a8e6b53efa6c21e0b0bc7e79464a95"
GROQ_API_KEY   = "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"
FMP_API_KEY    = "ogECGJ7AGs4W78mtryA6EGPTiiwH6bok"
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"

# ================= AI =================
def get_economic_calendar():
    print("📊 Calling FMP API...")
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=10)
        print("📊 FMP Status:", r.status_code)

        data = r.json()
        return "OK"
    except Exception as e:
        print("❌ FMP Error:", e)
        return "FMP failed"

def ask_hannah(user_text):
    print("🧠 Calling Groq API...")
    try:
        client = Groq(api_key=GROQ_API_KEY)

        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
        )

        print("🧠 Groq Success")
        return resp.choices[0].message.content

    except Exception as e:
        print("❌ Groq Error:", e)
        return "AI failed"

# ================= SEND =================
def send_message(chat_id, text):
    try:
        url = f"{BASE_URL}/sendMessage/{GREEN_TOKEN}"

        chat_id = chat_id if "@c.us" in chat_id else f"{chat_id}@c.us"

        print("📤 Sending to:", chat_id)

        r = requests.post(url, json={
            "chatId": chat_id,
            "message": text
        }, timeout=10)

        print("📤 Send status:", r.status_code)

    except Exception as e:
        print("❌ Send Error:", e)

# ================= LOOP =================
def main_loop():
    print("🚀 BOT STARTED...")

    while True:
        try:
            url = f"{BASE_URL}/receiveNotification/{GREEN_TOKEN}"
            r = requests.post(url, timeout=20)

            print("\n====== NEW POLL ======")
            print("STATUS:", r.status_code)

            if r.status_code == 200 and r.text:
                data = r.json()
                print("📦 FULL DATA:", data)

                if data:
                    receipt_id = data.get("receiptId")
                    body = data.get("body", {})

                    print("📩 BODY:", body)

                    msg_data = body.get("messageData", {})

                    msg_text = (
                        msg_data.get("textMessageData", {}).get("text") or
                        msg_data.get("extendedTextMessageData", {}).get("text") or
                        msg_data.get("conversation") or
                        ""
                    )

                    sender = body.get("senderData", {}).get("sender", "")

                    print("👤 Sender:", sender)
                    print("💬 Message:", msg_text)

                    # 🔥 FORCE EXECUTION (no conditions)
                    if msg_text:
                        print("⚡ MESSAGE DETECTED → CALLING AI")

                        # test FMP
                        get_economic_calendar()

                        # test Groq
                        reply = ask_hannah(msg_text)

                        print("🤖 Reply:", reply)

                        send_message(sender, reply)

                    if receipt_id:
                        requests.delete(f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}")

            time.sleep(1)

        except Exception as e:
            print("❌ LOOP ERROR:", e)
            time.sleep(5)

# ================= SERVER =================
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ONLINE")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

# ================= START =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    threading.Thread(
        target=lambda: HTTPServer(("0.0.0.0", port), PingHandler).serve_forever(),
        daemon=True
    ).start()

    main_loop()
