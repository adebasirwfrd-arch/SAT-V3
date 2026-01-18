from .base_general import BaseGeneral

class GeometryMaster(BaseGeneral):
    def __init__(self):
        super().__init__("The Geometry Master", weight=0.10)

    def analyze(self, df):
        # Cari Swing High & Low dalam 50 candle terakhir
        period = 50
        if len(df) < period: 
            return {'score': 50, 'signal': 'NEUTRAL', 'reason': 'No Data'}
        
        recent_high = df['high'].rolling(period).max().iloc[-1]
        recent_low = df['low'].rolling(period).min().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Hitung Level Fib 0.618 dari range tersebut
        diff = recent_high - recent_low
        fib_618 = recent_low + (diff * 0.618) # Golden Pocket Retracement Upside
        
        # Toleransi 0.5%
        tolerance = diff * 0.005
        
        score = 50
        reasons = []
        
        # Jika harga berada di dekat level 0.618
        if abs(current_price - fib_618) < tolerance:
            score += 30
            reasons.append("Testing Golden Ratio 0.618")
        else:
            reasons.append("Price not at Fib level")
        
        signal = "NEUTRAL"
        if score >= 60: signal = "BUY"
        elif score <= 40: signal = "SELL"

        return {'score': score, 'signal': signal, 'reason': ", ".join(reasons)}
