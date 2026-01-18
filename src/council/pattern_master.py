from .base_general import BaseGeneral
import talib

class PatternMaster(BaseGeneral):
    def __init__(self):
        super().__init__("The Pattern Master", weight=0.10)

    def analyze(self, df):
        open_ = df['open'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        close = df['close'].values.astype(float)

        score = 50
        reasons = []

        # 1. Engulfing
        engulfing = talib.CDLENGULFING(open_, high, low, close)
        if engulfing[-1] == 100:
            score += 30
            reasons.append("Bullish Engulfing")
        elif engulfing[-1] == -100:
            score -= 30
            reasons.append("Bearish Engulfing")

        # 2. Morning/Evening Star
        morning_star = talib.CDLMORNINGSTAR(open_, high, low, close)
        evening_star = talib.CDLEVENINGSTAR(open_, high, low, close)
        
        if morning_star[-1] == 100:
            score += 30
            reasons.append("Morning Star")
        if evening_star[-1] == -100:
            score -= 30
            reasons.append("Evening Star")

        # 3. Hammer / Shooting Star
        hammer = talib.CDLHAMMER(open_, high, low, close)
        if hammer[-1] == 100:
            score += 10
            reasons.append("Hammer")

        if not reasons:
            reasons.append("No pattern detected")

        signal = "NEUTRAL"
        if score >= 60: signal = "BUY"
        elif score <= 40: signal = "SELL"

        return {'score': score, 'signal': signal, 'reason': ", ".join(reasons)}
