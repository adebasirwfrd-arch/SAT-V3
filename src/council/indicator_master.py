from .base_general import BaseGeneral
import talib
import numpy as np

class IndicatorMaster(BaseGeneral):
    def __init__(self):
        super().__init__("The Indicator Master", weight=0.05) # Bobot kecil hanya konfirmasi

    def analyze(self, df):
        close = df['close'].values.astype(float)
        
        # RSI
        rsi = talib.RSI(close, timeperiod=14)
        current_rsi = rsi[-1]
        
        # MACD
        macd_line, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        current_macd = macd_line[-1]
        current_signal = macd_signal[-1]

        score = 50
        reasons = []

        # Logic RSI
        if current_rsi < 30:
            score += 25
            reasons.append("RSI Oversold")
        elif current_rsi > 70:
            score -= 25
            reasons.append("RSI Overbought")
        else:
            reasons.append("RSI Neutral")

        # Logic MACD
        if current_macd > current_signal:
            score += 25
            reasons.append("MACD Bullish Cross")
        else:
            score -= 25
            reasons.append("MACD Bearish Cross")

        signal = "NEUTRAL"
        if score >= 70: signal = "BUY"
        elif score <= 30: signal = "SELL"

        return {'score': score, 'signal': signal, 'reason': ", ".join(reasons)}
