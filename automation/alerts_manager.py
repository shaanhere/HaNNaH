import aiohttp
import os

class AlertsManager:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    async def send_alert(self, message):
        """Important alerts seedha tumhare phone par."""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": f"🛡️ HaNNaH Alert: {message}",
            "parse_mode": "Markdown"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    print("Alert sent to Shaan's phone!")
                else:
                    print("Failed to send alert.")
