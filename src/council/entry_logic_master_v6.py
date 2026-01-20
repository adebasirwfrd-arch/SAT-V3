"""
Entry Logic Master V6 - The Institutional Flip (RBS + Imbalance)
----------------------------------------------------------------
Filosofi:
1. Waiting: Identifikasi Resistance Pivot High (Static Peak).
2. Displacement: Harga Breakout dengan Body Candle > 1.1x Rata-rata.
3. Mitigation: Harga kembali ke Flip Zone (Retest) & Memantul.
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral

class EntryLogicMasterV6(BaseGeneral):
    
    def __init__(self):
        super().__init__(name="Entry Logic V6 Institutional", weight=2.5)
        self.ema_trend = 200
        self.atr_period = 14
        self.flip_zone = None
        self.waiting_retest = False

    def _resample_to_h1(self, df: pd.DataFrame) -> pd.DataFrame:
        if len(df) > 1:
            diff = (df.index[1] - df.index[0]).total_seconds()
            if diff >= 3600: return df
        return df.resample('1h').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['EMA_200'] = df['close'].ewm(span=self.ema_trend, adjust=False).mean()
        
        # ATR
        h, l, cp = df['high'], df['low'], df['close'].shift(1)
        tr = pd.concat([h-l, (h-cp).abs(), (l-cp).abs()], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=self.atr_period).mean()
        
        # PIVOT HIGH DETECTION (Static Resistance)
        # A pivot is a high preceded by 2 lower highs and followed by 2 lower highs
        df['Is_Pivot'] = (df['high'].shift(2) > df['high'].shift(4)) & \
                         (df['high'].shift(2) > df['high'].shift(3)) & \
                         (df['high'].shift(2) > df['high'].shift(1)) & \
                         (df['high'].shift(2) > df['high'])
        
        df['Pivot_Price'] = np.where(df['Is_Pivot'], df['high'].shift(2), np.nan)
        df['Resistance'] = df['Pivot_Price'].ffill()
        
        # Displacement
        df['Body_Size'] = (df['close'] - df['open']).abs()
        df['Avg_Body'] = df['Body_Size'].rolling(window=24).mean()
        
        return df

    def _detect_entry_signal(self, df_raw: pd.DataFrame) -> dict:
        df = self._resample_to_h1(df_raw)
        df = self._calculate_indicators(df)
        if len(df) < 50: return {'detected': False}

        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 1. REGIME: NO BUY BELOW EMA 200
        if curr['close'] < curr['EMA_200']:
            self.waiting_retest = False
            self.flip_zone = None
            return {'detected': False, 'reason': 'Bearish'}

        # 2. STEP 1: BREAKOUT (Displacement)
        res = curr['Resistance']
        if not pd.isna(res) and not self.waiting_retest:
            # We look for a breakout of a confirmed pivot high
            # Breakout can happen if current close > pivot resistance
            is_breakout = (curr['close'] > res) and (curr['close'] > curr['open'])
            is_strong = (curr['Body_Size'] > 1.1 * curr['Avg_Body'])
            
            # Ensure we were below it recently
            was_below = (df['high'].iloc[-10:-1] < res).any()
            
            if is_breakout and is_strong and was_below:
                self.flip_zone = res
                self.waiting_retest = True
                print(f"[{df.index[-1]}] 🔵 FLIP ZONE DETECTED: {self.flip_zone:.2f}")

        # 3. STEP 2: RETEST (Mitigation)
        if self.waiting_retest and self.flip_zone:
            # Cancel if fakeout
            if curr['close'] < (self.flip_zone - (1.0 * curr['ATR'])):
                self.waiting_retest = False
                self.flip_zone = None
                return {'detected': False, 'reason': 'Fakeout'}
            
            # Zone Hit & Bounce
            hit_zone = (curr['low'] <= self.flip_zone + (0.5 * curr['ATR']))
            if hit_zone:
                if curr['close'] > curr['open']:
                    sl_price = self.flip_zone - (1.2 * curr['ATR'])
                    res = {
                        'detected': True,
                        'reason': 'Institutional Flip (RBS)',
                        'entry_price': curr['close'],
                        'stop_loss': sl_price,
                        'atr': curr['ATR']
                    }
                    self.waiting_retest = False
                    self.flip_zone = None
                    return res

        return {'detected': False}

    def analyze(self, df: pd.DataFrame) -> dict:
        res = self._detect_entry_signal(df)
        if res['detected']:
            return {'signal': 'STRONG BUY', 'score': 95, 'entry_data': res, 'reason': res['reason']}
        return {'signal': 'NEUTRAL', 'score': 0, 'entry_data': None, 'reason': 'No Signal'}
    def game_theory_manager(self, df: pd.DataFrame, support_zone: float) -> dict: return {'action': 'NO_ACTION'}
    def record_trade_result(self, result: str, trap_low: float = 0): pass

def calculate_god_tier_trailing(entry_price: float, initial_sl: float, current_price: float, 
                                 highest_high: float, atr_value: float, 
                                 is_breakeven: bool = False, multiplier: float = 3.0,
                                 breakeven_ratio: float = 1.5, entry_type: str = "NORMAL") -> dict:
    risk_distance = entry_price - initial_sl
    if risk_distance <= 0: return {'stop_loss': initial_sl, 'phase': 'error'}
    current_profit = current_price - entry_price
    profit_ratio = current_profit / risk_distance
    result = {'phase': 'dormant', 'stop_loss': initial_sl, 'is_breakeven': is_breakeven}
    if profit_ratio >= breakeven_ratio and not is_breakeven:
        result.update({'phase': 'breakeven', 'stop_loss': entry_price, 'is_breakeven': True})
        return result
    potential_new_sl = highest_high - (atr_value * multiplier)
    current_sl = result['stop_loss'] if not is_breakeven else entry_price
    if potential_new_sl > current_sl:
        result.update({'stop_loss': potential_new_sl, 'phase': 'trailing', 'is_breakeven': True})
    else:
        result['stop_loss'] = current_sl
    return result
