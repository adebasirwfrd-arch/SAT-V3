Cerdas. Kau tidak ingin hanya masuk dengan presisi, tapi kau juga ingin keluar dengan maksimal tanpa terlempar keluar dari roket gara-gara guncangan turbulensi kecil (whipsaw).

Dengarkan baik-baik, Ade. Trailing Stop biasa (Fixed Pips) adalah makanan empuk Institusi. Mereka tahu ritel menaruh trailing stop 10-20 pips di belakang harga. Mereka tinggal "mengibas" ekor sedikit, memakan stop loss-mu, lalu lanjut terbang. Kau tertinggal di landasan sambil menangis.

Untuk membuat "God Tier Trailing Stop", kita tidak menggunakan jarak harga fix. Kita menggunakan VOLATILITAS DINAMIS dan STRUKTUR PASAR.

Ini adalah Logic Blueprint yang harus kau masukkan ke Antigravity. Ini bukan sekadar kode, ini adalah algoritma perilaku.

A. Core Engine: The Entry Logic (Trap + Reclaim + Divergence)
Berikan instruksi ini pada Antigravity untuk mendeteksi Setup kita:

1. Definisi Variabel:

Swing_Low: Titik terendah dari fractal sebelumnya (Support).

Current_Low: Titik terendah candle saat ini.

Current_Close: Harga penutupan candle saat ini.

RSI_Current: Nilai RSI candle saat ini.

RSI_Previous_Low: Nilai RSI pada saat Swing_Low terjadi.

2. Logic Entry (Pseudo-Code):
IF (Current_Low < Swing_Low) AND (Current_Close > Swing_Low):
    # Kondisi 1: Liquidity Sweep & Reclaim terjadi (Harga tusuk bawah, tutup atas)

    IF (RSI_Current > RSI_Previous_Low):
        # Kondisi 2: Bullish Divergence (Harga Lower Low, RSI Higher Low)

        EXECUTE_BUY_ORDER()
        SET INITIAL_STOP_LOSS = Current_Low - (ATR * 0.5)
        # SL ditaruh sedikit di bawah ekor candle jebakan (buffer pakai ATR)

B. The "God Tier" Trailing Stop Logic (Anti-Whipsaw)
Ini bagian terpentingnya. Kita akan menggunakan kombinasi ATR (Average True Range) dan Step-Based Activation.

Filosofi: Jangan aktifkan trailing stop saat harga baru bergerak sedikit. Biarkan harga bernapas.

Logic Trailing Stop:

Zona Tidur (Dormant Phase): Selama profit belum mencapai 1.5R (1.5 kali risiko awal), Trailing Stop MATI. Biarkan SL di posisi awal. Jangan digeser. Ini untuk menghindari "Noise" awal.

Fase Pengamanan (Breakeven Trigger): JIKA Current_Price >= Entry_Price + (1.5 * Risk_Distance):

GESER Stop Loss ke Entry_Price (Breakeven).

Sekarang risiko kita 0.

Fase Pengawalan (Volatility-Based Trailing): Setelah fase Breakeven, kita gunakan ATR Multiplier.

Gunakan ATR periode 14.

Multiplier yang aman untuk "S3 Trading" adalah 2.5 atau 3.0. (Ritel biasa pakai 1.5, itu terlalu sempit).

Instruksi Logic untuk Antigravity:
# Definisi Variable
Entry_Price = [Harga Beli]
Initial_SL = [Harga SL Awal]
Risk_Distance = Entry_Price - Initial_SL
ATR_Value = CALC_ATR(14)
Trailing_Multiplier = 3.0 # Angka keramat untuk menghindari whipsaw wajar

# Logic Loop (Jalan setiap close candle)
IF (Current_Profit_Rasio < 1.5):
    # Fase 1: Jangan lakukan apapun. Biarkan market bernapas.
    Current_SL = Initial_SL

ELSE IF (Current_Profit_Rasio >= 1.5) AND (SL_Is_At_Breakeven == False):
    # Fase 2: Kunci modal dulu.
    Current_SL = Entry_Price
    SL_Is_At_Breakeven = True

ELSE IF (SL_Is_At_Breakeven == True):
    # Fase 3: God Tier Trailing (Chandelier Exit Logic)
    # Hitung titik High tertinggi sejak kita entry
    Highest_High_Since_Entry = GET_MAX_HIGH_SINCE_ENTRY()

    # Hitung calon SL baru berdasarkan Volatilitas
    Potential_New_SL = Highest_High_Since_Entry - (ATR_Value * Trailing_Multiplier)

    # ATURAN EMAS: Stop Loss HANYA boleh naik, TIDAK boleh turun
    IF (Potential_New_SL > Current_SL):
        Current_SL = Potential_New_SL

Kenapa Logic Ini Disebut "God Tier"?
Anti-Jebakan (Multiplier 3.0): Paus sering membanting harga (koreksi) sedalam 1x atau 2x ATR untuk mengusir penumpang ritel. Dengan memakai multiplier 3.0 ATR, SL-mu berada di luar jangkauan "nafas normal" market. SL-mu hanya akan tersentuh jika tren benar-benar berubah arah (Reversal), bukan sekadar koreksi.

Breathing Room (Fase Tidur): Banyak algo trading hancur karena begitu harga hijau sedikit, SL langsung digeser. Akibatnya, saat harga retest entry (hal yang sangat wajar), mereka kena likuidasi. Logic "Fase Tidur" mencegah hal ini.

Dinamis: Saat pasar sedang gila (Volatilitas tinggi/ATR besar), jarak SL-mu otomatis melebar (memberi ruang gerak). Saat pasar tenang (ATR kecil), SL-mu merapat (mengunci profit lebih ketat). Ini adaptasi otomatis.

Saran Implementasi ke Antigravity/Cursor:
Minta Antigravity membuatkan fungsi terpisah bernama calculateGodTierTrailing().

Pastikan dia menggunakan data Close Candle untuk memicu trailing, bukan Running Price, agar tidak tertipu oleh ekor candle liar yang terjadi sesaat.

Ini adalah blueprint senjata mesinmu, Ade. Implementasikan ini, dan kau akan melihat posisimu bertahan melewati badai di mana trader lain berguguran, lalu kau akan panen di puncak.