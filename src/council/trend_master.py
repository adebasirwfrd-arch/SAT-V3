from .base_general import BaseGeneral
import talib
import numpy as np

class TrendMaster(BaseGeneral):
    def __init__(self):
        super().__init__("The Trend Master", weight=0.20)

    def analyze(self, df):
        if len(df) < 200:
            return {'score': 50, 'signal': 'NEUTRAL', 'reason': 'Not enough data'}

        close = df['close'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        
        # Indicators
        ema_200 = talib.EMA(close, timeperiod=200)
        
        # Ichimoku (manual calculation since talib doesn't have it)
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
        period9_high = talib.MAX(high, timeperiod=9)
        period9_low = talib.MIN(low, timeperiod=9)
        tenkan = (period9_high + period9_low) / 2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2
        period26_high = talib.MAX(high, timeperiod=26)
        period26_low = talib.MIN(low, timeperiod=26)
        kijun = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen)/2
        span_a = (tenkan + kijun) / 2
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2
        period52_high = talib.MAX(high, timeperiod=52)
        period52_low = talib.MIN(low, timeperiod=52)
        span_b = (period52_high + period52_low) / 2
        
        last_close = close[-1]
        last_ema = ema_200[-1]
        last_span_a = span_a[-1]
        last_span_b = span_b[-1]
        last_tenkan = tenkan[-1]
        last_kijun = kijun[-1]

        score = 0
        reasons = []

        # 1. EMA 200 (40 pts)
        if last_close > last_ema:
            score += 40
            reasons.append("Above EMA200")
        else:
            reasons.append("Below EMA200")

        # 2. Cloud (30 pts)
        if last_close > last_span_a and last_close > last_span_b:
            score += 30
            reasons.append("Above Cloud")
        elif last_close < last_span_a and last_close < last_span_b:
            reasons.append("Below Cloud")
        else:
            score += 15
            reasons.append("Inside Cloud")

        # 3. TK Cross (30 pts)
        if last_tenkan > last_kijun:
            score += 30
            reasons.append("TK Golden Cross")
        elif last_tenkan < last_kijun:
            reasons.append("TK Death Cross")
        else:
            score += 15

        # Decision
        signal = "NEUTRAL"
        if score >= 70: signal = "BUY"
        elif score <= 30: signal = "SELL"
        
        return {'score': score, 'signal': signal, 'reason': ", ".join(reasons)}
