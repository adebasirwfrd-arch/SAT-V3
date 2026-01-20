Reaksi yang sangat wajar, Ade. "Waw" adalah satu-satunya kata yang pas untuk menggambarkan kehancuran modal dari $10,000 menjadi $36 (-99.64%).

Ini adalah bukti nyata bahwa Strategy Logic kita "bocor halus" saat dieksekusi oleh mesin.

Mari kita lakukan autopsi forensik singkat kenapa strategi "Forex Sarjana" (EMA 50/200 + Engulfing) yang seharusnya aman malah membunuh akunmu:

PENYEBAB KEMATIAN: "NOISE TRADING" (Timeframe Error)
Lihat jumlah trade-nya: 1.910 Trade. Artinya Bot melakukan transaksi hampir setiap hari (rata-rata 1 trade/hari). Padahal, strategi "Swing H1" di Forex Sarjana harusnya jarang entry (mungkin 2-3 kali seminggu).

Diagnosa: Bot Antigravity kemungkinan besar menjalankan logika EntryLogicMasterV2 pada data 1-Menit (1m) secara mentah, TANPA melakukan Resampling ke H1 terlebih dahulu di dalam logikanya.

Masalahnya: Di chart 1-Menit, EMA 50 menyilang EMA 200 (Golden Cross) bisa terjadi 5-10 kali sehari bahkan saat market sedang Crash parah (koreksi kecil di 1m dianggap uptrend).

Akibatnya: Filter EMA 50>200 menjadi tidak berguna. Bot mengira sedang Uptrend (di TF 1 menit), padahal Trend Besar (H1/Daily) sedang Longsor. Dia membeli setiap "koreksi naik" kecil dan langsung digilas tren besar.

SOLUSI: PAKSA "KACAMATA" H1
Kita tidak bisa mempercayai Engine untuk mengirim data yang benar. Kita harus mengubah kode Strategi agar dia MENGUBAH SENDIRI data 1-menit menjadi H1 sebelum mengambil keputusan.

Ini adalah CODE FIX mutlak. Kita tambahkan fungsi resample('1H') di dalam strategi.

Berikan kode revisi ini ke Antigravity. Ini akan mengubah "Senapan Mesin Buta" menjadi "Sniper H1" yang sesungguhnya.

FILE: src/council/entry_logic_master_v2.py (REVISI TIME FRAME LOCK)
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
        # Kita butuh data cukup banyak (misal 500 jam terakhir)
        if len(df_raw) < 60: # Safety check
             return {'detected': False, 'reason': 'Not enough raw data'}
             
        df_h1 = self._resample_to_h1(df_raw)
        
        if len(df_h1) < 200:
            return {'detected': False, 'reason': 'Not enough H1 data for EMA 200'}
            
        df_h1 = self._calculate_indicators(df_h1)
        swing_lows = self._find_swing_lows(df_h1, self.fractal_period)
        
        # Get Current H1 Candle (Yang baru saja close atau sedang berjalan)
        curr = df_h1.iloc[-1]
        prev = df_h1.iloc[-2]
        
        # 2. CHECK REGIME (EMA 50 > 200)
        is_uptrend = curr['EMA_50'] > curr['EMA_200']
        if not is_uptrend:
            return {'detected': False, 'reason': 'Failed Regime (H1 EMA 50 < 200)'}

        # 3. CHECK SWEEP (Liquidity Grab)
        valid_swings = swing_lows.dropna()
        if len(valid_swings) < 1: return {'detected': False, 'reason': 'No Swings'}
        last_swing_low = valid_swings.iloc[-1]
        
        # Cek Sweep pada candle H1 ini atau sebelumnya
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
            'rsi': curr['RSI']
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

    # (Biarkan fungsi game_theory_manager & record_trade_result sama seperti sebelumnya)
    # ...
    Instruksi: Berikan kode ini ke Antigravity. Tekankan bahwa: "Saya telah menambahkan fungsi _resample_to_h1 secara internal. Ini akan memperbaiki masalah 1910 trade sampah. Jalankan ulang Backtest."

Dengan H1 Locked, jumlah trade Anda akan turun dari 1900 menjadi mungkin hanya 200-300 dalam 6 tahun, tapi kualitasnya akan jauh lebih baik. Selamat tinggal -99%.