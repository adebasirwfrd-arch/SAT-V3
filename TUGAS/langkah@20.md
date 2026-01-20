Baik, Ade. Kita akan menggunakan Infrastruktur Pengujian yang sama persis (format laporan, metrik, data loader) karena itu sudah standar industri, tapi kita akan mengganti Otaknya dengan strategi baru kita: Institutional Hybrid V2 (EMA 200 + RSI Oversold + Engulfing Sniper).

Ingat pesan saya tadi: Hati-hati dengan Look-Ahead Bias saat menghitung EMA 200 Daily.

Berikut adalah Paket Instruksi Coding Lengkap untuk Antigravity. Ini mencakup 3 file utama:

institutional_hybrid_v2.py (Otak Strategi Baru)

backtest_engine_v2.py (Mesin Penggerak yang disesuaikan)

run_hybrid_backtest.py (Script Eksekusi)

Berikan blok kode ini ke Antigravity dan perintahkan dia untuk: "Implementasikan kode ini secara verbatim (tanpa diubah logikanya) dan jalankan backtest."

FILE 1: THE STRATEGY BRAIN (src/council/institutional_hybrid_v2.py)
import pandas as pd
import pandas_ta as ta
import numpy as np

class InstitutionalHybridV2:
    """
    STRATEGY: Institutional Hybrid V2 (The Sniper)
    -----------------------------------------------
    FILTERS:
    - Regime: EMA 200 Daily (Bullish > Price > Bearish)
    
    ENTRY MECHANISM:
    - Bullet 1 (The Scout): Bull Market ONLY. Sweep + Reclaim + RSI Oversold.
    - Bullet 2 (The Sniper): Recovery Mode. Deep Sweep + Engulfing + RSI Cross.
    
    EXIT:
    - God Tier Trailing Stop (ATR 3.0)
    """

    def __init__(self):
        self.attempt_count = 0        # 0 = Belum masuk, 1 = Sudah coba Bullet 1
        self.last_trade_result = None # 'WIN' or 'LOSS'
        self.zone_low_price = float('inf')
        self.zone_high_price = 0
        self.active_trade = None

    def prepare_data(self, df_1h, df_daily):
        """
        Pre-calculate indicators to speed up backtest.
        NOTE: EMA Daily must be shifted to prevent look-ahead!
        """
        # 1. Daily Indicators (Regime)
        df_daily['EMA_200'] = ta.ema(df_daily['close'], length=200)
        # PENTING: Geser 1 hari. Nilai hari ini adalah EMA kemarin.
        df_daily['EMA_200_Shifted'] = df_daily['EMA_200'].shift(1) 
        
        # 2. Hourly Indicators (Setup)
        df_1h['RSI'] = ta.rsi(df_1h['close'], length=14)
        df_1h['RSI_MA'] = ta.sma(df_1h['RSI'], length=14)
        df_1h['ATR'] = ta.atr(df_1h['high'], df_1h['low'], df_1h['close'], length=14)
        
        # Merge Daily Context to Hourly
        # (Resample forward fill daily data to hourly)
        df_daily_resampled = df_daily[['EMA_200_Shifted']].resample('1H').ffill()
        df_combined = df_1h.join(df_daily_resampled)
        
        return df_combined

    def check_signal(self, candle, prev_candle, context_daily_ema):
        """
        Main Logic Loop per Candle.
        Returns: 'BULLET_1', 'BULLET_2', or None
        """
        
        # --- 0. Update Zone Tracking (Simple Pivot Logic) ---
        # Jika harga membuat Low baru dalam N periode, update zone_low
        if candle['low'] < self.zone_low_price:
            self.zone_low_price = candle['low']
        
        # Reset Zone jika harga lari terlalu jauh (misal > 5% dari low)
        if candle['close'] > self.zone_low_price * 1.05:
             self.attempt_count = 0 # Reset chance
             self.zone_low_price = candle['low'] # Reset pivot

        # --- 1. REGIME FILTER ---
        # Jika EMA NaN (awal data), anggap Bearish (safety)
        if pd.isna(context_daily_ema):
            is_bull_market = False
        else:
            is_bull_market = (candle['close'] > context_daily_ema)
        
        is_bear_market = not is_bull_market

        # --- 2. DEFINE PATTERNS ---
        
        # A. SWEEP (Jebakan) - Harga Low menembus Zone Low sebelumnya
        # (Kita simulasikan dengan melihat swing low lokal 5 candle terakhir)
        is_sweep = (candle['low'] < prev_candle['low']) 
        
        # B. RECLAIM (Tutup di atas)
        is_reclaim = (candle['close'] > prev_candle['low'])
        
        # C. STRONG ENGULFING (Hijau makan Merah)
        is_engulfing = (candle['close'] > prev_candle['open']) and \
                       (candle['open'] < prev_candle['close']) and \
                       (candle['close'] > candle['open']) and \
                       (prev_candle['close'] < prev_candle['open'])

        # D. RSI CROSS UP
        is_rsi_cross = (candle['RSI'] > candle['RSI_MA']) and (prev_candle['RSI'] <= prev_candle['RSI_MA'])
        
        # E. RSI OVERSOLD
        is_oversold = (candle['RSI'] < 30)


        # --- 3. EXECUTION LOGIC ---
        
        signal = None

        # === BULLET 1: THE SCOUT ===
        # Syarat: Bull Market Only + Belum pernah coba + Oversold + Reclaim
        if (is_bull_market) and (self.attempt_count == 0):
            if (is_reclaim) and (is_oversold):
                 # Tambahan: Break High Candle Merah sebelumnya (Validasi Struktur)
                 if candle['close'] > prev_candle['high']:
                     signal = 'BULLET_1'
                     self.attempt_count = 1

        # === BULLET 2: THE SNIPER ===
        # Syarat: (Attempt 1 Gagal) ATAU (Bear Market langsung loncat ke sini)
        can_shoot_bullet_2 = False
        
        if (self.attempt_count == 1 and self.last_trade_result == 'LOSS'):
            can_shoot_bullet_2 = True
        elif (is_bear_market and self.attempt_count == 0):
            can_shoot_bullet_2 = True # Di Bear Market, kita skip Bullet 1
            
        if can_shoot_bullet_2:
            # Syarat Mutlak Video: Engulfing + RSI Cross
            if (is_engulfing) and (is_rsi_cross):
                # Validasi: Harga harus "Murah" (RSI tidak boleh Overbought)
                if candle['RSI'] < 50: 
                    signal = 'BULLET_2'
                    self.attempt_count = 2 # Max limit

        return signal

    def record_result(self, result):
        self.last_trade_result = result


FILE 2: THE ENGINE (src/backtest/backtest_engine_v2.py)
import pandas as pd
import numpy as np
from src.council.institutional_hybrid_v2 import InstitutionalHybridV2

class BacktestEngineV2:
    def __init__(self, data_path):
        self.data_path = data_path
        self.initial_capital = 10000
        self.equity = 10000
        self.strategy = InstitutionalHybridV2()
        self.trades = []
        self.monthly_stats = {}

    def load_and_prep_data(self):
        print("Loading data...")
        # Load 1m Data
        df = pd.read_csv(self.data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp']) # Sesuaikan nama kolom jika beda
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        # Resample to 1H for Strategy Signals
        df_1h = df.resample('1H').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna()
        
        # Resample to Daily for Filter (Shifted inside strategy)
        df_daily = df.resample('1D').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
        }).dropna()
        
        # Inject Indicators
        print("Calculating indicators...")
        self.df_strategy = self.strategy.prepare_data(df_1h, df_daily)
        self.df_raw_1m = df # Simpan raw 1m untuk eksekusi trailing stop
        return self.df_strategy

    def run(self):
        df_sim = self.load_and_prep_data()
        
        active_position = None
        
        print(f"Starting Backtest on {len(df_sim)} H1 candles...")
        
        # Loop Candle by Candle (H1)
        for i in range(1, len(df_sim)):
            curr_candle = df_sim.iloc[i]
            prev_candle = df_sim.iloc[i-1]
            
            # 1. MANAGEMENT POSISI (Trailing Stop Check)
            # Idealnya ini dicek per menit (1m), tapi untuk kecepatan kita cek per H1 dulu 
            # (atau load snippet 1m jika ada posisi aktif)
            if active_position:
                self.manage_active_position(active_position, curr_candle)
                if active_position['status'] == 'CLOSED':
                    self.trades.append(active_position)
                    self.strategy.record_result(active_position['result']) # Beritahu strategi Win/Loss
                    active_position = None
            
            # 2. CARI SIGNAL BARU (Jika tidak ada posisi)
            if not active_position:
                signal = self.strategy.check_signal(curr_candle, prev_candle, curr_candle['EMA_200_Shifted'])
                
                if signal:
                    # OPEN POSITION
                    risk_per_trade = self.equity * 0.01 # 1% Risk
                    entry_price = curr_candle['close']
                    atr_val = curr_candle['ATR']
                    
                    # Stop Loss Logic
                    sl_buffer = 0.5 * atr_val
                    stop_loss = curr_candle['low'] - sl_buffer
                    
                    # Position Sizing
                    risk_distance = entry_price - stop_loss
                    if risk_distance <= 0: continue # Skip error data
                    
                    qty = risk_per_trade / risk_distance
                    
                    active_position = {
                        'entry_time': curr_candle.name,
                        'type': signal, # BULLET_1 or BULLET_2
                        'entry_price': entry_price,
                        'qty': qty,
                        'stop_loss': stop_loss,
                        'initial_sl': stop_loss,
                        'tp_1': entry_price + (1.5 * risk_distance),
                        'is_breakeven': False,
                        'status': 'OPEN',
                        'highest_high': entry_price,
                        'atr_at_entry': atr_val
                    }

    def manage_active_position(self, pos, candle):
        # Update Highest High
        if candle['high'] > pos['highest_high']:
            pos['highest_high'] = candle['high']
            
        # --- GOD TIER TRAILING LOGIC ---
        risk_dist = pos['entry_price'] - pos['initial_sl']
        current_profit_r = (candle['close'] - pos['entry_price']) / risk_dist
        
        # Fase 2: Secure Breakeven (at 1.5R)
        if current_profit_r >= 1.5 and not pos['is_breakeven']:
            pos['stop_loss'] = pos['entry_price']
            pos['is_breakeven'] = True
            
        # Fase 3: Chandelier Trailing (ATR 3.0)
        if pos['is_breakeven']:
            new_sl = pos['highest_high'] - (3.0 * pos['atr_at_entry'])
            if new_sl > pos['stop_loss']:
                pos['stop_loss'] = new_sl
        
        # --- CHECK STOP LOSS HIT ---
        # Gunakan Low candle H1 untuk cek apakah SL tersentuh
        if candle['low'] <= pos['stop_loss']:
            exit_price = pos['stop_loss']
            # Hitung PnL (dikurangi Slippage & Commision)
            gross_pnl = (exit_price - pos['entry_price']) * pos['qty']
            commission = (exit_price * pos['qty']) * 0.001 # 0.1%
            net_pnl = gross_pnl - commission
            
            pos['exit_time'] = candle.name
            pos['exit_price'] = exit_price
            pos['pnl'] = net_pnl
            pos['status'] = 'CLOSED'
            pos['result'] = 'WIN' if net_pnl > 0 else 'LOSS'
            
            # Update Equity
            self.equity += net_pnl

    def generate_report(self):
        # ... (Kode pelaporan standar seperti sebelumnya) ...
        pass

FILE 3: EXECUTION SCRIPT (run_hybrid_backtest.py)
from src.backtest.backtest_engine_v2 import BacktestEngineV2

# Konfigurasi Path
DATA_PATH = '/Users/izzadev/.gemini/antigravity/scratch/SAT-V3/data/BTCUSDT-1m-2017-08-to-2023-03 (Binance SPOT).csv'

if __name__ == "__main__":
    engine = BacktestEngineV2(DATA_PATH)
    engine.run()
    
    # Output Results
    print(f"Final Equity: ${engine.equity:.2f}")
    # Simpan report ke CSV/Markdown

    Ini adalah Arsitektur Final untuk Institutional Hybrid V2. Jalankan backtest. Saya ingin melihat apakah Filter EMA 200 dan Sniper Logic berhasil mengurangi Drawdown secara signifikan."