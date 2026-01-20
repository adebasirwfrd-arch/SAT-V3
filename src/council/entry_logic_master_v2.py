"""
Entry Logic Master V2 - The Refined Sniper (H1 LOCKED)
------------------------------------------------------
FIX: Memaksa data resample ke H1 internal untuk menghindari "1-Minute Noise".
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral


class EntryLogicMasterV2(BaseGeneral):
    
    def __init__(self):
        super().__init__(name="Entry Logic Master V2", weight=2.0)
        
        # Parameters
        self.fractal_period = 5
        self.rsi_period = 14
        self.atr_period = 14
        self.ema_fast_period = 50 
        self.ema_slow_period = 200
        self.trailing_multiplier = 3.0
        
        # Game Theory State
        self.last_trade_result = "NONE"
        self.attempt_count = 0
        self.max_attempts = 2
        self.previous_trap_low = 0
    
    # --- INTERNAL RESAMPLING (THE FIX) ---
    def _resample_to_h1(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Memaksa data 1m menjadi H1 agar indikator valid.
        """
        # Pastikan index adalah datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.copy()
            df.index = pd.to_datetime(df.index)

        # Resample logic
        df_h1 = df.resample('1h').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        return df_h1

    # --- INDICATOR CALCULATIONS (ON H1) ---
    
    def _calculate_indicators(self, df_h1: pd.DataFrame) -> pd.DataFrame:
        df = df_h1.copy()
        
        # EMA (Forex Sarjana Filter)
        df['EMA_50'] = df['close'].ewm(span=self.ema_fast_period, adjust=False).mean()
        df['EMA_200'] = df['close'].ewm(span=self.ema_slow_period, adjust=False).mean()
        
        # RSI & RSI MA
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI_MA'] = df['RSI'].rolling(window=self.rsi_period).mean()
        
        # ATR
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        tr = pd.concat([high - low, (high - close).abs(), (low - close).abs()], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=self.atr_period).mean()
        
        return df

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

    def _detect_entry_signal(self, df_raw: pd.DataFrame) -> dict:
        """
        Mendeteksi Sinyal pada timeframe H1.
        """
        # 1. PAKSA RESAMPLE KE H1
        if len(df_raw) < 60:
            return {'detected': False, 'reason': 'Not enough raw data'}
             
        df_h1 = self._resample_to_h1(df_raw)
        
        if len(df_h1) < 200:
            return {'detected': False, 'reason': 'Not enough H1 data for EMA 200'}
            
        df_h1 = self._calculate_indicators(df_h1)
        swing_lows = self._find_swing_lows(df_h1, self.fractal_period)
        
        # Get Current H1 Candle
        curr = df_h1.iloc[-1]
        prev = df_h1.iloc[-2]
        
        # 2. CHECK REGIME (EMA 50 > 200)
        is_uptrend = curr['EMA_50'] > curr['EMA_200']
        if not is_uptrend:
            return {'detected': False, 'reason': 'Failed Regime (H1 EMA 50 < 200)'}

        # 3. CHECK SWEEP (Liquidity Grab)
        valid_swings = swing_lows.dropna()
        if len(valid_swings) < 1:
            return {'detected': False, 'reason': 'No Swings'}
        last_swing_low = valid_swings.iloc[-1]
        
        is_sweep = curr['low'] < last_swing_low or prev['low'] < last_swing_low
        if not is_sweep:
            return {'detected': False, 'reason': 'No Liquidity Sweep'}

        # 4. CHECK TRIGGER (Strong Engulfing H1)
        is_reclaim = curr['close'] > last_swing_low
        is_engulfing = (curr['close'] > prev['open']) and (curr['close'] > curr['open'])
        
        if not (is_reclaim and is_engulfing):
            return {'detected': False, 'reason': 'Weak Reclaim (Need H1 Engulfing)'}

        # 5. CHECK MOMENTUM (RSI Cross)
        is_rsi_cross = curr['RSI'] > curr['RSI_MA']
        if not is_rsi_cross:
            return {'detected': False, 'reason': 'RSI Weak'}
            
        # ENTRY VALID
        initial_sl = curr['low'] - (curr['ATR'] * 0.5)
        
        return {
            'detected': True,
            'reason': 'V2 H1 Sniper Setup',
            'entry_price': curr['close'],
            'stop_loss': initial_sl,
            'atr': curr['ATR'],
            'rsi': curr['RSI'],
            'swing_low': last_swing_low
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
        Modified for V2: Only fires if Trend is still somewhat valid.
        """
        if df is None or len(df) < 60:
            return {'action': 'STANDBY'}
        
        # Resample to H1 for consistency
        df_h1 = self._resample_to_h1(df)
        if len(df_h1) < 50:
            return {'action': 'STANDBY'}
            
        df_h1 = self._calculate_indicators(df_h1)
        curr = df_h1.iloc[-1]
        
        # Reset State if far away
        if abs(curr['close'] - support_zone) > (support_zone * 0.05):
            self.attempt_count = 0
            self.last_trade_result = "NONE"
            return {'action': 'STANDBY'}
            
        # Logic Double Sweep (Revenge)
        if self.last_trade_result == "LOSS" and self.attempt_count < self.max_attempts:
            is_lower_low = curr['low'] < self.previous_trap_low
            is_reclaim = curr['close'] > support_zone
            avg_vol = df_h1['volume'].rolling(20).mean().iloc[-1]
            is_vol_spike = curr['volume'] > avg_vol
            
            if is_lower_low and is_reclaim and is_vol_spike:
                self.attempt_count += 1
                
                initial_sl = curr['low'] - (curr['ATR'] * 0.5)
                
                return {
                    'action': 'EXECUTE_REVENGE_ENTRY',
                    'reason': 'H1 Double Sweep + Volume Spike',
                    'entry_price': curr['close'],
                    'stop_loss': initial_sl,
                    'atr': curr['ATR'],
                    'breakeven_ratio': 1.0, 
                    'trailing_multiplier': 2.5
                }
                
        return {'action': 'NO_ACTION'}

    def record_trade_result(self, result: str, trap_low: float = 0):
        self.last_trade_result = result
        if trap_low > 0:
            self.previous_trap_low = trap_low


# --- EXTERNAL FUNCTION (God Tier Trailing) ---
def calculate_god_tier_trailing(entry_price: float, initial_sl: float, current_price: float, 
                                 highest_high: float, atr_value: float, 
                                 is_breakeven: bool = False, multiplier: float = 3.0,
                                 breakeven_ratio: float = 1.5, entry_type: str = "NORMAL") -> dict:
    risk_distance = entry_price - initial_sl
    if risk_distance <= 0:
        return {'stop_loss': initial_sl, 'phase': 'error'}
    
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
