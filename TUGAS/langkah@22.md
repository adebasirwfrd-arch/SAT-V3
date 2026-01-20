Tentu, Ade. Ini adalah keputusan yang sangat logis. Kita kembali ke DNA Asli (Sweep + Reclaim) yang sudah terbukti punya R:R tinggi, tapi kita ganti "kacamata"-nya dengan filter tajam dari Forex Sarjana agar tidak menembak sembarangan.

Kita akan menamakannya EntryLogicMasterV2.

Strategi ini menggabungkan:

Core: Liquidity Sweep + Reclaim (Warisan V1).

Filter Forex Sarjana:

Regime: EMA 50 > EMA 200 (Wajib Uptrend).

Trigger: Reclaim harus berupa Engulfing (Bukan candle hijau lemah).

Momentum: RSI harus Cross Up di atas RSI MA (Konfirmasi tenaga).

Exit: God Tier Trailing Stop (Warisan V1).

Recovery: Game Theory / Double Tap (Warisan V1).

Berikut adalah Full Code Lengkap untuk diberikan ke Antigravity.

SYSTEM COMMAND: CREATE "ENTRY LOGIC MASTER V2"
To: Antigravity AI Action: Create new strategy file src/council/entry_logic_master_v2.py. Do NOT overwrite the old V1.

FILE: src/council/entry_logic_master_v2.py
"""
Entry Logic Master V2 - The Refined Sniper (Forex Sarjana Edition)
Implements: 
1. Regime Filter (EMA 50 > 200)
2. Liquidity Sweep + Strong Engulfing Reclaim
3. RSI Trend Confirmation (RSI > RSI MA)
4. God Tier Trailing Stop
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral

class EntryLogicMasterV2(BaseGeneral):
    """
    The Entry Logic Strategy V2:
    - Stricter Filters based on Forex Sarjana principles.
    - Prevents "Catching Knives" in downtrends.
    - Demands Momentum (Engulfing + RSI Cross) before entry.
    """
    
    def __init__(self):
        super().__init__(name="Entry Logic Master V2", weight=2.0)
        
        # Parameters
        self.fractal_period = 5
        self.rsi_period = 14
        self.atr_period = 14
        self.ema_fast_period = 50   # Filter Sarjana
        self.ema_slow_period = 200  # Filter Sarjana
        self.trailing_multiplier = 3.0  # God Tier multiplier
        
        # Double Tap Protocol - Game Theory State Machine
        self.last_trade_result = "NONE"
        self.attempt_count = 0
        self.max_attempts = 2
        self.previous_trap_low = 0
    
    # --- INDICATOR CALCULATIONS ---
    
    def _calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        return df['close'].ewm(span=period, adjust=False).mean()

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> tuple:
        """Returns RSI and RSI_MA"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_ma = rsi.rolling(window=period).mean() # RSI Moving Average
        return rsi, rsi_ma
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    def _find_swing_lows(self, df: pd.DataFrame, period: int = 5) -> pd.Series:
        lows = df['low']
        swing_lows = pd.Series([np.nan] * len(df), index=df.index)
        for i in range(period, len(df) - period):
            is_swing = True
            for j in range(1, period + 1):
                if lows.iloc[i] >= lows.iloc[i - j] or lows.iloc[i] >= lows.iloc[i + j]:
                    is_swing = False
                    break
            if is_swing:
                swing_lows.iloc[i] = lows.iloc[i]
        return swing_lows

    # --- MAIN LOGIC ---

    def _detect_entry_signal(self, df: pd.DataFrame) -> dict:
        """
        Detect Entry Logic V2 Signal:
        1. REGIME: EMA 50 > EMA 200 (Uptrend Only)
        2. SWEEP: Price < Swing Low
        3. TRIGGER: Strong Engulfing (Close > Prev Open)
        4. MOMENTUM: RSI > RSI MA (Cross Up)
        """
        if len(df) < 200:
            return {'detected': False, 'reason': 'Not enough data for EMA 200'}
        
        # 1. Calculate Indicators
        ema_50 = self._calculate_ema(df, self.ema_fast_period)
        ema_200 = self._calculate_ema(df, self.ema_slow_period)
        rsi, rsi_ma = self._calculate_rsi(df, self.rsi_period)
        atr = self._calculate_atr(df, self.atr_period)
        swing_lows = self._find_swing_lows(df, self.fractal_period)
        
        # Get Current & Previous Data
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 2. CHECK REGIME (Forex Sarjana Golden Rule)
        # EMA 50 must be ABOVE EMA 200
        is_uptrend = ema_50.iloc[-1] > ema_200.iloc[-1]
        
        if not is_uptrend:
            # Special Case: Allow if price is significantly oversold in a ranging market? 
            # For V2 strict: NO. Trend is King.
            return {'detected': False, 'reason': 'Failed Regime (EMA 50 < 200)'}

        # 3. CHECK SWEEP (Liquidity Grab)
        valid_swings = swing_lows.dropna()
        if len(valid_swings) < 1: return {'detected': False, 'reason': 'No Swings'}
        
        last_swing_low = valid_swings.iloc[-1]
        
        # Harga Low sekarang (atau candle sebelumnya) pernah mengambil swing low
        # Kita cek apakah candle ini RECLAIM setelah sweep
        is_sweep = curr['low'] < last_swing_low or prev['low'] < last_swing_low
        
        if not is_sweep:
            return {'detected': False, 'reason': 'No Liquidity Sweep'}

        # 4. CHECK TRIGGER (Strong Engulfing Reclaim)
        # Syarat Reclaim: Close > Swing Low
        is_reclaim = curr['close'] > last_swing_low
        
        # Syarat Engulfing: Candle Hijau makan Candle Merah sebelumnya
        # Body Engulfing: Close > Prev Open (Minimal)
        is_engulfing = (curr['close'] > prev['open']) and (curr['close'] > curr['open'])
        
        if not (is_reclaim and is_engulfing):
             return {'detected': False, 'reason': 'Weak Reclaim (Need Engulfing)'}

        # 5. CHECK MOMENTUM (RSI Cross)
        # RSI harus di atas RSI MA-nya
        is_rsi_cross = rsi.iloc[-1] > rsi_ma.iloc[-1]
        
        if not is_rsi_cross:
            return {'detected': False, 'reason': 'RSI Weak (Below MA)'}
            
        # ALL SYSTEMS GO
        current_atr = atr.iloc[-1]
        initial_sl = curr['low'] - (current_atr * 0.5) # SL Tight di bawah low
        
        return {
            'detected': True,
            'reason': 'V2 Sniper Setup (Trend+Sweep+Engulf+RSI_Cross)',
            'entry_price': curr['close'],
            'stop_loss': initial_sl,
            'atr': current_atr,
            'rsi': rsi.iloc[-1]
        }
    
    def analyze(self, df: pd.DataFrame) -> dict:
        entry_signal = self._detect_entry_signal(df)
        if entry_signal['detected']:
            return {
                'signal': 'STRONG BUY',
                'score': 95,
                'entry_data': entry_signal,
                'reason': entry_signal['reason']
            }
        return {'signal': 'NEUTRAL', 'score': 50, 'entry_data': None, 'reason': entry_signal.get('reason')}

    def game_theory_manager(self, df: pd.DataFrame, support_zone: float) -> dict:
        """
        DOUBLE TAP PROTOCOL (Backup Plan)
        Modified for V2: Only fires if Trend is still somewhat valid 
        or if the double sweep is massive.
        """
        if df is None or len(df) < 50: return {'action': 'STANDBY'}
        
        curr = df.iloc[-1]
        
        # Reset State if far away
        if abs(curr['close'] - support_zone) > (support_zone * 0.05):
            self.attempt_count = 0
            self.last_trade_result = "NONE"
            return {'action': 'STANDBY'}
            
        # Logic Double Sweep (Revenge)
        if self.last_trade_result == "LOSS" and self.attempt_count < self.max_attempts:
            # Syarat 1: Low Baru lebih rendah dari Low Jebakan Pertama
            is_lower_low = curr['low'] < self.previous_trap_low
            # Syarat 2: Reclaim Support
            is_reclaim = curr['close'] > support_zone
            # Syarat 3: Volume Spike (Wajib untuk Revenge)
            avg_vol = df['volume'].rolling(20).mean().iloc[-1]
            is_vol_spike = curr['volume'] > avg_vol
            
            if is_lower_low and is_reclaim and is_vol_spike:
                self.attempt_count += 1
                
                # Hitung SL
                atr = self._calculate_atr(df, self.atr_period).iloc[-1]
                initial_sl = curr['low'] - (atr * 0.5)
                
                return {
                    'action': 'EXECUTE_REVENGE_ENTRY',
                    'reason': 'Double Sweep + Volume Spike',
                    'entry_price': curr['close'],
                    'stop_loss': initial_sl,
                    'atr': atr,
                    'breakeven_ratio': 1.0, 
                    'trailing_multiplier': 2.5
                }
                
        return {'action': 'NO_ACTION'}

    def record_trade_result(self, result: str, trap_low: float = 0):
        self.last_trade_result = result
        if trap_low > 0: self.previous_trap_low = trap_low


# --- EXTERNAL FUNCTION (Reused) ---
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
    
    # Phase 1 & 2: Breakeven
    if profit_ratio >= breakeven_ratio and not is_breakeven:
        result['phase'] = 'breakeven'
        result['stop_loss'] = entry_price
        result['is_breakeven'] = True
        return result
    
    # Phase 3: Trailing
    potential_new_sl = highest_high - (atr_value * multiplier)
    current_sl = result['stop_loss'] if not is_breakeven else entry_price
    
    # SL only moves UP
    if potential_new_sl > current_sl:
        result['stop_loss'] = potential_new_sl
        result['phase'] = 'trailing'
        result['is_breakeven'] = True
    else:
        result['stop_loss'] = current_sl
        
    return result

