Betul Prof, saya melihat masalahnya. Candle tersebut terlihat "gepeng" (squashed) dan terlalu kurus karena dua alasan teknis pada logika matematikanya:

Masalah Skala (Y-Axis Scaling): Chart saat ini menghitung minPrice dan maxPrice dari SELURUH data (history), bukan hanya data yang TERLIHAT di layar. Akibatnya, jika ada satu jarum panjang (wick) di masa lalu yang sangat tinggi/rendah, seluruh chart akan mengecil (zoom out) untuk memuat jarum tersebut.

Solusi: Kita harus ubah menjadi "Viewport Auto-Scaling". Skala harga harus dihitung ulang secara dinamis hanya berdasarkan candle yang sedang tampil di layar.

Masalah Ketebalan (Candle Width): Lebar body candle mungkin di-set ke nilai pixel statis (misal: 1px atau 2px), padahal seharusnya dinamis (persentase dari lebar slot waktu).

Mari kita perbaiki ini agar tampilannya "ganteng" dan proporsional seperti TradingView asli.

Silakan berikan Prompt Perbaikan (Tahap 3) ini ke Antigravity:

🛠️ PROMPT TAHAP 3: Fix Scaling & Modern Styling
Copy & Paste perintah ini:

Plaintext

The candles are rendering, but they look "squashed" (too thin and flat). The Y-axis scaling is currently incorrect because it considers the global min/max instead of the local viewport.

**Task:** Refine the `ChartCanvas.tsx` rendering logic to implement "Viewport Auto-Scaling" and "Modern Candle Styling".

**Requirements:**

1.  **Implement Viewport Auto-Scaling (Crucial):**
    * Inside the `draw` loop, BEFORE calculating `priceToY`, calculate `minPrice` and `maxPrice` based **ONLY** on the `visibleData` (the candles currently inside the start/end index).
    * **Add Padding:** Apply a 10% padding to the top and bottom of the Y-axis so the high/low candles don't touch the canvas edges.
        * `range = max - min`
        * `yMax = max + (range * 0.1)`
        * `yMin = min - (range * 0.1)`

2.  **Fix Candle Width (Chunky/Modern Look):**
    * Instead of a fixed pixel width, calculate `candleWidth` dynamically.
    * `slotWidth = canvasWidth / visibleCandleCount`
    * `candleWidth = slotWidth * 0.8` (Leaves 20% gap between candles for a clean look).
    * Ensure `candleWidth` is never less than 1px.

3.  **Refine Visual Style:**
    * **Wicks:** Should be strictly 1px thick (centered).
    * **Colors:** Use slightly brighter, more modern colors:
        * Up (Green): `#089981`
        * Down (Red): `#F23645`
    * **Crisp Rendering:** Use `Math.floor(x) + 0.5` for the wick coordinates to ensure they snap to the pixel grid and look sharp (anti-aliasing fix).

**Output:**
Provide the updated rendering logic/function for `ChartCanvas.tsx`.
Apa yang akan berubah setelah kode ini?

Body Candle Lebih Gemuk: Karena kita menggunakan rumus slotWidth * 0.8, candle akan mengisi ruang dengan padat dan enak dilihat.

Chart Lebih "Tinggi": Chart tidak akan lagi gepeng. Dia akan otomatis zoom-in secara vertikal menyesuaikan harga yang sedang dilihat (mengabaikan harga ekstrim yang ada jauh di belakang/depan).

Silakan dijalankan, Prof! Hasilnya harusnya sudah sangat mirip dengan screenshot TradingView asli.