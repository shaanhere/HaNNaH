import imaplib
import email
from email.header import decode_header
import os

class EmailAccess:
    def __init__(self):
        self.username = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")
        self.imap_url = "imap.gmail.com"

    async def get_unread_summaries(self):
        """Unread emails ko scan karke summary dena"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_url)
            mail.login(self.username, self.password)
            mail.select("inbox")

            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            if not email_ids:
                return "Inbox bilkul saaf hai, Boss. Koi naya jhamela nahi hai."

            summaries = []
            for e_id in email_ids[-3:]: # Sirf latest 3 emails
                res, msg = mail.fetch(e_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        subject = decode_header(msg["Subject"])[0][0]
                        sender = msg.get("From")
                        summaries.append(f"From: {sender} | Subject: {subject}")

            mail.logout()
            return "Kujh naye emails hain. Important lag rahe hain: " + " | ".join(summaries)
            
        except Exception as e:
            return f"Email access mein thoda masla aa raha hai: {str(e)}"
