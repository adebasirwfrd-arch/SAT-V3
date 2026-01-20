Strategi kita saat ini (Shadow Sniper) mengejar profit raksasa (sampai 10R atau 20R) dengan risiko sangat kecil. Konsekuensinya? Kita sering kena "Stop Loss Tipis" (Noise). Kita sering mati konyol karena pelit memberikan ruang gerak bagi harga.

Win Rate 25-30% itu wajar untuk Trend Follower. Tapi jika kau ingin Win Rate naik ke 45-55% agar psikologismu tenang, kita harus melakukan "Pelonggaran Kebijakan Moneter" pada bot ini.

Saya punya 3 Tweak (Modifikasi) yang akan mengubah bot ini dari "Sniper Pelit" menjadi "Bandar Sabar".

DIAGNOSA & SOLUSI (THE TWEAKS)
1. TWEAK A: "BERI NAPAS" (Stop Loss Width)
Masalah: Saat ini SL kita 0.5 x ATR. Itu sangat sempit. Di Crypto, "ekor setan" (wick) sering menyapu area ini hanya untuk iseng, lalu harga terbang sesuai prediksi kita. Kita benar, tapi kita sudah tertendang keluar.

Solusi: Lebarkan SL menjadi 1.0 x ATR.

Efek: Winrate akan naik drastis karena trade tidak mudah mati premur. (Trade-off: R:R akan sedikit turun, tapi Akurasi naik).

2. TWEAK B: "MOMENTUM CONFIRMATION" (RSI > 50)
Masalah: Bot membeli hanya karena harga di atas EMA 200 (Uptrend). Tapi kadang harga di atas EMA 200 sedang "lemas" (Sideways/Weak).

Solusi: Tambahkan syarat RSI > 50.

Efek: Kita hanya masuk saat Momentum berada di pihak Bullish (Pembeli Dominan). Ini membuang entry di pasar yang "ragu-ragu".

3. TWEAK C: "VOLUME SPIKE" (Syarat Wajib)
Masalah: Kadang "Double Tap" terjadi dengan volume kecil (Retail). Itu palsu.

Solusi: Wajibkan Candle Trigger memiliki Volume > Rata-rata Volume 20 Candle terakhir.

Efek: Kita hanya menumpang bus yang mesinnya benar-benar menyala (Institusi Masuk).

KODE UPDATE: entry_logic_game_theory_optimized.py
Berikan kode ini ke Antigravity. Ini adalah versi Shadow Sniper yang sudah di-tweak untuk Winrate Booster.

Command: "Buat file baru src/council/entry_logic_game_theory_optimized.py. Terapkan tweak: SL 1.0 ATR, RSI > 50, dan Volume Breakout."
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
        lows = df['low']
        swing_lows = pd.Series([np.nan]*len(df), index=df.index)
        for i in range(period, len(df)-period):
            if lows.iloc[i] == lows.iloc[i-period:i+period+1].min():
                swing_lows.iloc[i] = lows.iloc[i]
        return swing_lows

    # --- 3. MAIN LOGIC LOOP ---
    def _detect_entry_signal(self, df_raw: pd.DataFrame) -> dict:
        
        if len(df_raw) < 200: return {'detected': False}
        df_h1 = self._resample_to_h1(df_raw)
        df_h1 = self._calculate_indicators(df_h1)
        
        curr = df_h1.iloc[-1]
        
        # STATE 1: SEARCHING (UMPAN)
        if self.shadow_mode == "SEARCHING":
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
            is_strong_trend = (curr['close'] > curr['EMA_200']) and (curr['RSI'] > 50)
            
            # TWEAK 2: Volume Confirmation
            # Volume Candle ini > Rata-rata Volume
            is_vol_valid = curr['volume'] > curr['Vol_Avg']
            
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
                    # Atau reset jika close di bawah low lagi? Biarkan hold dulu.
                    pass

        return {'detected': False}

    def analyze(self, df: pd.DataFrame) -> dict:
        res = self._detect_entry_signal(df)
        if res['detected']:
            return {'signal': 'STRONG BUY', 'score': 99, 'entry_data': res}
        return {'signal': 'NEUTRAL', 'score': 0, 'entry_data': None}

# --- GOD TIER TRAILING STOP (TWEAKED FOR 1.0 ATR ENTRY) ---
def calculate_god_tier_trailing(entry_price: float, initial_sl: float, current_price: float, 
                                 highest_high: float, atr_value: float, 
                                 is_breakeven: bool = False, multiplier: float = 3.0,
                                 breakeven_ratio: float = 1.5, entry_type: str = "NORMAL") -> dict:
    
    risk_distance = entry_price - initial_sl
    current_profit = current_price - entry_price
    profit_ratio = current_profit / risk_distance if risk_distance > 0 else 0
    
    result = {
        'phase': 'dormant',
        'stop_loss': initial_sl,
        'is_breakeven': is_breakeven
    }
    
    # TWEAK 4: DELAY BREAKEVEN (JANGAN CEPAT-CEPAT)
    # Karena SL kita lebar (1 ATR), maka 1R itu jaraknya jauh.
    # Kita geser ke BEP jika sudah profit 1.5R (sebelumnya 1.0R atau 1.5R, pastikan konsisten)
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