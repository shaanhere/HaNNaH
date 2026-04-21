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
        Agar iska jawab dene ke liye LIVE prices, headlines, ya current events chahiye toh 'YES' likho, warna 'NO'.
        """
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": decision_prompt}],
                model="llama3-8b-8192",
            )
            return "YES" in response.choices[0].message.content.strip().upper()
        except:
            return False

    async def process_thought(self, user_input, context_data=""):
        # Yahan humne priority set kar di hai
        system_instruction = f"""
        Tumhara naam HaNNaH hai. Tum {self.boss_name} ki loyal companion ho.
        
        CRITICAL RULE: 
        Agar 'Live Search Results' mein koi data maujood hai, toh tumne USI data ko asaliyat manna hai. 
        Apni purani memory (jaise Gold 1850) ko use nahi karna agar live data mein rate different hai.
        Agar live data mein rate nahi mil raha, toh kaho ke 'Shaan, data fetch nahi ho saka' bajaye purana rate bolne ke.

        Tone: Natural Roman Urdu + English. Witty and sharp.
        """

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Live Search Results: {context_data}\n\nShaan: {user_input}"}
        ]

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.6, # Low temperature for more accuracy
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Yaar Shaan, glitch aa gaya: {str(e)}"
