class TradingStrategy:
    def __init__(self):
        self.pairs = ["XAUUSD", "EURUSD", "GBPUSD"]
        
    def check_bias(self, dxy_sentiment, news_impact):
        """
        DXY (Dollar Index) aur news impact ko mix karke trade bias nikalna.
        """
        if dxy_sentiment == "Strong" and "Red Folder" in news_impact:
            return "BEARISH for Gold/EU/GU. Look for SMT divergence."
        elif dxy_sentiment == "Weak":
            return "BULLISH bias. Watch for internal range liquidity sweeps."
        
        return "Market is in Consolidation. Stay flat, Boss."
