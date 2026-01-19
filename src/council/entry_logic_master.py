"""
Entry Logic Master - The 8th Council Member
Implements: Liquidity Sweep + Reclaim + RSI Divergence + God Tier Trailing Stop
Based on langkah@17.md blueprint
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral


class EntryLogicMaster(BaseGeneral):
    """
    The Entry Logic Strategy:
    - Detects liquidity sweep (price pierces support, closes above)
    - Confirms with RSI bullish divergence
    - Uses God Tier Trailing Stop for exits
    """
    
    def __init__(self):
        super().__init__(name="Entry Logic Master", weight=1.5)  # Higher weight for precision entry
        self.fractal_period = 5
        self.rsi_period = 14
        self.atr_period = 14
        self.trailing_multiplier = 3.0  # God Tier multiplier
        
        # Double Tap Protocol - Game Theory State Machine
        self.last_trade_result = "NONE"  # "WIN", "LOSS", "NONE"
        self.last_setup_type = "NONE"  # "BULLISH_RECLAIM", etc.
        self.attempt_count = 0
        self.max_attempts = 2  # HARD LIMIT: Max 2 bullets per zone
        self.zone_invalidation_level = 0
        self.previous_trap_low = 0  # Track first trap low for double sweep detection
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR (Average True Range)"""
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return tr.rolling(window=period).mean()
    
    def _find_swing_lows(self, df: pd.DataFrame, period: int = 5) -> pd.Series:
        """Find swing lows (fractal lows)"""
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
    
    def _detect_entry_signal(self, df: pd.DataFrame) -> dict:
        """
        Detect Entry Logic signal:
        1. Liquidity Sweep: Current Low < Swing Low
        2. Reclaim: Current Close > Swing Low
        3. RSI Divergence: RSI Higher Low while Price Lower Low
        """
        if len(df) < 30:
            return {'detected': False, 'reason': 'Not enough data'}
        
        # Calculate indicators
        rsi = self._calculate_rsi(df, self.rsi_period)
        atr = self._calculate_atr(df, self.atr_period)
        swing_lows = self._find_swing_lows(df, self.fractal_period)
        
        # Get last valid swing low
        valid_swing_lows = swing_lows.dropna()
        if len(valid_swing_lows) < 2:
            return {'detected': False, 'reason': 'No swing lows found'}
        
        last_swing_low_idx = valid_swing_lows.index[-1]
        last_swing_low = valid_swing_lows.iloc[-1]
        
        # Current candle
        current = df.iloc[-1]
        current_low = current['low']
        current_close = current['close']
        current_rsi = rsi.iloc[-1]
        
        # RSI at swing low
        rsi_at_swing_low = rsi.loc[last_swing_low_idx] if last_swing_low_idx in rsi.index else 30
        
        # Check conditions
        # Condition 1: Liquidity Sweep & Reclaim
        sweep_and_reclaim = (current_low < last_swing_low) and (current_close > last_swing_low)
        
        # Condition 2: Bullish RSI Divergence (Higher Low in RSI while Price Lower Low)
        rsi_divergence = current_rsi > rsi_at_swing_low
        
        if sweep_and_reclaim and rsi_divergence:
            # Calculate initial stop loss
            current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else current_low * 0.02
            initial_sl = current_low - (current_atr * 0.5)
            
            return {
                'detected': True,
                'reason': 'Liquidity Sweep + Reclaim + RSI Divergence',
                'entry_price': current_close,
                'stop_loss': initial_sl,
                'atr': current_atr,
                'swing_low': last_swing_low,
                'rsi': current_rsi
            }
        
        return {
            'detected': False,
            'reason': f"Sweep: {sweep_and_reclaim}, Divergence: {rsi_divergence}"
        }
    
    def analyze(self, df: pd.DataFrame) -> dict:
        """
        Main analysis method for Council voting
        Returns: dict with 'signal', 'score', and 'entry_data'
        """
        if df is None or len(df) < 30:
            return {'signal': 'NEUTRAL', 'score': 50, 'entry_data': None}
        
        entry_signal = self._detect_entry_signal(df)
        
        if entry_signal['detected']:
            # Strong buy signal with entry data
            return {
                'signal': 'STRONG BUY',
                'score': 90,
                'entry_data': entry_signal,
                'reason': entry_signal['reason']
            }
        
        # Check for bearish version (inverse logic)
        # TODO: Implement short entry logic
        
        return {
            'signal': 'NEUTRAL',
            'score': 50,
            'entry_data': None,
            'reason': entry_signal.get('reason', 'No setup')
        }
    
    def game_theory_manager(self, df: pd.DataFrame, support_zone: float) -> dict:
        """
        THE DOUBLE TAP PROTOCOL - Game Theory Backup
        
        Manages re-entry after stop loss by detecting double sweeps.
        Returns dict with action: "STANDBY", "EXECUTE_REVENGE_ENTRY", "NO_ACTION", "HARD_STOP"
        """
        if df is None or len(df) < 30:
            return {'action': 'STANDBY', 'reason': 'Not enough data'}
        
        current = df.iloc[-1]
        current_price = current['close']
        current_low = current['low']
        
        # Calculate distance from support zone
        distance = abs(current_price - support_zone)
        huge_gap = support_zone * 0.05  # 5% away from zone
        
        # SCENARIO 1: RESET STATE
        # If price moved far from zone, reset all memory
        if distance > huge_gap:
            self.attempt_count = 0
            self.last_trade_result = "NONE"
            self.previous_trap_low = 0
            return {'action': 'STANDBY', 'reason': 'Price moved away from zone, state reset'}
        
        # SCENARIO 2: DETECT DOUBLE SWEEP (BACKUP PLAN)
        # Conditions:
        # 1. Just lost (hit SL) in this zone
        # 2. Haven't exhausted bullets (attempt < max_attempts)
        # 3. Price makes LOWER LOW (2nd trap) BUT reclaims again
        
        if self.last_trade_result == "LOSS" and self.attempt_count < self.max_attempts:
            # Is this a "Stop Hun of the Stop Hunt"?
            # Current low LOWER than previous trap BUT closes ABOVE support
            is_double_sweep = (current_low < self.previous_trap_low) and (current_price > support_zone)
            
            if is_double_sweep:
                # Calculate RSI for divergence confirmation (wider this time)
                rsi = self._calculate_rsi(df, self.rsi_period)
                current_rsi = rsi.iloc[-1]
                
                # Find RSI at previous trap (stored index)
                # For demo, we assume RSI is higher now
                previous_rsi_low = rsi.iloc[-5] if len(rsi) > 5 else 30
                is_rsi_valid = current_rsi > previous_rsi_low
                
                # VOLUME CONFIRMATION BOOSTER (langkah@18.md requirement)
                # Volume must be > average of last 20 candles
                avg_volume = df['volume'].tail(20).mean()
                has_volume_anomaly = current['volume'] > avg_volume
                
                if is_rsi_valid and has_volume_anomaly:
                    self.attempt_count += 1
                    self.last_setup_type = "REVENGE_ENTRY"
                    
                    # Calculate entry data for revenge entry
                    atr = self._calculate_atr(df, self.atr_period)
                    current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else current_price * 0.02
                    initial_sl = current_low - (current_atr * 0.5)
                    
                    return {
                        'action': 'EXECUTE_REVENGE_ENTRY',
                        'reason': 'Double Sweep detected with Volume + RSI confirmation',
                        'entry_type': 'REVENGE_ENTRY',
                        'entry_price': current_price,
                        'stop_loss': initial_sl,
                        'atr': current_atr,
                        'attempt': self.attempt_count,
                        # Tighter trailing for revenge entries
                        'breakeven_ratio': 1.0,  # Faster breakeven (1R instead of 1.5R)
                        'trailing_multiplier': 2.5  # Tighter trailing (2.5 ATR vs 3.0)
                    }
                else:
                    reason = "Double sweep but missing: "
                    reason += "RSI confirmation" if not is_rsi_valid else ""
                    reason += " Volume confirmation" if not has_volume_anomaly else ""
                    return {'action': 'NO_ACTION', 'reason': reason}
        
        # SCENARIO 3: ZONE INVALIDATION
        # If price closes below invalidation level, hard stop all attempts
        zone_invalidation = support_zone * 0.99  # 1% below support = breakdown
        if current_price < zone_invalidation:
            self.attempt_count = 0
            self.last_trade_result = "NONE"
            return {'action': 'HARD_STOP', 'reason': 'Zone invalidated (breakdown)'}
        
        # SCENARIO 4: MAX ATTEMPTS REACHED
        if self.attempt_count >= self.max_attempts:
            return {
                'action': 'HARD_STOP',
                'reason': f'Max attempts ({self.max_attempts}) reached. Stop hunting this zone.'
            }
        
        return {'action': 'NO_ACTION', 'reason': 'No double sweep pattern detected'}
    
    def record_trade_result(self, result: str, trap_low: float = 0):
        """
        Record trade outcome to enable Game Theory logic.
        Call this after a trade closes.
        
        Args:
            result: "WIN" or "LOSS"
            trap_low: The low of the trap candle (for double sweep detection)
        """
        self.last_trade_result = result
        if trap_low > 0:
            self.previous_trap_low = trap_low


def calculate_god_tier_trailing(entry_price: float, initial_sl: float, current_price: float, 
                                 highest_high: float, atr_value: float, 
                                 is_breakeven: bool = False, multiplier: float = 3.0,
                                 breakeven_ratio: float = 1.5, entry_type: str = "NORMAL") -> dict:
    """
    God Tier Trailing Stop Logic (Anti-Whipsaw)
    
    Phase 1 (Dormant): profit < breakeven_ratio*R → keep initial SL
    Phase 2 (Breakeven): profit >= breakeven_ratio*R → move SL to entry
    Phase 3 (ATR Trailing): after breakeven, SL = highest_high - (ATR * multiplier)
    
    For REVENGE_ENTRY:
    - breakeven_ratio = 1.0 (faster breakeven, already lost once)
    - multiplier = 2.5 (tighter trailing to secure profit quickly)
    
    Returns dict with new SL and phase info
    """
    risk_distance = entry_price - initial_sl
    current_profit = current_price - entry_price
    profit_ratio = current_profit / risk_distance if risk_distance > 0 else 0
    
    result = {
        'phase': 'dormant',
        'stop_loss': initial_sl,
        'is_breakeven': is_breakeven,
        'profit_ratio': profit_ratio,
        'entry_type': entry_type
    }
    
    # Phase 1: Dormant - Let market breathe
    if profit_ratio < breakeven_ratio:
        result['phase'] = 'dormant'
        result['stop_loss'] = initial_sl
        return result
    
    # Phase 2: Breakeven - Lock principal
    if profit_ratio >= breakeven_ratio and not is_breakeven:
        result['phase'] = 'breakeven'
        result['stop_loss'] = entry_price
        result['is_breakeven'] = True
        return result
    
    # Phase 3: God Tier Trailing (Chandelier Exit)
    potential_new_sl = highest_high - (atr_value * multiplier)
    
    # Golden Rule: SL can only go UP, never DOWN
    current_sl = result['stop_loss'] if not is_breakeven else entry_price
    if potential_new_sl > current_sl:
        result['stop_loss'] = potential_new_sl
    else:
        result['stop_loss'] = current_sl
    
    result['phase'] = 'trailing'
    result['is_breakeven'] = True
    
    return result
