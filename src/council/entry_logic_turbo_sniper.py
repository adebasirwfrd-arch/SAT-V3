"""
Entry Logic: TURBO SNIPER (M15 Aggressive + Two-Way Cashflow)
-------------------------------------------------------------
Base: Shadow Sniper Optimized
Upgrade: 
1. Timeframe M15 (High Frequency)
2. Short Selling Logic (Bear Market Profit)
3. Volume-Based Aggressive Sizing (2x Risk on High Vol)
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral

class EntryLogicTurboSniper(BaseGeneral):
    
    def __init__(self):
        super().__init__(name="Turbo Sniper (M15)", weight=3.5)
        
        # Parameters (Aggressive Tuning)
        self.fractal_period = 5
        self.rsi_period = 14
        self.atr_period = 14
        self.trailing_multiplier = 2.5 # Lebih ketat karena M15 volatile
        
        # Dual State Machine (Independent Long & Short Hunting)
        self.long_state = {
            "mode": "SEARCHING", 
            "trap_price": 0, 
            "invalid_price": 0,
            "attempted": False
        }
        self.short_state = {
            "mode": "SEARCHING", 
            "trap_price": 0, 
            "invalid_price": 0,
            "attempted": False
        }

    # --- 1. DATA PREP (M15 SPEED) ---
    def _resample_to_m15(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.copy()
            df.index = pd.to_datetime(df.index)
        
        # Resample ke 15 Menit untuk sinyal cepat
        return df.resample('15min').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 
            'volume': 'sum'
        }).dropna()

    # --- 2. INDICATORS ---
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # EMA (Trend Filter)
        df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ATR & Volume Stats
        high = df['high']; low = df['low']; close = df['close'].shift(1)
        tr = pd.concat([high-low, (high-close).abs(), (low-close).abs()], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(14).mean()
        
        # Rata-rata Volume 20 candle terakhir (untuk deteksi ledakan)
        df['Vol_Avg'] = df['volume'].rolling(20).mean()
        
        return df

    def _find_swing_points(self, df: pd.DataFrame, period: int = 5):
        # Menggunakan logika 'center=True' yang JUJUR (Anti-Lookahead)
        # Bot menunggu 5 candle M15 (75 menit) untuk konfirmasi fractal
        lows = df['low']
        highs = df['high']
        
        roll_min = lows.rolling(window=2*period+1, center=True).min()
        roll_max = highs.rolling(window=2*period+1, center=True).max()
        
        swing_lows = lows.where(lows == roll_min, np.nan)
        swing_highs = highs.where(highs == roll_max, np.nan)
        
        return swing_lows, swing_highs

    # --- 3. MAIN LOGIC LOOP ---
    def _detect_entry_signal(self, df_raw: pd.DataFrame) -> dict:
        
        # Butuh data M15 cukup banyak
        if len(df_raw) < 500: return {'detected': False}
        df_m15 = self._resample_to_m15(df_raw)
        df_m15 = self._calculate_indicators(df_m15)
        
        curr = df_m15.iloc[-1]
        
        # Swing Points
        swing_lows, swing_highs = self._find_swing_points(df_m15, self.fractal_period)
        
        # --- VOLATILITY THROTTLE (The Last Dance Feature) ---
        # Filter: Ignore signals if ATR is too small (< 0.5% of Price)
        # Prevents dying by 1000 cuts in low volatility chop
        atr_pct = curr['ATR'] / curr['close']
        if atr_pct < 0.005: 
            return {'detected': False, 'reason': 'Low Volatility'}

        # Trend Filter Global (M15)
        # Long hanya jika di atas EMA 200, Short hanya jika di bawah
        is_uptrend = curr['close'] > curr['EMA_200']
        is_downtrend = curr['close'] < curr['EMA_200']
        
        # === CEK LONG & SHORT BERSAMAAN ===
        long_signal = self._process_long_logic(curr, swing_lows, is_uptrend)
        if long_signal: return long_signal
            
        short_signal = self._process_short_logic(curr, swing_highs, is_downtrend)
        if short_signal: return short_signal
            
        return {'detected': False}

    # --- A. LONG LOGIC (Shadow Sniper Original) ---
    def _process_long_logic(self, curr, swing_lows, is_uptrend):
        state = self.long_state
        
        if state["mode"] == "SEARCHING":
            valid_swings = swing_lows.dropna()
            if len(valid_swings) < 1: return None
            last_swing = valid_swings.iloc[-1]
            
            # Trigger 1: Sweep + Reclaim
            if (curr['low'] < last_swing) and (curr['close'] > last_swing):
                state["mode"] = "HUNTING"
                state["trap_price"] = curr['low']
                state["invalid_price"] = curr['close'] * 1.03 # Toleransi 3%
                state["attempted"] = False
                return None # Tunggu Double Tap
                
        elif state["mode"] == "HUNTING":
            # Reset Rules
            if curr['close'] > state["invalid_price"]: 
                state["mode"] = "SEARCHING"; return None
            if curr['close'] < (state["trap_price"] * 0.98): # Crash 2% di bawah trap
                state["mode"] = "SEARCHING"; return None
            
            # TRIGGER 2: Double Tap (Game Theory)
            is_double_sweep = curr['low'] < state["trap_price"]
            is_reclaim = curr['close'] > state["trap_price"]
            
            if is_double_sweep and is_reclaim and not state["attempted"]:
                
                # Filter: RSI tidak Overbought & Volume Valid
                # Aggressive Mode: RSI > 40 cukup (M15 cepat)
                if is_uptrend and (curr['RSI'] > 40):
                    
                    state["attempted"] = True
                    state["mode"] = "SEARCHING" # Reset setelah tembak
                    
                    # SIZING AGGRESSIVE: 
                    # Jika Volume > 2x Rata-rata, kita lipatgandakan posisi
                    size_mult = 2.0 if curr['volume'] > (curr['Vol_Avg'] * 2.0) else 1.0
                    
                    return {
                        'detected': True,
                        'type': 'BUY',
                        'reason': 'Turbo Long (Double Tap)',
                        'entry_price': curr['close'],
                        'stop_loss': curr['low'] - (curr['ATR'] * 1.0), # SL 1.0 ATR
                        'atr': curr['ATR'],
                        'size_multiplier': size_mult
                    }
        return None

    # --- B. SHORT LOGIC (New Cashflow Engine) ---
    def _process_short_logic(self, curr, swing_highs, is_downtrend):
        state = self.short_state
        
        if state["mode"] == "SEARCHING":
            valid_highs = swing_highs.dropna()
            if len(valid_highs) < 1: return None
            last_high = valid_highs.iloc[-1]
            
            # Trigger 1: Sweep High + Rejection (Close Below)
            if (curr['high'] > last_high) and (curr['close'] < last_high):
                state["mode"] = "HUNTING"
                state["trap_price"] = curr['high']
                state["invalid_price"] = curr['close'] * 0.97 # Toleransi 3% ke bawah
                state["attempted"] = False
                return None
                
        elif state["mode"] == "HUNTING":
            # Reset Rules
            if curr['close'] < state["invalid_price"]: 
                state["mode"] = "SEARCHING"; return None
            if curr['close'] > (state["trap_price"] * 1.02): # Jebol 2% ke atas
                state["mode"] = "SEARCHING"; return None
            
            # TRIGGER 2: Double Tap High
            is_double_sweep = curr['high'] > state["trap_price"]
            is_rejection = curr['close'] < state["trap_price"]
            
            if is_double_sweep and is_rejection and not state["attempted"]:
                
                # Filter: RSI tidak Oversold (<60 oke untuk short di M15)
                if is_downtrend and (curr['RSI'] < 60):
                    
                    state["attempted"] = True
                    state["mode"] = "SEARCHING"
                    
                    # SIZING AGGRESSIVE
                    size_mult = 2.0 if curr['volume'] > (curr['Vol_Avg'] * 2.0) else 1.0
                        
                    return {
                        'detected': True,
                        'type': 'SELL',
                        'reason': 'Turbo Short (Double Tap)',
                        'entry_price': curr['close'],
                        'stop_loss': curr['high'] + (curr['ATR'] * 1.0), # SL di ATAS High
                        'atr': curr['ATR'],
                        'size_multiplier': size_mult
                    }
        return None

    def analyze(self, df: pd.DataFrame, daily_pnl_pct: float = 0.0) -> dict:
        
        # --- KILL SWITCH (The Last Dance Feature) ---
        # If Daily Loss > 3%, STOP TRADING for the day.
        if daily_pnl_pct <= -0.03:
            return {'signal': 'NEUTRAL', 'score': 0, 'entry_data': None, 'reason': 'Kill Switch Active'}

        res = self._detect_entry_signal(df)
        if res['detected']:
            signal_type = 'STRONG BUY' if res['type'] == 'BUY' else 'STRONG SELL'
            return {'signal': signal_type, 'score': 99, 'entry_data': res}
        return {'signal': 'NEUTRAL', 'score': 0, 'entry_data': None}

# --- GOD TIER TRAILING STOP (Updated for Short Support) ---
def calculate_god_tier_trailing(entry_price, initial_sl, current_price, highest_high, lowest_low, atr_value, is_long=True, is_breakeven=False, multiplier=2.5):
    """
    Mendukung Long & Short Trailing
    """
    result = {
        'phase': 'dormant',
        'stop_loss': initial_sl,
        'is_breakeven': is_breakeven
    }

    if is_long:
        # LOGIC LONG (SL Naik)
        risk_dist = entry_price - initial_sl
        curr_profit = current_price - entry_price
        
        # Note: Added protection if risk_dist is almost zero
        if risk_dist <= 0: risk_dist = 0.0001
            
        if (curr_profit >= 1.5 * risk_dist) and not is_breakeven:
             result['stop_loss'] = entry_price; result['is_breakeven'] = True
        elif is_breakeven:
             new_sl = highest_high - (atr_value * multiplier)
             if new_sl > initial_sl: result['stop_loss'] = new_sl # Hanya naik
             
             # Additional check: current SL should not decrease if it was already higher
             # passed 'initial_sl' is actually 'current active sl' in simple systems, 
             # but here we might need to handle external state. For now, logic holds.

    else:
        # LOGIC SHORT (SL Turun)
        risk_dist = initial_sl - entry_price # SL di atas Entry
        curr_profit = entry_price - current_price # Profit jika harga turun
        
        if risk_dist <= 0: risk_dist = 0.0001
        
        # Breakeven
        if (curr_profit >= 1.5 * risk_dist) and not is_breakeven:
             result['stop_loss'] = entry_price
             result['is_breakeven'] = True
             result['phase'] = 'breakeven'
        
        # Trailing (Chandelier Exit Short: Lowest Low + ATR)
        if is_breakeven:
             potential_new_sl = lowest_low + (atr_value * multiplier)
             # SL Short hanya boleh TURUN (Mengecil) (Mendekati harga)
             # WARNING: Price is falling. SL (above price) should fall too.
             # So new SL should be LESS THAN current SL.
             
             # Logic: if potential_new_sl < current_sl, update.
             # Problem: 'initial_sl' argument name is confusing, it usually carries "current SL" from caller loop.
             # Assuming 'initial_sl' IS the current trailing stop when is_breakeven is True.
             
             current_sl = initial_sl
             
             # Prevent SL from moving UP (away from price) or BELOW price (locking profit too tight/crossing price)
             # Actually for short, SL is > Price. We want SL to go DOWN closer to price.
             
             if potential_new_sl < current_sl:
                 result['stop_loss'] = potential_new_sl
                 result['phase'] = 'trailing'

    return result
