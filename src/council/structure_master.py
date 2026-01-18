from .base_general import BaseGeneral

class StructureMaster(BaseGeneral):
    def __init__(self):
        super().__init__("The Structure Master", weight=0.20)

    def analyze(self, df):
        if len(df) < 50:
            return {'score': 50, 'signal': 'NEUTRAL', 'reason': 'Not enough data'}

        # Support & Resistance (Donchian Channel 20)
        # Menggunakan max high dan min low dari 20 candle terakhir
        recent_high = df['high'].rolling(20).max().iloc[-1]
        recent_low = df['low'].rolling(20).min().iloc[-1]
        close = df['close'].iloc[-1]
        
        # Hitung posisi harga relatif (0% = di support, 100% = di resistance)
        range_size = recent_high - recent_low
        if range_size == 0: range_size = 1 # Prevent div by zero
        
        position_pct = (close - recent_low) / range_size
        
        score = 50
        reasons = []

        # Logic: Beli jika dekat Support (Pantulan), Jual jika dekat Resistance (Atap)
        # Kita cari "Discount" (Murah) vs "Premium" (Mahal)
        
        if position_pct < 0.2: # Harga di 20% bawah (Murah/Dekat Support)
            score += 40
            reasons.append("Near Support (Discount Zone)")
        elif position_pct > 0.8: # Harga di 20% atas (Mahal/Dekat Resistance)
            score -= 40
            reasons.append("Near Resistance (Premium Zone)")
        else:
            reasons.append("Middle of Structure")

        # Final Decision
        signal = "NEUTRAL"
        if score >= 70: signal = "BUY"
        elif score <= 30: signal = "SELL"

        return {'score': score, 'signal': signal, 'reason': ", ".join(reasons)}
