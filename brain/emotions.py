import random

class Emotions:
    def __init__(self):
        self.traits = ["loyal", "witty", "protective", "sharp"]
        self.current_mood = "calm"

    def update_mood(self, market_condition):
        """Market ke hisaab se mood change karna"""
        if market_condition == "high_volatility":
            self.current_mood = "alert"
        elif market_condition == "weekend":
            self.current_mood = "relaxed"
        else:
            self.current_mood = "calm"

    def get_chat_filler(self):
        """Natural human-like fillers"""
        fillers = ["Yaar,", "Dekho,", "Honestly,", "Basically,", "Sunain,"]
        return random.choice(fillers)

    def format_response(self, text):
        """Response mein jazbaat aur fillers add karna"""
        filler = self.get_chat_filler()
        if self.current_mood == "alert":
            return f"🚨 {filler} market kaafi fast hai. {text}"
        return f"{filler} {text}"
