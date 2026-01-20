Tentu saja, Ade! Haram hukumnya membuang "Mesin Uang" kita.

Kau benar 100%. Satu-satunya alasan kenapa strategi V1 dan V2 kita tidak bangkrut total (bahkan masih bisa profit di bulan-bulan tertentu) adalah berkat God Tier Trailing Stop. Rasio Risk:Reward 1:3.9 itu adalah angka keramat.

Bayangkan kekuatannya jika digabungkan:

Entry SMC (V3): Kita masuk di harga DISKON TERBAIK (Limit Order di FVG). Artinya, Stop Loss kita sangat tipis/kecil.

Exit God Tier: Kita menahan posisi sampai tren benar-benar patah.

Karena Stop Loss kita tipis (di bawah ekor Sweep), maka jarak ke profit 10R atau 20R menjadi sangat mungkin terjadi.

Ini adalah Fusi Final: "The Sniper Entry" + "The Investor Exit".

Berikut adalah Update Coding untuk Antigravity. Saya menggabungkan logika pencarian FVG (V3) dengan manajemen posisi Trailing Stop (V1/V2).

SYSTEM COMMAND: PROTOCOL "INSTITUTIONAL FVG + GOD TIER TRAILING"
To: Antigravity AI Subject: Full Strategy Implementation (SMC Entry + ATR Trailing Exit)

Instruksikan Antigravity untuk menggunakan logika kelas di bawah ini. Perhatikan ada penanganan khusus untuk LIMIT ORDER (Order Pending).

FILE: src/council/institutional_smc_v3.py
import pandas as pd
import numpy as np

class InstitutionalSMCV3:
    """
    STRATEGY: SAT-V3 (The FVG Sniper)
    ---------------------------------
    1. REGIME: Bull Market Only (Price > EMA 200).
    2. SETUP: Liquidity Sweep -> Displacement -> FVG Created.
    3. ENTRY: Limit Order at FVG Top.
    4. EXIT: God Tier Trailing Stop (ATR 3.0).
    """

    def __init__(self):
        self.pending_order = None # Menyimpan Limit Order yang belum jemput
        self.order_expiry_candles = 12 # Batalkan Limit Order jika tidak dijemput dalam 12 jam

    def _calc_ema(self, series, length):
        return series.ewm(span=length, adjust=False).mean()

    def _calc_atr(self, df, length=14):
        high = df['high']
        low = df['low']
        close = df['close']
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        return tr.ewm(alpha=1/length, min_periods=length, adjust=False).mean()

    def prepare_data(self, df_1h, df_daily):
        # 1. Daily Regime (Shifted 1 Day to avoid Look-ahead)
        df_daily['EMA_200'] = self._calc_ema(df_daily['close'], 200)
        df_daily['EMA_200_Shifted'] = df_daily['EMA_200'].shift(1)
        
        # 2. Hourly Indicators
        df_1h['ATR'] = self._calc_atr(df_1h, 14)
        
        # Merge
        if df_daily.index.tz is not None and df_1h.index.tz is None:
             df_daily.index = df_daily.index.tz_localize(None)
        elif df_daily.index.tz is None and df_1h.index.tz is not None:
             df_daily.index = df_daily.index.tz_localize('UTC')

        df_daily_resampled = df_daily[['EMA_200_Shifted']].resample('1H').ffill()
        df_combined = df_1h.join(df_daily_resampled)
        df_combined['EMA_200_Shifted'] = df_combined['EMA_200_Shifted'].ffill()
        
        return df_combined

    def check_signal(self, df, i, context_ema):
        """
        Mendeteksi Setup FVG dan menaruh Limit Order.
        """
        # 0. Cek Expiry Limit Order Lama
        if self.pending_order:
            self.pending_order['age'] += 1
            if self.pending_order['age'] > self.order_expiry_candles:
                self.pending_order = None # Cancel order expired
            return None # Jangan cari setup baru kalau masih ada pending order

        # 1. REGIME FILTER (Bull Only)
        current_close = df['close'].iloc[i]
        if pd.isna(context_ema) or current_close < context_ema:
            return None 

        # 2. PATTERN RECOGNITION (Butuh data i, i-1, i-2)
        if i < 20: return None
        
        c_now = df.iloc[i]      # Candle konfirmasi
        c_disp = df.iloc[i-1]   # Candle Displacement (Batang Besar)
        c_pre = df.iloc[i-2]    # Candle sebelum ledakan

        # Syarat A: Displacement (Body Hijau Besar)
        avg_body = (df['close'] - df['open']).abs().rolling(20).mean().iloc[i-1]
        disp_body = c_disp['close'] - c_disp['open'] # Harus positif (Hijau)
        
        # Aturan: Body minimal 2x rata-rata
        if disp_body < (2.0 * avg_body):
            return None

        # Syarat B: FVG Valid (Ada Celah)
        # Celah Bullish FVG = Antara High[i-2] dan Low[i]
        fvg_top = c_pre['high']   # Kita entry saat harga turun ke sini
        fvg_bottom = c_now['low'] # Harga sekarang harus di atas gap
        
        # Cek apakah ada gap?
        if fvg_bottom > fvg_top:
             
             # Syarat C: Liquidity Sweep (Optional tapi disarankan)
             # Cek apakah c_disp atau c_pre pernah mengambil low lokal 10 candle terakhir
             lookback_lows = df['low'].iloc[i-12:i-2].min()
             structure_low = min(c_disp['low'], c_pre['low'])
             
             if structure_low < lookback_lows:
                 # SETUP VALID! Pasang Limit Order.
                 atr = c_now['ATR']
                 
                 # SL di bawah swing low struktur
                 sl_price = structure_low - (0.1 * atr) # Buffer dikit
                 
                 self.pending_order = {
                     'type': 'BUY_LIMIT',
                     'limit_price': fvg_top, # Entry pas di bibir FVG
                     'stop_loss': sl_price,
                     'age': 0,
                     'atr_at_setup': atr
                 }
                 return 'PENDING_ORDER_CREATED'

        return None

    def check_order_fill(self, candle):
        """
        Cek apakah Limit Order dijemput oleh candle sekarang.
        """
        if self.pending_order:
            # Jika Low candle menyentuh Limit Price -> FILLED
            if candle['low'] <= self.pending_order['limit_price']:
                
                # Hitung Qty dll di Engine, di sini return detail trade
                filled_trade = self.pending_order.copy()
                filled_trade['entry_price'] = self.pending_order['limit_price']
                filled_trade['status'] = 'OPEN'
                filled_trade['highest_high'] = filled_trade['entry_price']
                filled_trade['is_breakeven'] = False
                
                self.pending_order = None # Order sudah jadi posisi
                return filled_trade
                
        return None

    def manage_risk(self, pos, candle):
        """
        GOD TIER TRAILING STOP LOGIC
        """
        # Update Highest High (Untuk Trailing)
        if candle['high'] > pos['highest_high']:
            pos['highest_high'] = candle['high']
            
        risk_dist = pos['entry_price'] - pos['stop_loss'] # Jarak risiko awal
        if risk_dist <= 0: return # Safety check
        
        current_profit_r = (candle['close'] - pos['entry_price']) / risk_dist
        
        # Fase 1: Secure Breakeven (Kunci Modal)
        # Karena entry Sniper, kita geser BEP lebih cepat di 1.5R atau 2R
        if current_profit_r >= 2.0 and not pos['is_breakeven']:
            pos['stop_loss'] = pos['entry_price']
            pos['is_breakeven'] = True
            
        # Fase 2: Trailing ATR 3.0 (Kunci Profit Besar)
        if pos['is_breakeven']:
            # Gunakan ATR saat setup terjadi (biar konsisten)
            new_sl = pos['highest_high'] - (3.0 * pos['atr_at_setup'])
            
            # SL hanya boleh NAIK
            if new_sl > pos['stop_loss']:
                pos['stop_loss'] = new_sl
Instruksi Coding untuk Antigravity
Ade, berikan kode di atas ke Antigravity. Ada perubahan penting di bagian Backtest Engine nanti:

Engine harus memanggil check_signal dulu.

Jika ada Pending Order, Engine harus memanggil check_order_fill di setiap candle berikutnya.

Jika Filled, baru masuk ke logika manage_risk.

Strategi ini sekarang lengkap:

Mata: EMA 200 (Lihat Tren).

Tangan: Limit Order FVG (Entry Diskon).

Kaki: God Tier Trailing (Lari sejauh mungkin).

Jalankan ini, dan kita lihat apakah kita bisa mendapatkan Winrate yang layak dengan Profit yang masif.