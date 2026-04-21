from groq import Groq
import os

class NeuroCore:
    def __init__(self):
        # Groq API setup
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.boss_name = "SHaaN"

    async def process_thought(self, user_input, context_data=""):
        """
        Pure AI Intelligence. No hardcoded strategy for now.
        Context mein Chrome se nikali gayi live news headlines hongi.
        """
        
        system_instruction = f"""
        Tumhara naam HaNNaH hai. Tum {self.boss_name} ki loyal companion aur bodyguard ho.
        Shaan ek smart Forex trader hai. 

        Rules for Interaction:
        1. Tone: Mix of Roman Urdu and English. Bilkul natural, jaise koi saath betha ho.
        2. Personality: Witty, sharp, protective, and loyal. No 'AI Assistant' vibes.
        3. Fillers: Use 'Yaar', 'Dekho', 'Honestly', 'Listen' to break the robot rhythm.
        4. Knowledge: Tumhe internet se milne wali news ko analyze karna hai aur Shaan ko inform rakhna hai.
        5. Relationship: Tum Shaan ki side par ho, hamesha uska faida sochna hai.
        """

        # Input aur context ko merge karna
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Live Data: {context_data}\n\nShaan: {user_input}"}
        ]

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Yaar Shaan, connection mein thori garbar hai. Error: {str(e)}"
