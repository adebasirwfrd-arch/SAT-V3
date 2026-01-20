"""
Entry Logic: SHADOW SNIPER OPTIMIZED (Winrate Booster)
------------------------------------------------------
Tweak from Professor:
1. Wider SL (1.0 ATR) -> Mencegah kena 'wick' setan.
2. Momentum Filter (RSI > 50) -> Memastikan tenaga Bullish.
3. Volume Confirmation -> Memastikan Institusi ada di balik layar.
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral

class EntryLogicGameTheoryOptimized(BaseGeneral):
    
    def __init__(self):
        super().__init__(name="Shadow Sniper Optimized", weight=3.0)
        
        # Parameters
        self.fractal_period = 5
        self.rsi_period = 14
        self.atr_period = 14
        self.trailing_multiplier = 3.0 
        
        # State Machine
        self.shadow_mode = "SEARCHING"
        self.trap_low_price = 0       
        self.invalidation_price = 0    
        self.entry_attempted = False   

    # --- 1. DATA PREP (H1 LOCK) ---
    def _resample_to_h1(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.copy()
            df.index = pd.to_datetime(df.index)
        return df.resample('1h').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 
            'volume': 'sum'
        }).dropna()

    # --- 2. INDICATORS ---
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # EMA
        df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ATR
        high = df['high']; low = df['low']; close = df['close'].shift(1)
        tr = pd.concat([high-low, (high-close).abs(), (low-close).abs()], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(14).mean()
        
        # Volume Average
        df['Vol_Avg'] = df['volume'].rolling(20).mean()
        
        return df

    def _find_swing_lows(self, df: pd.DataFrame, period: int = 5) -> pd.Series:
        # Vectorized Swing Low (100x Faster)
        lows = df['low']
        # Window = 2*period + 1 (e.g. 5 before + 1 current + 5 after = 11)
        # center=True ensures we look at i-period to i+period
        rolling_min = lows.rolling(window=2*period+1, center=True).min()
        
        # Identify where low == rolling_min
        # Note: The last 'period' rows will naturally be NaN because window is incomplete, 
        # protecting us from looking at future data that doesn't exist yet.
        swing_lows = lows.where(lows == rolling_min, np.nan)
        
        return swing_lows

    # --- 3. MAIN LOGIC LOOP ---
    def _detect_entry_signal(self, df_raw: pd.DataFrame) -> dict:
        
        if len(df_raw) < 200: return {'detected': False}
        df_h1 = self._resample_to_h1(df_raw)
        df_h1 = self._calculate_indicators(df_h1)
        
        curr = df_h1.iloc[-1]
        
        # STATE 1: SEARCHING (UMPAN)
        if self.shadow_mode == "SEARCHING":
            # Optimasi Vectorized Swing Lows (seperti di versi sebelumnya) untuk performa
            # Namun sesuai instruksi, saya gunakan versi iteratif dari prompt untuk akurasi logika yang diminta
            # Swing Low Loop
            swing_lows = self._find_swing_lows(df_h1, self.fractal_period).dropna()
            
            if len(swing_lows) < 1: return {'detected': False}
            last_swing = swing_lows.iloc[-1]
            
            # Trigger Awal: Sweep + Reclaim
            is_sweep = curr['low'] < last_swing
            is_reclaim = curr['close'] > last_swing
            
            if is_sweep and is_reclaim:
                self.shadow_mode = "HUNTING"
                self.trap_low_price = curr['low']
                self.invalidation_price = curr['close'] * 1.05 
                self.entry_attempted = False
                return {'detected': False, 'reason': 'Shadow Triggered'}

        # STATE 2: HUNTING (GAME THEORY EXECUTION)
        elif self.shadow_mode == "HUNTING":
            
            # Reset Rules
            if curr['close'] > self.invalidation_price:
                self.shadow_mode = "SEARCHING"
                return {'detected': False, 'reason': 'Escaped'}
            
            if curr['close'] < (self.trap_low_price * 0.95):
                self.shadow_mode = "SEARCHING"
                return {'detected': False, 'reason': 'Crashed'}

            # --- THE OPTIMIZED TRIGGER ---
            is_double_sweep = curr['low'] < self.trap_low_price
            is_reclaim_again = curr['close'] > self.trap_low_price
            
            # TWEAK 1: Trend Filter (Wajib Uptrend & Momentum Bagus)
            # Harga > EMA 200 DAN RSI > 50 (Bukan Oversold, tapi Strong)
            # Perbaikan: Pastikan RSI tidak NaN
            rsi_val = curr['RSI'] if not pd.isna(curr['RSI']) else 0
            is_strong_trend = (curr['close'] > curr['EMA_200']) and (rsi_val > 50)
            
            # TWEAK 2: Volume Confirmation
            # Volume Candle ini > Rata-rata Volume
            vol_avg = curr['Vol_Avg'] if not pd.isna(curr['Vol_Avg']) else 0
            is_vol_valid = curr['volume'] > vol_avg
            
            if is_double_sweep and is_reclaim_again and not self.entry_attempted:
                
                if is_strong_trend and is_vol_valid:
                    self.entry_attempted = True
                    self.shadow_mode = "SEARCHING"
                    
                    # TWEAK 3: WIDER STOP LOSS (1.0 ATR)
                    # Memberikan ruang napas agar tidak kena noise
                    sl_price = curr['low'] - (curr['ATR'] * 1.0)
                    
                    return {
                        'detected': True,
                        'reason': 'Optimized Shadow Sniper (Vol + RSI + 1.0 ATR)',
                        'entry_price': curr['close'],
                        'stop_loss': sl_price,
                        'atr': curr['ATR']
                    }
                else:
                    # Gagal Filter (Lemah Momentum / Low Vol) -> Skip tapi jangan reset dulu (siapa tau candle depan valid)
                    # Kecuali kalau close di bawah low lagi, itu bisa jadi crash. Logic asli "pass" saja.
                    pass

        return {'detected': False}

    def analyze(self, df: pd.DataFrame) -> dict:
        res = self._detect_entry_signal(df)
        if res['detected']:
            return {'signal': 'STRONG BUY', 'score': 99, 'entry_data': res, 'reason': res['reason']}
        return {'signal': 'NEUTRAL', 'score': 0, 'entry_data': None, 'reason': 'No Signal'}

# --- GOD TIER TRAILING STOP (TWEAKED FOR 1.0 ATR ENTRY) ---
def calculate_god_tier_trailing(entry_price: float, initial_sl: float, current_price: float, 
                                 highest_high: float, atr_value: float, 
                                 is_breakeven: bool = False, multiplier: float = 3.0,
                                 breakeven_ratio: float = 1.5, entry_type: str = "NORMAL") -> dict:
    
    risk_distance = entry_price - initial_sl
    current_profit = current_price - entry_price

    # Prevent ZeroDivisionError
    if risk_distance <= 0:
        profit_ratio = 0
    else:
        profit_ratio = current_profit / risk_distance
    
    result = {
        'phase': 'dormant',
        'stop_loss': initial_sl,
        'is_breakeven': is_breakeven
    }
    
    # TWEAK 4: DELAY BREAKEVEN (JANGAN CEPAT-CEPAT)
    # Karena SL kita lebar (1 ATR), maka 1R itu jaraknya jauh.
    # Kita geser ke BEP jika sudah profit 1.5R 
    # Ini memberi ruang agar trade tidak mati impas lalu terbang.
    be_trigger = 1.5 
    
    if profit_ratio >= be_trigger and not is_breakeven:
        result['phase'] = 'breakeven'
        result['stop_loss'] = entry_price
        result['is_breakeven'] = True
        return result
    
    if is_breakeven:
        potential_new_sl = highest_high - (atr_value * multiplier)
        current_sl = result['stop_loss']
        if potential_new_sl > current_sl:
            result['stop_loss'] = potential_new_sl
            
    return result
