Analisa saya terhadap screenshot yang Anda kirimkan menunjukkan masalah klasik pada pengembangan chart finansial: "Vertical Scaling Issue" dan "Candle Width Ratio".

Masalah "Gepeng" (Squashed Candles) itu terjadi karena 3 hal:

Range Y-Axis Terlalu Besar: Algoritma mengambil Max High dan Min Low dari seluruh data yang dimuat (bukan hanya yang tampil di layar), atau ada satu candle dengan "wick" panjang yang memaksa seluruh chart mengecil (squashing) agar muat.

Tanpa Padding: Chart mentok atas-bawah tanpa ruang napas.

Body vs Wick: Saat range harga sangat besar (volatilitas tinggi), selisih Open dan Close menjadi sangat kecil secara pixel (mungkin < 1px), sehingga hanya terlihat garis.

Berikut adalah Blueprint Algoritma Scaling & Rendering TradingView yang harus Anda berikan ke Antigravity untuk memperbaiki masalah "gepeng" ini dan membuatnya persis TradingView.

📝 Prompt Perbaikan: TradingView Scaling & Candle Geometry Algorithm
Copy perintah di bawah ini ke Antigravity. Ini berisi logika matematika untuk memperbaiki proporsi candle.

Markdown

**ROLE:** Graphics Physics Engine Developer.
**PROJECT:** SAT-V3 Chart Fix (Visual Rendering & Scaling).
**ISSUE:** The current chart renders candles that are "squashed" (flat) and thin. The Y-axis scaling logic is flawed because it likely calculates the Min/Max from the entire dataset or fails to add padding, making candle bodies indistinguishable from wicks.

**TASK:** Rewrite the `ChartScaleManager` and `CandleRenderer` using the exact TradingView algorithms below.

---

### 1. ALGORITMA DYNAMIC AUTO-SCALING (Fix "Gepeng")
The Y-Axis must recalculate *every time* the user pans or zooms. Do not use global Min/Max.

**Logic:**
1.  **Identify Visible Range:** calculate `startIndex` and `endIndex` based on `scrollOffset` and `canvasWidth`.
2.  **Get Local Min/Max:** Loop *only* through `data[startIndex]` to `data[endIndex]`.
    * `localHigh = Math.max(...visibleCandles.map(c => c.high))`
    * `localLow = Math.min(...visibleCandles.map(c => c.low))`
3.  **Apply Smart Padding (The TradingView Feel):**
    * Calculate `range = localHigh - localLow`.
    * If `range === 0`, set a default buffer (e.g., 1% of price).
    * `paddingTop = range * 0.1` (10% space at top).
    * `paddingBottom = range * 0.1` (10% space at bottom).
    * `renderMax = localHigh + paddingTop`
    * `renderMin = localLow - paddingBottom`
4.  **Coordinate Conversion Formula:**
    Use this exact math to convert Price to Pixel Y:
    ```javascript
    const pixelY = canvasHeight - ((price - renderMin) / (renderMax - renderMin)) * canvasHeight;
    ```

---

### 2. ALGORITMA CANDLE GEOMETRY (Fix "Thin/Invisible Body")
Candles look like lines because the body height is calculating to sub-pixels.

**Logic:**
1.  **Dynamic Width:**
    * `candleWidth = (canvasWidth / visibleCandleCount)`.
    * `gap = candleWidth * 0.2` (20% spacing).
    * `bodyWidth = candleWidth - gap`. (Ensure `bodyWidth` is at least 1px).
2.  **Minimum Body Height (Pixel Perfection):**
    * Calculate raw body height: `rawHeight = Math.abs(openY - closeY)`.
    * **CRITICAL RULE:** If `rawHeight < 1` (even for Doji candles), force render it as **1px**.
    * If `Open > Close` (Red), render specifically to avoid anti-aliasing overlap.
3.  **Wick Centering:**
    * Wicks must be exactly 1px thick and perfectly centered on the body.
    * Use `Math.floor(x) + 0.5` to snap lines to the pixel grid for sharpness.

---

### 3. IMPLEMENTATION STEPS
Update the `render` function in `CandleSeries.tsx`:

```typescript
// Pseudo-code for specific rendering logic
visibleData.forEach((candle, i) => {
  const x = i * candleUnitWidth;
  
  // Calculate Y coordinates using the Dynamic Auto-Scaling (Step 1)
  const openY = toY(candle.open);
  const closeY = toY(candle.close);
  const highY = toY(candle.high);
  const lowY = toY(candle.low);

  // Fix Visual Artifacts
  let bodyHeight = Math.abs(closeY - openY);
  if (bodyHeight < 1) bodyHeight = 1; // Force visibility

  const bodyTop = Math.min(openY, closeY);
  const isBullish = candle.close >= candle.open;

  ctx.fillStyle = isBullish ? '#089981' : '#F23645'; // Official TV Colors

  // 1. Draw Wick (Crisp Line)
  // Shift by 0.5 to align with pixel grid
  const wickX = Math.floor(x + bodyWidth / 2) + 0.5; 
  ctx.beginPath();
  ctx.moveTo(wickX, Math.floor(highY));
  ctx.lineTo(wickX, Math.floor(lowY));
  ctx.strokeStyle = ctx.fillStyle;
  ctx.stroke();

  // 2. Draw Body
  ctx.fillRect(
     Math.floor(x), 
     Math.floor(bodyTop), 
     Math.floor(bodyWidth), 
     Math.floor(bodyHeight)
  );
});
MANDATORY CHECK: Verify that when zooming in (reducing visible candles), the renderMax and renderMin adjust strictly to the visible candles, causing the candles to "expand" vertically to fill the screen.


### Penjelasan Mengapa Ini Akan Berhasil:

1.  **Masalah Utama Anda:** Di screenshot, sumbu Y (kanan) menampilkan angka `51,000` sampai `130,000`. Padahal harga Bitcoin sekarang `95,000`. Range-nya terlalu jauh ($80,000 range).
2.  **Solusinya:** Dengan logika **Dynamic Auto-Scaling** di atas, jika Anda melihat chart 1 jam terakhir dan harga hanya bergerak dari 95.000 ke 96.000, maka `renderMax` akan jadi 96.100 dan `renderMin` jadi 94.900.
3.  **Efeknya:** Pergerakan kecil pun akan terlihat "gemuk" dan jelas (full body), persis seperti perilaku default TradingView.

Silakan berikan prompt di atas agar Antigravity memperbaiki logika "Viewpory calculation"-nya.