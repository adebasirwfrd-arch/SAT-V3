from .base_general import BaseGeneral
import pandas as pd

class SmartMoneyMaster(BaseGeneral):
    def __init__(self):
        super().__init__("The Smart Money Master", weight=0.15)

    def analyze(self, df):
        # FVG Logic: Celah antara Candle i-1 (High) dan i+1 (Low)
        # Kita cek 5 candle terakhir saja untuk FVG yang masih "fresh"
        
        score = 50
        reasons = []
        
        # Simple FVG Detection (Last 3 candles completed)
        # Candle 0=terbaru, 1=kemarin, 2=lusa
        # Bullish FVG: Low[-1] > High[-3]
        
        try:
            c_now = df.iloc[-1]
            c_prev = df.iloc[-2]
            c_prev2 = df.iloc[-3]
            
            # Cek Bullish FVG (Demand Zone)
            if df['low'].iloc[-1] > df['high'].iloc[-3]:
                score += 20
                reasons.append("Resting above Bullish FVG")
            
            # Cek Bearish FVG (Supply Zone)
            if df['high'].iloc[-1] < df['low'].iloc[-3]:
                score -= 20
                reasons.append("Rejected from Bearish FVG")
                
        except IndexError:
            reasons.append("Data Insufficient")

        if not reasons:
            reasons.append("No FVG detected")

        signal = "NEUTRAL"
        if score >= 60: signal = "BUY"
        elif score <= 40: signal = "SELL"

        return {'score': score, 'signal': signal, 'reason': ", ".join(reasons)}
