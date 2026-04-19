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
BASE_URL       = f"https://api.green-api.com/waInstance{GREEN_INSTANCE}"
SHAAN_NUMBER   = "923479165100@c.us"

HANNAH_SOUL = "You are HaNNaH, SHaaN's loyal market wingman. Speak in Roman Urdu/English mix. Be bold and direct."

def ask_hannah(user_text):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            messages=[{"role": "system", "content": HANNAH_SOUL}, {"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
            temperature=0.7, # Safe temperature
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Groq Error: {str(e)}"

def send_message(chat_id, text):
    try:
        url = f"{BASE_URL}/sendMessage/{GREEN_TOKEN}"
        payload = {"chatId": chat_id, "message": text}
        r = requests.post(url, json=payload, timeout=10)
        print(f"[SEND] Status: {r.status_code}")
    except Exception as e:
        print(f"[SEND ERROR] {e}")

# --- MAIN LOOP ---
def main_loop():
    print("🚀 HaNNaH Debug Loop Started...")
    while True:
        try:
            # Check notifications
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
                        
                        print(f"📩 New Message from {sender}: {msg_text}")
                        
                        if sender == SHAAN_NUMBER:
                            response = ask_hannah(msg_text)
                            send_message(sender, response)
                    
                    # ALWAYS delete notification to keep the queue moving
                    del_url = f"{BASE_URL}/deleteNotification/{GREEN_TOKEN}/{receipt_id}"
                    requests.delete(del_url)
                    print(f"✅ Notification {receipt_id} cleared.")
            
            time.sleep(2) # Short sleep to keep it responsive
        except Exception as e:
            print(f"❌ Loop Error: {e}")
            time.sleep(5)

# Keep-alive server
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ALIVE")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(("0.0.0.0", port), PingHandler).serve_forever(), daemon=True).start()
    main_loop()
