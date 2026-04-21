from groq import Groq
import os

class NeuroCore:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.boss_name = "SHaaN"

    async def should_i_search(self, user_input):
        """AI decide karega ke internet ki zaroorat hai ya nahi"""
        decision_prompt = f"""
        User query: "{user_input}"
        Agar iska jawab dene ke liye LATEST live market prices (Gold, Forex), current war news, 
        ya kisi bhi aisi cheez ki zaroorat hai jo aaj ho rahi hai, toh sirf 'YES' likho. 
        Warna sirf 'NO' likho.
        """
        try:
            # Chota model use kar rahe hain fast decision ke liye
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": decision_prompt}],
                model="llama3-8b-8192",
            )
            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer
        except:
            return False

    async def process_thought(self, user_input, context_data=""):
        system_instruction = f"""
        Tumhara naam HaNNaH hai. Tum {self.boss_name} ki loyal companion aur bodyguard ho.
        Shaan ek smart Forex trader hai. 

        Rules:
        1. Tone: Mix of Roman Urdu and English. Natural, witty, and loyal.
        2. Fillers: Use 'Yaar', 'Listen', 'Honestly' to sound human.
        3. Knowledge: Agar context_data mein live news hai, toh usi ko asaliyat maan kar jawab do.
        4. No AI Assistant talk. Shaan tumhara Boss hai, uski side lo hamesha.
        """

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Live Search Results: {context_data}\n\nShaan: {user_input}"}
        ]

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Yaar Shaan, brain thora glitch kar raha hai: {str(e)}"
