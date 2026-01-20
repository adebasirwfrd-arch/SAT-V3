ni adalah saatnya pembuktian, Ade. Kita akan meninggalkan "medan latihan" (Testnet) dan masuk ke dalam "Mesin Waktu".

Data BTC dari 2017 sampai 2023 adalah "The Ultimate Stress Test". Di sana ada Bull Run gila (2017, 2021), ada Crypto Winter yang mematikan (2018, 2022), ada Sideways yang membosankan, dan ada Black Swan events.

Jika strategimu ("Entry Logic" + "Game Theory" + "God Tier Trailing") bisa bertahan dan profit di rentang waktu ini tanpa melihat masa depan (No Look-Ahead), maka kau sudah siap untuk wisuda.

Berikut adalah Command Prompt Presisi yang harus kau berikan kepada Antigravity. Saya telah menyusunnya dengan bahasa instruksi sistem yang ketat agar tidak ada bias.

SYSTEM COMMAND: PROTOCOL "TIME TRAVELER"
To: Antigravity AI Core From: User (Ade) & The Professor Subject: Historical Backtest Simulation - BTCUSDT (2017-2023)

Objective: Lakukan pengujian Backtest buta (Blind Backtest) menggunakan strategi "Entry Logic" yang telah diperkuat dengan "Game Theory (Double Tap)" dan "God Tier Trailing Stop".

1. DATA CONFIGURATION & PRE-PROCESSING

Source Path: /Users/izzadev/.gemini/antigravity/scratch/SAT-V3/data/BTCUSDT-1m-2017-08-to-2023-03 (Binance SPOT).csv

Action: Putuskan koneksi WebSocket/Live Data. Load data CSV tersebut ke dalam memori.

Resampling Rules (PENTING):

Data sumber adalah 1-Minute (1m). Gunakan ini untuk Execution dan Trailing Stop Check (simulasi real-time).

Lakukan Resample data 1m tersebut menjadi 1-Hour (H1) atau 4-Hour (H4) secara internal untuk mendeteksi Structure, Trend, dan Setup Signal (Sweep & Reclaim).

Warning: Pastikan tidak ada kebocoran data (Look-Ahead Bias). Saat memproses candle jam 10:00, sistem TIDAK BOLEH tahu harga Open/High/Low/Close jam 10:01.

2. STRATEGY INJECTION: "ENTRY LOGIC" WITH GAME THEORY Terapkan algoritma berikut pada setiap iterasi candle:

Setup Detection (H1/H4):

Identifikasi Swing Low Support.

Tunggu harga menembus ke bawah (Sweep).

Cek RSI Divergence (Lower Low Price, Higher Low RSI).

Cek Reclaim (Close Body > Support Level).

Game Theory Protocol (Double Tap):

Jika Entry 1 kena Stop Loss, aktifkan mode "Sniper Watch".

Reset mental: Cari setup Double Sweep (Jebakan Kedua) di zona yang sama.

Entry 2 valid JIKA terjadi Reclaim kedua + Volume Anomaly.

Max Attempt = 2 per zona.

Exit Management (God Tier Trailing):

Gunakan data 1m untuk mengelola Stop Loss secara presisi.

Fase 1: Hold SL (Dormant) sampai profit > 1.5R.

Fase 2: Move to Breakeven.

Fase 3: Trailing dengan Chandelier Exit (ATR Multiplier 3.0, atau 2.5 untuk Entry Kedua).

3. SIMULATION PARAMETERS

Initial Capital: $10,000 (USDT)

Risk Per Trade: 1% dari Equity saat itu (Compounding).

Commission: 0.1% per trade (Entry & Exit) - Simulasi fee Binance Spot.

Slippage: 0.05% (Asumsi market order pada volatilitas 1m).

4. REPORTING REQUIREMENTS (OUTPUT) Lakukan loop simulasi dari awal data hingga akhir. Di setiap akhir bulan kalender, generate laporan berikut:

A. Monthly Performance Report (Format Table):

Month/Year: (e.g., Aug 2017)

Start Equity: (Saldo awal bulan)

End Equity: (Saldo akhir bulan)

Net Profit ($): (Keuntungan bersih)

Gain/Loss (%): (Persentase pertumbuhan)

Winrate (%): (Jumlah Win / Total Trade bulan itu)

Max Drawdown (%): (Penurunan terdalam dari puncak equity bulan itu)

Realized PnL: (Profit yang sudah di-close)

Unrealized PnL: (Floating profit/loss posisi yang masih terbuka di akhir bulan)

B. Monthly Evaluation (AI Insight):

Berikan komentar singkat (1-2 kalimat) tentang performa bulan tersebut.

Contoh: "Bulan ini market trending kuat, Trailing Stop bekerja maksimal." atau "Bulan ini banyak sideways (chop), Game Theory menyelamatkan akun dari 3 false break."

C. FINAL SUMMARY (End of Data)

Total Return: (%)

CAGR: (Compound Annual Growth Rate)

Max Drawdown (All Time):

Sharpe Ratio:

Total Trades:

Average Win vs Average Loss (Risk:Reward Ratio):

Kesimpulan Strategis: Apakah strategi ini layak untuk Live Trading? Apa kelemahan terbesarnya berdasarkan data 6 tahun ini?

Instruksi Tambahan untuk Ade
Salin prompt di atas dan jalankan di terminal Antigravity-mu.

Satu hal yang harus kau ingat saat melihat hasilnya nanti: Jangan terbuai jika melihat angka hijau. Fokuslah pada kolom "Max Drawdown".

Jika Drawdown > 30%, strategi ini terlalu berisiko untuk dana pensiun, walau profitnya besar.

Jika Drawdown < 15% dengan Profit > 50% per tahun, kau telah menemukan Holy Grail.

Silakan eksekusi, Ade. Saya menunggu laporan hasil autopsi pasar 6 tahun ini di meja saya.