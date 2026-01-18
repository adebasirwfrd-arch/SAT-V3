import pandas as pd
import talib

class RiskManager:
    def __init__(self, max_risk_pct=0.02, atr_multiplier=2.0):
        """
        max_risk_pct: Persentase resiko per trade (default 2% atau 0.02)
        atr_multiplier: Jarak SL dalam satuan ATR (default 2x ATR)
        """
        self.max_risk_pct = max_risk_pct
        self.atr_multiplier = atr_multiplier

    def calculate_atr(self, df: pd.DataFrame, period=14):
        # Menggunakan talib untuk menghitung ATR
        try:
            high = df['high'].values.astype(float)
            low = df['low'].values.astype(float)
            close = df['close'].values.astype(float)
            atr = talib.ATR(high, low, close, timeperiod=period)
            return atr[-1]
        except Exception:
            # Fallback manual calculation if TA lib fails
            high_low = df['high'] - df['low']
            return high_low.rolling(period).mean().iloc[-1]

    def calculate_entry_params(self, account_balance, entry_price, atr_value):
        """
        Menghitung:
        1. Stop Loss Price
        2. Take Profit Price (R:R 1:2 minimal)
        3. Quantity (Lot Size) agar resiko terjaga
        """
        
        # 1. Tentukan Jarak Stop Loss (Risk Distance)
        sl_distance = atr_value * self.atr_multiplier
        stop_loss_price = entry_price - sl_distance
        
        # Cegah error jika SL negatif (jika harga aset terlalu kecil)
        if stop_loss_price <= 0:
            stop_loss_price = entry_price * 0.95 # Fallback 5%
            sl_distance = entry_price - stop_loss_price

        # 2. Hitung Berapa Uang yang Siap "Dibakar" (Risk Amount)
        risk_amount = account_balance * self.max_risk_pct
        
        # 3. Hitung Quantity (Lot Size)
        # Rumus: Quantity = Risk Amount / Jarak SL
        # Contoh: Siap rugi $100. Jarak SL $50. Maka beli 2 coin.
        quantity = risk_amount / sl_distance
        
        # 4. Tentukan Take Profit (Minimal 1.5x Risk)
        tp_distance = sl_distance * 1.5
        take_profit_price = entry_price + tp_distance
        
        return {
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'take_profit': take_profit_price,
            'quantity': quantity,
            'risk_amount_usdt': risk_amount,
            'sl_distance': sl_distance
        }
        
    def check_drawdown(self, initial_balance, current_balance):
        """Kill Switch: Cek apakah equity turun terlalu dalam"""
        dd_pct = (initial_balance - current_balance) / initial_balance
        if dd_pct > 0.10: # Jika drawdown > 10%
            return True # TRIGGER KILL SWITCH
        return False
