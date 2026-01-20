Inilah Strategy V6: "THE INSTITUTIONAL FLIP".

Strategi ini dirancang untuk HANYA masuk di Langkah 3 (Mitigation/Retest).

Bot Menunggu: Bot akan memantau Resistance.

Bot Melihat: Saat Resistance dijebol dengan Candle Raksasa (Displacement), Bot mencatat level itu sebagai "Flip Zone" (Calon Support).

Bot Menjebak: Bot menunggu dengan sabar sampai harga turun kembali ke Flip Zone itu.

Bot Menembak: Saat harga memantul (muncul candle hijau di zona itu), Bot masuk.

Berikan perintah dan kode ini kepada Antigravity.

SYSTEM COMMAND: IMPLEMENT STRATEGY V6
To: Antigravity AI Subject: Strategy Implementation - EntryLogicMasterV6 (Institutional Flip)

Instruksi: Buat file baru src/council/entry_logic_master_v6.py. Strategi ini fokus pada setup RBS (Resistance Become Support) dengan validasi Impulsive Breakout.

FILE: src/council/entry_logic_master_v6.py
"""
Entry Logic Master V6 - The Institutional Flip (RBS + Imbalance)
----------------------------------------------------------------
Filosofi:
1. Waiting (Menunggu): Identifikasi Resistance Swing High.
2. Displacement (Validasi): Harga Breakout dengan Body Candle > 1.5x Rata-rata.
3. Mitigation (Entry): Harga kembali ke level Breakout (Retest) & Memantul.
"""
import pandas as pd
import numpy as np
from .base_general import BaseGeneral

class EntryLogicMasterV6(BaseGeneral):
    
    def __init__(self):
        super().__init__(name="Entry Logic V6 Institutional", weight=2.5)
        
        # Parameter Struktur
        self.swing_period = 10     # Periode untuk menentukan Swing High valid
        self.retest_window = 48    # Batas waktu tunggu retest (48 jam)
        
        # Parameter Filter
        self.ema_trend = 200       # Institusi hanya Buy di atas EMA 200
        self.atr_period = 14
        
        # Memory State (Penyimpan Jejak Institusi)
        self.flip_zone = None      # Harga Resistance yang sudah dijebol
        self.break_candle_idx = 0  # Waktu kejadian breakout
        self.waiting_retest = False

    # --- 1. DATA PROCESSING (H1 LOCK) ---
    def _resample_to_h1(self, df: pd.DataFrame) -> pd.DataFrame:
        """Kunci Data ke H1 untuk menghilangkan Noise M1/M5"""
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.copy()
            df.index = pd.to_datetime(df.index)
            
        return df.resample('1h').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna()

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # EMA 200 untuk Trend Besar
        df['EMA_200'] = df['close'].ewm(span=self.ema_trend, adjust=False).mean()
        
        # ATR untuk Stop Loss Rasional
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        tr = pd.concat([high-low, (high-close).abs(), (low-close).abs()], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=self.atr_period).mean()
        
        # Swing High (Mencari Puncak Resistance)
        # Menggunakan window rolling untuk mencari local maxima
        df['Swing_High'] = df['high'].rolling(window=self.swing_period*2+1, center=True).max()
        
        # Rata-rata Body Candle (Untuk deteksi Displacement)
        df['Body_Size'] = (df['close'] - df['open']).abs()
        df['Avg_Body'] = df['Body_Size'].rolling(window=20).mean()
        
        return df

    # --- 2. MAIN LOGIC LOOP ---
    def _detect_entry_signal(self, df_raw: pd.DataFrame) -> dict:
        
        # A. Persiapan Data
        if len(df_raw) < 500: return {'detected': False} # Butuh data banyak untuk EMA 200
        df = self._resample_to_h1(df_raw)
        df = self._calculate_indicators(df)
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # B. RESET LOGIC (Jika Trend Berubah Bearish)
        # Institusi tidak melakukan Buy Setup di Bawah EMA 200
        if curr['close'] < curr['EMA_200']:
            self.waiting_retest = False
            self.flip_zone = None
            return {'detected': False, 'reason': 'Bearish Regime (Below EMA 200)'}

        # C. STEP 1: DETEKSI DISPLACEMENT (The Breakout)
        # Kita cari Swing High valid terakhir dari masa lalu (misal 5-50 candle ke belakang)
        # Kita ambil nilai unik Swing High terakhir yang valid
        last_resistance_series = df['Swing_High'].iloc[-50:-3].dropna()
        
        if not last_resistance_series.empty:
            potential_resistance = last_resistance_series.iloc[-1]
            
            # Cek Breakout: Candle SEKARANG (atau kemarin) menembus Resistance
            # Syarat Breakout Institusi:
            # 1. Close > Resistance
            # 2. Body Candle > 1.5x Rata-rata (Ledakan Volume/Displacement)
            
            is_breakout = (prev['close'] > potential_resistance) and \
                          (prev['close'] > prev['open']) and \
                          (prev['Body_Size'] > 1.5 * prev['Avg_Body'])
            
            # Pastikan sebelumnya kita ada di bawah resistance
            was_below = df['close'].iloc[-3] < potential_resistance
            
            if is_breakout and was_below and not self.waiting_retest:
                # KONFIRMASI: INSTITUSI SUDAH MENJEBOL DINDING
                self.flip_zone = potential_resistance # Resistance resmi jadi Support (Flip)
                self.waiting_retest = True
                self.break_candle_idx = len(df) # Timestamp internal
                # Kita TIDAK Buy di sini. Itu FOMO. Kita tunggu Retest.
                return {'detected': False, 'reason': f'Displacement Detected at {potential_resistance}. Waiting Retest...'}

        # D. STEP 2: MITIGATION / RETEST (The Entry)
        if self.waiting_retest and self.flip_zone:
            
            # Cek Batal: Jika harga malah jebol balik ke bawah Flip Zone (Fakeout)
            # Toleransi fakeout: 1 ATR
            if curr['close'] < (self.flip_zone - curr['ATR']):
                self.waiting_retest = False
                self.flip_zone = None
                return {'detected': False, 'reason': 'Setup Failed (Fakeout/Deep Crash)'}
            
            # Cek Retest: Harga Low menyentuh Zona Flip
            # Zona Flip = Harga Resistance +/- 0.2 ATR
            hit_zone = (curr['low'] <= self.flip_zone + (0.2 * curr['ATR']))
            
            if hit_zone:
                # STEP 3: TRIGGER (Pantulan)
                # Syarat: Candle H1 ditutup HIJAU (Bullish) setelah menyentuh zona
                is_bouncing = curr['close'] > curr['open']
                
                if is_bouncing:
                    # ENTRY CONFIRMED
                    # Stop Loss: Di bawah ekor candle retest (Swing Low lokal)
                    sl_price = curr['low'] - (0.5 * curr['ATR'])
                    
                    entry_signal = {
                        'detected': True,
                        'reason': 'Institutional Flip (RBS) Confirmed',
                        'entry_price': curr['close'],
                        'stop_loss': sl_price,
                        'atr': curr['ATR']
                    }
                    
                    # Reset setelah entry
                    self.waiting_retest = False
                    self.flip_zone = None
                    
                    return entry_signal

        return {'detected': False}

    def analyze(self, df: pd.DataFrame) -> dict:
        res = self._detect_entry_signal(df)
        if res['detected']:
            return {'signal': 'STRONG BUY', 'score': 95, 'entry_data': res}
        return {'signal': 'NEUTRAL', 'score': 0, 'entry_data': None}
        
    # Fungsi Trailing Stop God Tier tetap wajib ada di sini untuk Exit
    # (Copy paste fungsi calculate_god_tier_trailing dari file sebelumnya)

