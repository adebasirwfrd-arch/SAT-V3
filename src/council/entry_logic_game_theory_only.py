"""
Entry Logic: SHADOW SNIPER (Game Theory Only + EMA Filter)
----------------------------------------------------------
Concept:
1. PHASE 1 (SHADOW): Deteksi Sweep+Reclaim+RSI. JANGAN TRADE. Anggap ini "Umpan".
2. PHASE 2 (HUNTING): Tunggu harga menjebol Low dari Phase 1 (Double Sweep).
3. PHASE 3 (EXECUTION): Entry HANYA JIKA terjadi Reclaim Kedua DAN Harga > EMA 200.
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral

class EntryLogicGameTheoryOnly(BaseGeneral):
    
    def __init__(self):
        super().__init__(name="Shadow Sniper (GT Only)", weight=2.5)
        
        # Parameters
        self.fractal_period = 5
        self.rsi_period = 14
        self.atr_period = 14
        self.trailing_multiplier = 3.0
        
        # State Machine (Memory)
        self.shadow_mode = "SEARCHING" # SEARCHING -> HUNTING
        self.trap_low_price = 0        # Harga Low dari sinyal pertama (Umpan)
        self.invalidation_price = 0    # Batas toleransi
        self.entry_attempted = False   # Mencegah spam entry di zona yang sama

    # --- 1. INTERNAL H1 RESAMPLING (Wajib) ---
    def _resample_to_h1(self, df: pd.DataFrame) -> pd.DataFrame:
        # Check if already H1 (Optimization for Hybrid Engine)
        if len(df) > 1:
            diff = (df.index[1] - df.index[0]).total_seconds()
            if diff >= 3600: return df

        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.copy()
            df.index = pd.to_datetime(df.index)
        return df.resample('1h').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 
            'volume': 'sum' # Penting untuk validasi volume
        }).dropna()

    # --- 2. INDICATORS ---
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # EMA Filter (Perisai Utama)
        df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # ATR & RSI
        delta = df['close'].diff()
        offset_pos = delta.copy()
        offset_pos[offset_pos < 0] = 0
        offset_neg = delta.copy()
        offset_neg[offset_neg > 0] = 0
        
        avg_gain = offset_pos.rolling(window=14).mean()
        avg_loss = offset_neg.abs().rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        high = df['high']; low = df['low']; close = df['close'].shift(1)
        tr = pd.concat([high-low, (high-close).abs(), (low-close).abs()], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(14).mean()
        
        return df

    def _find_swing_lows(self, df: pd.DataFrame, period: int = 5) -> pd.Series:
        # Vectorized Swing Low Detection (O(N) speedup vs O(N^2) loop)
        lows = df['low']
        window = 2 * period + 1
        # center=True ensures we look at [i-period, i+period]
        # NaN at edges (unconfirmed swings) is desired behavior
        rolling_min = lows.rolling(window=window, center=True).min()
        
        # Filter: strictly equal to local min
        swing_lows = lows[lows == rolling_min]
        
        return swing_lows

    # --- 3. MAIN LOGIC LOOP ---
    def _detect_entry_signal(self, df_raw: pd.DataFrame) -> dict:
        
        # A. PREPARE DATA H1
        if len(df_raw) < 200: return {'detected': False}
        df_h1 = self._resample_to_h1(df_raw)
        df_h1 = self._calculate_indicators(df_h1)
        
        curr = df_h1.iloc[-1]
        
        # B. STATE 1: SEARCHING (Mencari Umpan / Sinyal Pertama)
        if self.shadow_mode == "SEARCHING":
            swing_lows = self._find_swing_lows(df_h1, self.fractal_period).dropna()
            if len(swing_lows) < 1: return {'detected': False}
            
            last_swing = swing_lows.iloc[-1]
            
            # Logic Lama (Sweep + Reclaim + RSI)
            is_sweep = curr['low'] < last_swing
            is_reclaim = curr['close'] > last_swing
            # is_rsi_div = curr['RSI'] > 30 # Simple filter removed to match logic focus on structure first? 
            # Prompt says: is_rsi_div = curr['RSI'] > 30 
            is_rsi_div = curr['RSI'] > 30 
            
            if is_sweep and is_reclaim and is_rsi_div:
                # KITA TIDAK ENTRY DI SINI. INI HANYA PEMICU.
                self.shadow_mode = "HUNTING"
                self.trap_low_price = curr['low'] # Ini titik jebakan pertama
                self.invalidation_price = curr['close'] * 1.05 # Reset jika harga lari 5%
                self.entry_attempted = False
                # Return False karena kita belum mau trade
                return {'detected': False, 'reason': 'Shadow Signal Detected. Hunting Mode ON.'}

        # C. STATE 2: HUNTING (Menunggu Game Theory / Double Tap)
        elif self.shadow_mode == "HUNTING":
            
            # Reset Rule: Jika harga lari terlalu jauh (sudah moon tanpa kita) -> Lupakan
            if curr['close'] > self.invalidation_price:
                self.shadow_mode = "SEARCHING"
                return {'detected': False, 'reason': 'Price escaped. Resetting.'}
            
            # Reset Rule: Jika harga crash parah jauh di bawah jebakan -> Batalkan
            if curr['close'] < (self.trap_low_price * 0.95): # Drop 5% di bawah low
                self.shadow_mode = "SEARCHING"
                return {'detected': False, 'reason': 'Zone invalidated (Deep Crash).'}

            # --- THE GAME THEORY TRIGGER ---
            # Syarat 1: Terjadi "Double Sweep" (Harga tembus di bawah Low Umpan Pertama)
            is_double_sweep = curr['low'] < self.trap_low_price
            
            # Syarat 2: Terjadi Reclaim Kembali (Harga tutup di atas Low Umpan)
            is_reclaim_again = curr['close'] > self.trap_low_price
            
            # Syarat 3: FILTER EMA (PERMINTAAN ANDA)
            # Hanya eksekusi Game Theory jika Trend Bullish (Harga > EMA 200)
            is_trend_safe = curr['close'] > curr['EMA_200']
            
            if is_double_sweep and is_reclaim_again and not self.entry_attempted:
                
                if is_trend_safe:
                    # FIRE!!! INI ADALAH TIKUS KEDUA YANG DAPAT KEJU.
                    self.entry_attempted = True # One shot per zone
                    self.shadow_mode = "SEARCHING" # Reset setelah tembak
                    
                    sl_price = curr['low'] - (curr['ATR'] * 0.5)
                    
                    return {
                        'detected': True,
                        'reason': 'Game Theory Executed (Double Tap + EMA Filter)',
                        'entry_price': curr['close'],
                        'stop_loss': sl_price,
                        'atr': curr['ATR']
                    }
                else:
                    # Ada sinyal Double Tap, TAPI Trend Bearish (EMA Filter Block)
                    # Kita batalkan trade ini demi keselamatan.
                    self.shadow_mode = "SEARCHING"
                    return {'detected': False, 'reason': 'Game Theory Filtered by EMA 200 (Bear Market)'}

        return {'detected': False}

    def analyze(self, df: pd.DataFrame) -> dict:
        res = self._detect_entry_signal(df)
        if res['detected']:
            return {'signal': 'STRONG BUY', 'score': 99, 'entry_data': res, 'reason': res['reason']}
        return {'signal': 'NEUTRAL', 'score': 0, 'entry_data': None, 'reason': 'No Signal'}
    
    # Required for interface
    def game_theory_manager(self, df: pd.DataFrame, support_zone: float) -> dict: return {'action': 'NO_ACTION'}
    def record_trade_result(self, result: str, trap_low: float = 0): pass

# --- GOD TIER TRAILING STOP ---
def calculate_god_tier_trailing(entry_price: float, initial_sl: float, current_price: float, 
                                 highest_high: float, atr_value: float, 
                                 is_breakeven: bool = False, multiplier: float = 3.0,
                                 breakeven_ratio: float = 1.5, entry_type: str = "NORMAL") -> dict:
    risk_distance = entry_price - initial_sl
    if risk_distance <= 0: return {'stop_loss': initial_sl, 'phase': 'error'}
    
    current_profit = current_price - entry_price
    profit_ratio = current_profit / risk_distance
    
    result = {
        'phase': 'dormant',
        'stop_loss': initial_sl,
        'is_breakeven': is_breakeven
    }
    
    if profit_ratio >= breakeven_ratio and not is_breakeven:
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
