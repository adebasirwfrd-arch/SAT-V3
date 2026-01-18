from .base_general import BaseGeneral
import talib
import numpy as np

class VolumeMaster(BaseGeneral):
    def __init__(self):
        super().__init__("The Volume Master", weight=0.20)

    def analyze(self, df):
        if len(df) < 50: 
            return {'score': 50, 'signal': 'NEUTRAL', 'reason': 'No data'}

        close = df['close'].values.astype(float)
        volume = df['volume'].values.astype(float)
        
        # Hitung OBV menggunakan talib
        obv = talib.OBV(close, volume)
        
        # Hitung OBV EMA (Smoothing) untuk melihat tren volume
        obv_ema = talib.EMA(obv, timeperiod=20)
        
        current_obv = obv[-1]
        current_obv_ema = obv_ema[-1]
        
        score = 50
        reasons = []

        # Logic: Uang (Volume) harus mendukung tren
        if current_obv > current_obv_ema:
            score += 30
            reasons.append("Volume Trend Bullish (OBV > EMA)")
        else:
            score -= 30
            reasons.append("Volume Trend Bearish (OBV < EMA)")

        signal = "NEUTRAL"
        if score >= 60: signal = "BUY"
        elif score <= 40: signal = "SELL"

        return {'score': score, 'signal': signal, 'reason': ", ".join(reasons)}
