from groq import Groq
import os

class NeuroCore:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.boss_name = "SHaaN"

    async def process_thought(self, user_input, context_data=""):
        # context_data mein wo news ya chrome ka data aayega jo HaNNaH ne fetch kiya
        system_prompt = f"""
        Tumhara naam HaNNaH hai. Tum {self.boss_name} ki loyal AI bodyguard aur companion ho.
        Shaan ek smart Forex trader hai. 
        Tone: Mix of Roman Urdu and English. Natural, witty, and protective. 
        Agar context mein news hai, toh usse SMC/ICT point of view se analyze karo.
        """
        
        full_prompt = f"User says: {user_input}\nContext from Web/News: {context_data}"
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Yaar Shaan, Groq connect nahi ho raha. Check karo key sahi hai? Error: {str(e)}"
