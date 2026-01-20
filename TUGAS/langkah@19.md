SYSTEM PROMPT: TECHNICAL SPECIFICATION FOR HYBRID V2
To: Antigravity AI Action: Implementasi Strategi Trading berikut ke dalam Python Class untuk Backtesting. Gunakan logika state-machine untuk menangani urutan peluru (Bullet 1 & Bullet 2).

STRATEGY NAME: Institutional_Hybrid_V2

1. GLOBAL VARIABLES & INDICATORS
# Setup Indikator
EMA_200_Daily = TA.EMA(Daily_Close, 200)
RSI_14 = TA.RSI(Close_1m, 14)
RSI_MA_14 = TA.SMA(RSI_14, 14) # Moving Average dari RSI
ATR_14 = TA.ATR(14)

# State Variables (Memory)
var attempt_count = 0        # Hitung percobaan di zona ini
var last_trade_result = NONE # WIN / LOSS
var zone_low_price = 999999  # Harga terendah dari zona support

2. ENTRY LOGIC MODULE (The Core Brain)
Terapkan logika ini pada setiap Candle Baru (Loop):
def check_entry_signal(candle, trend_state):
    
    # --- STEP 1: REGIME FILTER (Perisai EMA 200) ---
    is_bull_market = (current_price > EMA_200_Daily)
    is_bear_market = (current_price < EMA_200_Daily)

    # --- STEP 2: DEFINISI SIGNAL ---
    
    # Definisi 1: SWEEP (Jebakan)
    # Harga Low candle ini menembus Zone Low sebelumnya
    is_sweep = (candle.low < zone_low_price)
    
    # Definisi 2: RECLAIM (Kembali ke Atas)
    # Body Candle menutup di atas Zone Low
    is_reclaim = (candle.close > zone_low_price)
    
    # Definisi 3: STRONG ENGULFING (Untuk Peluru 2)
    # Candle Hijau Besar memakan Candle Merah sebelumnya
    is_engulfing = (candle.close > prev_candle.open) and \
                   (candle.open < prev_candle.close) and \
                   (candle.close > candle.open) # Harus Hijau

    # Definisi 4: RSI MA CROSS (Konfirmasi Momentum)
    is_rsi_cross_up = (RSI_14 > RSI_MA_14) and (prev_RSI_14 < prev_RSI_MA_14)
    
    # Definisi 5: RSI OVERSOLD (Untuk Peluru 1)
    is_oversold = (RSI_14 < 30)


    # --- STEP 3: EKSEKUSI PELURU (THE TWO BULLETS) ---

    # === PELURU 1: THE SCOUT ===
    # Syarat: Market BULLISH, Belum pernah coba (Attempt 0), Oversold, Reclaim.
    if (is_bull_market) and (attempt_count == 0):
        if (is_sweep) and (is_reclaim) and (is_oversold):
            # Tambahan: Validasi Break High Candle Merah sebelumnya
            if (candle.close > prev_candle.high):
                attempt_count = 1
                return "BUY_SIGNAL_BULLET_1"

    # === PELURU 2: THE SNIPER (REVENGE) ===
    # Syarat: Peluru 1 Gagal (Attempt 1 & Loss) ATAU Bear Market (Attempt 0).
    # Khusus Bear Market, kita skip Peluru 1 dan langsung pakai logika Peluru 2 tapi risk kecil.
    
    can_shoot_bullet_2 = False
    
    if (attempt_count == 1 and last_trade_result == "LOSS"):
        can_shoot_bullet_2 = True # Mode Balas Dendam
    elif (is_bear_market and attempt_count == 0):
        can_shoot_bullet_2 = True # Mode Bearish Sniper (Langsung ke Bullet 2)

    if (can_shoot_bullet_2):
        # Syarat Mutlak Video Forex Sarjana:
        # 1. Harga Lebih Murah (Deep Sweep)
        # 2. Ada Engulfing
        # 3. Ada RSI Cross
        
        is_deep_sweep = (candle.low < prev_entry_stop_loss) # Harga lebih rendah dari SL sebelumnya
        
        if (is_deep_sweep) and (is_engulfing) and (is_rsi_cross_up):
             attempt_count = 2 # Max Limit Reached
             return "BUY_SIGNAL_BULLET_2"

    return "NO_SIGNAL"

3. EXIT & RISK MANAGEMENT LOGIC
def manage_risk(trade):
    
    # --- A. SETUP STOP LOSS AWAL ---
    if trade.is_new:
        swing_low = get_lowest_low(window=5) # Cari ekor terendah 5 candle terakhir
        trade.stop_loss = swing_low - (0.5 * ATR_14)
        trade.tp_1 = trade.entry_price + (1.5 * trade.risk_distance) # Target 1.5R
        
        # Risk Sizing Rule
        if trade.type == "BULLET_1":
            trade.size = 1.0% Equity
        elif trade.type == "BULLET_2":
            trade.size = 1.0% Equity (NO MARTINGALE!)

    # --- B. GOD TIER TRAILING STOP ---
    current_profit_r = (current_price - trade.entry_price) / trade.risk_distance

    # Fase 1: Dormant (Tidur)
    if current_profit_r < 1.5:
        pass # Jangan ubah SL

    # Fase 2: Secure (Kunci BEP)
    elif current_profit_r >= 1.5 and not trade.is_breakeven:
        trade.stop_loss = trade.entry_price
        trade.is_breakeven = True

    # Fase 3: Trailing (Chandelier Exit)
    elif trade.is_breakeven:
        # Cari High Tertinggi sejak Entry
        highest_high = get_highest_high_since_entry()
        
        # Rumus ATR Trailing Multiplier 3.0
        new_sl = highest_high - (3.0 * ATR_14)
        
        # SL hanya boleh NAIK
        if new_sl > trade.stop_loss:
            trade.stop_loss = new_sl

