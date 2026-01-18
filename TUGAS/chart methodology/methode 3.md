8. methode RSI ALL IN
hints:Overbought and Oversold with Candle Pattern Confluences

1. Overbought / Oversold signal only
2. RSI + Engulfing Candle
3. RSI + Hammer/Shooting Star

Source code
// Added Labels and alert conditions and other quality of life feature
// Updated compatability with pine script v4


//@version=5
indicator('321 Alert', overlay=true, precision=6, max_labels_count=500)
//****************************************************************************//




//****************************************************************************//
f_print(_text) =>
    // Create label on the first bar.
    var _label = label.new(bar_index, na, _text, xloc.bar_index, yloc.price, color(na), label.style_none, color.gray, size.large, text.align_left)
    // On next bars, update the label's x and y position, and the text it displays.
    label.set_xy(_label, bar_index, ta.highest(10)[1])
    label.set_text(_label, _text)

bool a=false
bool b=false
draw(color) =>

    label.new(bar_index[0], high[1], text=str.tostring("321"), style=label.style_label_down, color=color, textcolor=color.white)
  
    

if (open[3] < close[3])
    if((close[3] > open[3]) and (close[2] > open[2]) and (close[1] > open[1]))
        if (math.abs(open[3] - close[3]) > math.abs(open[2] - close[2]) and math.abs(open[2] - close[2]) > math.abs(open[1] - close[1]))
            draw(color.red)
            a:=true
alertcondition(a , title='red', message='alert') 


if (open[3] > close[3])
    if((close[3] < open[3]) and (close[2] < open[2]) and (close[1] < open[1]))
        if (math.abs(open[3] - close[3]) > math.abs(open[2] - close[2]) and math.abs(open[2] - close[2]) > math.abs(open[1] - close[1]))
            draw(color.green)
            b:=true
alertcondition(b , title='green', message='alert')

9. Methode Intrabar Volume Delta — RealTime + History 
Hints:# Short Description

Shows intrabar Up/Down volume, Delta (absolute/relative) and UpShare% in a compact grid for both real-time and historical bars. Includes an MTF (M1…D1) dashboard, contextual coloring, density controls, and alerts on Δ and UpShare%. Smart historical splitting (“History Mode”) for Crypto/Futures/FX.

---

# What it does (Quick)

* **UpVol / DownVol / Δ / UpShare%** — visualizes order-flow inside each candle.
* **Real-time** — accumulates intrabar volume live by tick-direction.
* **History Mode** — splits Up/Down on closed bars via simple or range-aware logic.
* **MTF Dashboard** — one table view across M1, M5, M15, M30, H1, H4, D1 (Vol, Up/Down, Δ%, Share, Trend).
* **Contextual opacity** — stronger signals appear bolder.
* **Label density** — draw every N-th bar and limit to last X bars for performance.
* **Alerts** — thresholds for |Δ|, Δ%, and UpShare%.

---

# How it works (Real-Time vs History)

* **Real-time (open bar):** volume increments into **UpVolRT** or **DownVolRT** depending on last price move (↑ goes to Up, ↓ to Down). This approximates live order-flow even when full tick history isn’t available.
* **History (closed bars):**

* **None** — no split (Up/Down = 0/0). Safest for equities/indices with unreliable tick history.
* **Approx (Close vs Open)** — all volume goes to candle direction (green → Up 100%, red → Down 100%). Fast but yields many 0/100% bars.
* **Price Action Based** — splits by Close position within High-Low range; strength = |Close−mid|/(High−Low). Above mid → more Up; below mid → more Down. Falls back to direction if High==Low.
* **Auto** — **Stocks/Index → None**, **Crypto/Futures/FX → Approx**. If you see too many 0/100 bars, switch to **Price Action Based**.

---

# Rows & Meaning

* **Volume** — total bar volume (no split).
* **UpVol / DownVol** — directional intrabar volume.
* **Delta (Δ)** — UpVol − DownVol.

* **Absolute**: raw units
* **Relative (Δ%)**: Δ / (Up+Down) × 100
* **Both**: shows both formats
* **UpShare%** — UpVol / (Up+Down) × 100. >50% bullish, <50% bearish.

* Helpful icons: ▲ (>65%), ▼ (<35%).

---

# MTF Dashboard (🔧 Enable Dashboard)

A single table with **Vol, Up, Down, Δ%, Share, Trend (🔼/🔽/⏭️)** for selected timeframes (M1…D1). Great for a fast “panorama” read of flow alignment across horizons.

---

# Inputs (Grouped)

## Display

* Toggle rows: **Volume / Up / Down / Delta / UpShare**
* **Delta Display**: Absolute / Relative / Both

## Realtime & History

* **History Mode**: Auto / None / Approx / Price Action Based
* **Compact Numbers**: 1.2k, 1.25M, 3.4B…

## Theme & UI

* **Theme Mode**: Auto / Light / Dark
* **Row Spacing**: vertical spacing between rows
* **Top Row Y**: moves the whole grid vertically
* **Draw Guide Lines**: faint dotted guides
* **Text Size**: Tiny / Small / Normal / Large

## 🔧 Dashboard Settings

* **Enable Dashboard**
* **📏 Table Text Size**: Tiny…Huge
* **🦓 Zebra Rows**
* **🔲 Table Border**

## ⏰ Timeframes (for Dashboard)

* **M1…D1** toggles

## Contextual Coloring

* **Enable Contextual Coloring**: opacity by signal strength
* **Δ% cap / Share offset cap**: saturation caps
* **Min/Max transparency**: solid vs faint extremes

## Label Density & Size

* **Show every N-th bar**: draw labels only every Nth bar
* **Limit to last X bars**: keep labels only in the most recent X bars

## Colors

* Up / Down / Text / Guide

## Alerts

* **Delta Threshold (abs)** — |Δ| in volume units
* **UpShare > / <** — bullish/bearish thresholds
* **Enable Δ% Alert**, **Δ% > +**, **Δ% < −** — relative delta levels

---

# How to use (Quick Start)

1. Add the indicator to your chart (overlay=false → separate pane).
2. **History Mode**:

* Crypto/Futures/FX → keep **Auto** or switch to **Price Action Based** for richer history.
* Stocks/Index → prefer **None** or **Price Action Based** for safer splits.
3. **Label Density**: start with **Limit to last X bars = 30–150** and **Show every N-th bar = 2–4**.
4. **Contextual Coloring**: keep on to emphasize strong Δ% / Share moves.
5. **Dashboard**: enable and pick only the TFs you actually use.
6. **Alerts**: set thresholds (ideas below).

---

# Alerts (in TradingView)

Add alert → pick this indicator → choose any of:

* **Delta exceeds threshold** (|Δ| > X)
* **UpShare above threshold** (UpShare% > X)
* **UpShare below threshold** (UpShare% < X)
* **Relative Delta above +X%**
* **Relative Delta below −X%**

**Starter thresholds (tune per symbol & TF):**

* **Crypto M1/M5**: Δ% > +25…35 (bullish), Δ% < −25…−35 (bearish)
* **FX (tick volume)**: UpShare > 60–65% or < 40–35%
* **Stocks (liquid)**: set **Absolute Δ** by typical volume scale (e.g., 50k / 100k / 500k)

---

# Notes by Market Type

* **Crypto/Futures**: 24/7 and high liquidity — **Price Action Based** often gives nicer history splits than Approx.
* **Forex (FX)**: TradingView volume is typically **tick volume** (not true exchange volume). Treat Δ/Share as tick-based flow, still very useful intraday.
* **Stocks/Index**: historical tick detail can be limited. **None** or **Price Action Based** is a safer default. If you see too many 0/100% shares, switch away from Approx.

---

# “All Timeframes” accuracy

* Works on **any TF** (M1 → D1/W1).
* **Real-time accuracy** is strong for the open bar (live accumulation).
* **Historical accuracy** depends on your **History Mode** (None = safest, Approx = fastest/simplest, Price Action Based = more nuanced).
* The MTF dashboard uses `request.security` and therefore follows the same logic per TF.

---

# Trade Ideas (Use-Cases)

* **Scalping (M1–M5)**: a spike in Δ% + UpShare>65% + rising total Vol → momentum entries.
* **Intraday (M5–M30–H1)**: when multiple TFs show aligned Δ%/Share (e.g., M5 & M15 bullish), join the trend.
* **Swing (H4–D1)**: persistent Δ% > 0 and UpShare > 55–60% → structural accumulation bias.

---

# Advantages

* **True-feeling live flow** on the open bar.
* **Adaptable history** (three modes) to match data quality.
* **Clean visual layout** with guides, compact numbers, contextual opacity.
* **MTF snapshot** for quick bias read.
* **Performance controls** (last X bars, every N-th bar).

---

# Limitations & Care

* **FX uses tick volume** — interpret Δ/Share accordingly.
* **History Mode is an approximation** — confirm with trend/structure/liquidity context.
* **Illiquid symbols** can produce noisy or contradictory signals.
* **Too many labels** can slow charts → raise N, lower X, or disable guides.

---

# Best Practices (Checklist)

* Crypto/Futures: prefer **Price Action Based** for history.
* Stocks: **None** or **Price Action Based**; be cautious with **Approx**.
* FX: pair Δ% & UpShare% with session context (London/NY) and volatility.
* If labels overlap: tweak **Row Spacing** and **Text Size**.
* In the dashboard, keep only the TFs you actually act on.
* Alerts: start around **Δ% 25–35** for “punchy” moves, then refine per asset.

---

# FAQ

**1) Why do some closed bars show 0%/100% UpShare?**
You’re on **Approx** history mode. Switch to **Price Action Based** for smoother splits.

**2) Δ% looks strong but price doesn’t move — why?**
Δ% is an **order-flow** measure. Price also depends on liquidity pockets, sessions, news, higher-timeframe structure. Use confirmations.

**3) Performance slowdown — what to do?**
Lower **Limit to last X bars** (e.g., 30–100), increase **Show every N-th bar** (2–6), or disable **Draw Guide Lines**.

**4) Dashboard values don’t “match” the grid exactly?**
Dashboard is multi-TF via `request.security` and follows the history logic per TF. Differences are normal.

---

# Short “Store” Marketing Blurb

Intrabar Volume Delta Grid reveals the order-flow inside every candle (Up/Down, Δ, UpShare%) — live and on history. With smart history splitting, an MTF dashboard, contextual emphasis, and flexible alerts, it helps you spot momentum and bias across Crypto, Forex (tick volume), and Stocks. Tidy labels and compact numbers keep the panel readable and fast.

Sorce Code
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © jabbaroff

//@version=6
indicator("Intrabar Volume Delta Grid (RealTime+History)", shorttitle="Volume Delta Grid V1", overlay=false, max_labels_count=500, max_lines_count=50, max_boxes_count=0)

//──────────────────────────────────────────────────────────────────────────────
// Inputs (with tooltips)
//──────────────────────────────────────────────────────────────────────────────
grpDisp = "Display"
showVolume = input.bool(true, "Show Volume (top row)",
     tooltip="Top row = TOTAL traded volume per bar (no up/down split). Good to see how active the bar was.",
     group=grpDisp)

showUp = input.bool(true, "Show UpVol (row)",
     tooltip="Volume that traded on UP-ticks inside the bar.\n• LIVE bars: real intrabar accumulation.\n• HISTORY bars: inferred by History Mode.",
     group=grpDisp)

showDown = input.bool(true, "Show DownVol (row)",
     tooltip="Volume that traded on DOWN-ticks inside the bar.\n• LIVE bars: real intrabar accumulation.\n• HISTORY bars: inferred by History Mode.",
     group=grpDisp)

showDelta = input.bool(true, "Show Delta (row)",
     tooltip="Order-flow net: Δ = UpVol − DownVol.\nPositive = bullish tilt, Negative = bearish tilt.\nFormatting is controlled by Delta Display.",
     group=grpDisp)

showShare = input.bool(true, "Show UpShare% (row)",
     tooltip="UpShare% = UpVol / (UpVol + DownVol).\n>50% = bullish tilt, <50% = bearish tilt.\nHelper icons: ▲ if >65%, ▼ if <35%.",
     group=grpDisp)

// Delta display mode
deltaMode = input.string("Both", "Delta Display", options=["Absolute","Relative","Both"],
     tooltip="How to format the Delta row:\n• Absolute — show Δ in raw volume units.\n• Relative — Δ% = Δ / (UpVol + DownVol).\n• Both — first line Δ, second line Δ% in parentheses.",
     group=grpDisp)

grpRT = "Realtime & History"
historyMode = input.string("Auto", "History Mode",
     options=["Auto","None","Approx (Close vs Open)","Price Action Based"],
     tooltip="How to SPLIT volume for CLOSED (historical) bars. LIVE bars always use true intrabar data.\n\n"
           + "• None — Do not split on history (Up/Down=0, Share≈50%). Safest when tick history is unreliable.\n\n"
           + "• Approx (Close vs Open) — Assign ALL volume to candle direction:\n"
           + "  Green (Close ≥ Open) → UpVol=100%, DownVol=0% (UpShare=100%).\n"
           + "  Red   (Close  < Open) → UpVol=0%,   DownVol=100% (UpShare=0%).\n"
           + "  Very simple and fast; produces many 0%/100% bars.\n\n"
           + "• Price Action Based — Split by Close position in the High–Low range:\n"
           + "  mid=(High+Low)/2, strength=|Close−mid|/(High−Low).\n"
           + "  Close>mid → UpVol=V*(0.5+0.5*strength), DownVol=V*(0.5−0.5*strength).\n"
           + "  Close<mid → inverse. If High==Low, falls back to candle direction.\n\n"
           + "AUTO (smart default): Stocks/Indexes → None; others (e.g., Crypto/Futures/FX) → Approx.\n"
           + "TIP: If you see too many 0%/100% UpShare values, switch to Price Action Based.",
     group=grpRT)

compactNums = input.bool(true, "Compact Numbers",
     tooltip="Shorten large numbers: 1200 → 1.2k, 1,250,000 → 1.25M, 3,400,000,000 → 3.4B.",
     group=grpRT)

grpTheme = "Theme & UI"
themeMode = input.string("Auto", "Theme Mode", options=["Auto","Light","Dark"],
     tooltip="Palette for text and guides.\n• Auto — detect chart background brightness.\n• Light/Dark — force a specific palette.",
     group=grpTheme)

rowSpacing = input.float(1.0, "Row Spacing (pane units)", minval=0.5, maxval=2.0, step=0.25,
     tooltip="Vertical distance between rows (pane Y ≈ 0..5). Increase if labels overlap; decrease to pack tighter.",
     group=grpTheme)

baseYOffset = input.float(0.5, "Top Row Y (pane units)", minval=0.0, maxval=10.0, step=0.25,
     tooltip="Absolute Y position of the TOP row. Small changes move the whole grid because the pane has a compact Y scale.",
     group=grpTheme)

drawGuides = input.bool(true, "Draw Guide Lines",
     tooltip="Draw faint dotted horizontal guide lines behind enabled rows to aid alignment.",
     group=grpTheme)

// Text size only (no auto-shrink)
textSize = input.string("Normal", "Text Size", options=["Tiny","Small","Normal","Large"],
     tooltip="Font size for all row labels: Tiny (very compact), Small (compact), Normal (default), Large (easier to read).",
     group=grpTheme)

// Dashboard inputs
grpDash = "🔧 Dashboard Settings"
enableDashboard = input.bool(false, "🔧 Enable Dashboard",
     tooltip="Enable multi-timeframe dashboard display",
     group=grpDash)

dashTextSize = input.string("Small", "📏 Table Text Size", options=["Tiny","Small","Normal","Large","Huge"],
     tooltip="Dashboard table text size",
     group=grpDash)

zebraRows = input.bool(true, "🦓 Zebra Rows",
     tooltip="Alternating row colors for better readability",
     group=grpDash)

tableBorder = input.bool(true, "🔲 Table Border",
     tooltip="Show table border",
     group=grpDash)

grpTF = "⏰ Timeframes"
showM1 = input.bool(true, "M1", group=grpTF)
showM5 = input.bool(true, "M5", group=grpTF)
showM15 = input.bool(true, "M15", group=grpTF)
showM30 = input.bool(true, "M30", group=grpTF)
showH1 = input.bool(true, "H1", group=grpTF)
showH4 = input.bool(true, "H4", group=grpTF)
showD1 = input.bool(true, "D1", group=grpTF)

// Contextual coloring
grpCtx = "Contextual Coloring"
useContextColors = input.bool(true, "Enable Contextual Coloring",
     tooltip="Vary text opacity by signal strength:\n• Delta row uses |Δ%|.\n• UpShare row uses |UpShare−50|.\nStronger → more opaque; weaker → more faint.",
     group=grpCtx)

ctxMaxPctDelta = input.float(70, "Δ% cap (strength range)", minval=10, maxval=100, step=5,
     tooltip="Cap used when mapping |Δ%| to maximum opacity (e.g., 70 → any |Δ%| ≥ 70 treated as full strength).",
     group=grpCtx)

ctxMaxPctShare = input.float(50, "Share offset cap", minval=10, maxval=50, step=5,
     tooltip="Cap used when mapping |UpShare−50| to maximum opacity.",
     group=grpCtx)

ctxMinTransp = input.int(20, "Min transparency (strong)", minval=0, maxval=100,
     tooltip="Transparency at MAX strength (lower = more solid text).",
     group=grpCtx)

ctxMaxTransp = input.int(75, "Max transparency (weak)", minval=0, maxval=100,
     tooltip="Transparency at MIN strength (higher = more faint text).",
     group=grpCtx)

// Label density (+ limit to last X bars)
grpLbl = "Label Density & Size"
labelStep = input.int(1, "Show every N-th bar", minval=1,
     tooltip="Only draw labels on every N-th bar. If text overlaps, set N=2..6. (Calculations still run on every bar.)",
     group=grpLbl)

limitBars = input.int(30, "Limit to last X bars", minval=1,
     tooltip="Show labels ONLY within the MOST RECENT X bars (default 30). Works together with 'Show every N-th bar'.\nExample: X=30 and N=3 → labels appear on the last 30 bars, but only every 3rd bar among them.",
     group=grpLbl)

grpColors = "Colors"
colUp    = input.color(color.rgb(34,197,94), "Up Color",
     tooltip="Color for UpVol values, positive Delta, and bullish UpShare.",
     group=grpColors)
colDown  = input.color(color.rgb(239,68,68), "Down Color",
     tooltip="Color for DownVol values, negative Delta, and bearish UpShare.",
     group=grpColors)
colTextL = input.color(color.rgb(226,232,240), "Text (on Dark)",
     tooltip="Text color used when the chart background is dark.",
     group=grpColors)
colTextD = input.color(color.rgb(15,23,42), "Text (on Light)",
     tooltip="Text color used when the chart background is light.",
     group=grpColors)
colGuide = input.color(color.new(color.rgb(148,163,184), 70), "Guide Line",
     tooltip="Color of the faint horizontal guide lines.",
     group=grpColors)

//──────────────────────────────────────────────────────────────────────────────
// Theme helpers
//──────────────────────────────────────────────────────────────────────────────
f_luma(c) =>
    float r = color.r(c), g = color.g(c), b = color.b(c)
    0.2126*r + 0.7152*g + 0.0722*b

isDarkAuto = f_luma(chart.bg_color) < 128.0
isDark     = themeMode == "Dark" ? true : themeMode == "Light" ? false : isDarkAuto
txtColor   = isDark ? colTextL : colTextD

//──────────────────────────────────────────────────────────────────────────────
// History mode auto
//──────────────────────────────────────────────────────────────────────────────
string autoDetectedMode = historyMode
if historyMode == "Auto"
    if syminfo.type == "stock" or syminfo.type == "index"
        autoDetectedMode := "None"
    else
        autoDetectedMode := "Approx (Close vs Open)"

//──────────────────────────────────────────────────────────────────────────────
// Formatting helpers
//──────────────────────────────────────────────────────────────────────────────
f_compact(n) =>
    if compactNums
        if math.abs(n) >= 1e9
            str.tostring(n/1e9, "#.##") + "B"
        else if math.abs(n) >= 1e6
            str.tostring(n/1e6, "#.##") + "M"
        else if math.abs(n) >= 1e3
            str.tostring(n/1e3, "#.##") + "k"
        else
            str.tostring(n, "#")
    else
        str.tostring(n, "#")

f_pct1(n) => str.tostring(n, "#.#") + "%"
f_pct0(n) => str.tostring(n, "#") + "%"

f_clamp01(x) =>
    x < 0 ? 0.0 : x > 1 ? 1.0 : x

f_transp_for_strength(absPct, pctCap, tMin, tMax) =>
    stren = f_clamp01(absPct / pctCap)
    transp = tMax - (tMax - tMin) * stren
    math.round(transp)

//──────────────────────────────────────────────────────────────────────────────
// Dashboard table size
//──────────────────────────────────────────────────────────────────────────────
dashSize = size.small
if dashTextSize == "Tiny"
    dashSize := size.tiny
else if dashTextSize == "Small"
    dashSize := size.small
else if dashTextSize == "Normal"
    dashSize := size.normal
else if dashTextSize == "Large"
    dashSize := size.large
else if dashTextSize == "Huge"
    dashSize := size.huge

//──────────────────────────────────────────────────────────────────────────────
// Dashboard multi-timeframe data function
//──────────────────────────────────────────────────────────────────────────────
f_getTrend(c, o) =>
    if c > o * 1.002
        "🔼"
    else if c < o * 0.998
        "🔽"
    else
        "⏭️"

f_getVolumeData(tf) =>
    [vol, o, h, l, c] = request.security(syminfo.tickerid, tf, [volume, open, high, low, close], lookahead=barmerge.lookahead_off)
    
    upVol = 0.0
    downVol = 0.0
    
    if vol > 0
        if autoDetectedMode == "Approx (Close vs Open)"
            if c >= o
                upVol := vol
                downVol := 0.0
            else
                upVol := 0.0
                downVol := vol
        else if autoDetectedMode == "Price Action Based"
            midPrice = (h + l) / 2
            if h != l
                priceStrength = math.abs(c - midPrice) / (h - l)
                if c > midPrice
                    upVol := vol * (0.5 + priceStrength * 0.5)
                    downVol := vol * (0.5 - priceStrength * 0.5)
                else
                    upVol := vol * (0.5 - priceStrength * 0.5)
                    downVol := vol * (0.5 + priceStrength * 0.5)
            else
                upVol := c >= o ? vol : 0.0
                downVol := c < o ? vol : 0.0
        else if autoDetectedMode == "None"
            upVol := 0.0
            downVol := 0.0
        else
            if c >= o
                upVol := vol * 0.65
                downVol := vol * 0.35
            else
                upVol := vol * 0.35
                downVol := vol * 0.65
    
    upVol := math.max(upVol, 0)
    downVol := math.max(downVol, 0)
    
    delta = upVol - downVol
    totalVol = upVol + downVol
    share = totalVol > 0 ? (upVol / totalVol) * 100.0 : 50.0
    relDelta = totalVol > 0 ? (delta / totalVol) * 100.0 : 0.0
    trend = f_getTrend(c, o)
    
    [vol, upVol, downVol, delta, relDelta, share, trend]

//──────────────────────────────────────────────────────────────────────────────
// Realtime intrabar state
//──────────────────────────────────────────────────────────────────────────────
varip float lastPrice  = na
varip float lastVolume = na
varip float upVolRT    = 0.0
varip float downVolRT  = 0.0
varip int   ticks      = 0

if na(lastPrice)
    lastPrice := close
if na(lastVolume)
    lastVolume := 0.0

if barstate.isrealtime
    float dv = ticks == 0 ? volume : math.max(volume - lastVolume, 0.0)
    if   close > lastPrice
        upVolRT += dv
    else if close < lastPrice
        downVolRT += dv
    lastVolume := volume
    lastPrice  := close
    ticks += 1

if barstate.isconfirmed
    lastVolume := 0.0
    lastPrice  := close
    upVolRT    := 0.0
    downVolRT  := 0.0
    ticks      := 0

//──────────────────────────────────────────────────────────────────────────────
// Values to display per bar
//──────────────────────────────────────────────────────────────────────────────
float upDisp    = 0.0
float downDisp  = 0.0
float deltaDisp = 0.0
float shareDisp = 50.0
float volDisp   = volume

// Label size (if/else)
labelSize = size.normal
if textSize == "Tiny"
    labelSize := size.tiny
else if textSize == "Small"
    labelSize := size.small
else if textSize == "Large"
    labelSize := size.large

// Calculate values for ALL bars (realtime + historical)
if barstate.isrealtime
    if ticks > 0 and (upVolRT + downVolRT) > 0
        upDisp   := upVolRT
        downDisp := downVolRT
    else
        if volume > 0
            if autoDetectedMode == "Approx (Close vs Open)"
                if close >= open
                    upDisp := volume
                    downDisp := 0.0
                else
                    upDisp := 0.0
                    downDisp := volume
            else if autoDetectedMode == "Price Action Based"
                float midPrice = (high + low) / 2
                if high != low
                    float priceStrength = math.abs(close - midPrice) / (high - low)
                    if close > midPrice
                        upDisp   := volume * (0.5 + priceStrength * 0.5)
                        downDisp := volume * (0.5 - priceStrength * 0.5)
                    else
                        upDisp   := volume * (0.5 - priceStrength * 0.5)
                        downDisp := volume * (0.5 + priceStrength * 0.5)
                else
                    upDisp   := close >= open ? volume : 0.0
                    downDisp := close <  open ? volume : 0.0
            else
                if close >= open
                    upDisp := volume * 0.6
                    downDisp := volume * 0.4
                else
                    upDisp := volume * 0.4
                    downDisp := volume * 0.6
        else
            upDisp := 0.0
            downDisp := 0.0
            shareDisp := 50.0
else
    if volume > 0
        if autoDetectedMode == "Approx (Close vs Open)"
            if close >= open
                upDisp := volume
                downDisp := 0.0
            else
                upDisp := 0.0
                downDisp := volume
        else if autoDetectedMode == "Price Action Based"
            float midPrice = (high + low) / 2
            if high != low
                float priceStrength = math.abs(close - midPrice) / (high - low)
                if close > midPrice
                    upDisp   := volume * (0.5 + priceStrength * 0.5)
                    downDisp := volume * (0.5 - priceStrength * 0.5)
                else
                    upDisp   := volume * (0.5 - priceStrength * 0.5)
                    downDisp := volume * (0.5 + priceStrength * 0.5)
            else
                upDisp   := close >= open ? volume : 0.0
                downDisp := close <  open ? volume : 0.0
        else if autoDetectedMode == "None"
            upDisp := 0.0
            downDisp := 0.0
        else
            if close >= open
                upDisp := volume * 0.65
                downDisp := volume * 0.35
            else
                upDisp := volume * 0.35
                downDisp := volume * 0.65

// Ensure non-negative values
upDisp   := math.max(upDisp, 0)
downDisp := math.max(downDisp, 0)

// Derived values
deltaDisp       := upDisp - downDisp
float totalDisp = upDisp + downDisp
shareDisp       := totalDisp > 0 ? (upDisp/totalDisp) * 100.0 : 50.0
float relDeltaPct = totalDisp > 0 ? (deltaDisp / totalDisp) * 100.0 : 0.0

//──────────────────────────────────────────────────────────────────────────────
// Layout
//──────────────────────────────────────────────────────────────────────────────
var float yTop = 0.0
yTop := baseYOffset + (showVolume ? 4 : 3) * rowSpacing
float y1 = yTop
float y2 = yTop - rowSpacing
float y3 = yTop - rowSpacing*2
float y4 = yTop - rowSpacing*3
float y5 = yTop - rowSpacing*4

plot(drawGuides and showVolume ? y1 : na, title="Guide Volume", color=colGuide, style=plot.style_line, linewidth=1)
plot(drawGuides and showUp     ? y2 : na, title="Guide Up",     color=colGuide, style=plot.style_line, linewidth=1)
plot(drawGuides and showDown   ? y3 : na, title="Guide Down",   color=colGuide, style=plot.style_line, linewidth=1)
plot(drawGuides and showDelta  ? y4 : na, title="Guide Delta",  color=colGuide, style=plot.style_line, linewidth=1)
plot(drawGuides and showShare  ? y5 : na, title="Guide Share",  color=colGuide, style=plot.style_line, linewidth=1)

//──────────────────────────────────────────────────────────────────────────────
// Dashboard Creation
//──────────────────────────────────────────────────────────────────────────────
if enableDashboard and barstate.islast
    var table dashTable = table.new(position.top_right, 7, 8, bgcolor=color.new(isDark ? color.black : color.white, 80), 
                                   border_width = tableBorder ? 1 : 0, border_color=txtColor)
    
    // Header row
    table.cell(dashTable, 0, 0, "📅 TF", bgcolor=color.new(txtColor, 90), text_color=txtColor, text_size=dashSize)
    table.cell(dashTable, 1, 0, "📦 Vol", bgcolor=color.new(txtColor, 90), text_color=txtColor, text_size=dashSize)
    table.cell(dashTable, 2, 0, "🟢 Up", bgcolor=color.new(txtColor, 90), text_color=txtColor, text_size=dashSize)
    table.cell(dashTable, 3, 0, "🔴 Down", bgcolor=color.new(txtColor, 90), text_color=txtColor, text_size=dashSize)
    table.cell(dashTable, 4, 0, "⚖️ Δ%", bgcolor=color.new(txtColor, 90), text_color=txtColor, text_size=dashSize)
    table.cell(dashTable, 5, 0, "📊 Share", bgcolor=color.new(txtColor, 90), text_color=txtColor, text_size=dashSize)
    table.cell(dashTable, 6, 0, "📈 Trend", bgcolor=color.new(txtColor, 90), text_color=txtColor, text_size=dashSize)
    
    rowIndex = 1
    
    // M1
    if showM1
        [vol1, upVol1, downVol1, delta1, relDelta1, share1, trend1] = f_getVolumeData("1")
        bgColor1 = zebraRows and (rowIndex % 2 == 0) ? color.new(txtColor, 95) : color.new(color.white, 100)
        deltaColor1 = relDelta1 > 0 ? colUp : relDelta1 < 0 ? colDown : txtColor
        shareColor1 = share1 > 50 ? colUp : share1 < 50 ? colDown : txtColor
        
        table.cell(dashTable, 0, rowIndex, "M1", bgcolor=bgColor1, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 1, rowIndex, f_compact(vol1), bgcolor=bgColor1, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 2, rowIndex, f_compact(upVol1), bgcolor=bgColor1, text_color=colUp, text_size=dashSize)
        table.cell(dashTable, 3, rowIndex, f_compact(downVol1), bgcolor=bgColor1, text_color=colDown, text_size=dashSize)
        table.cell(dashTable, 4, rowIndex, f_pct1(relDelta1), bgcolor=bgColor1, text_color=deltaColor1, text_size=dashSize)
        table.cell(dashTable, 5, rowIndex, f_pct0(share1), bgcolor=bgColor1, text_color=shareColor1, text_size=dashSize)
        table.cell(dashTable, 6, rowIndex, trend1, bgcolor=bgColor1, text_color=txtColor, text_size=dashSize)
        rowIndex += 1
    
    // M5
    if showM5
        [vol5, upVol5, downVol5, delta5, relDelta5, share5, trend5] = f_getVolumeData("5")
        bgColor5 = zebraRows and (rowIndex % 2 == 0) ? color.new(txtColor, 95) : color.new(color.white, 100)
        deltaColor5 = relDelta5 > 0 ? colUp : relDelta5 < 0 ? colDown : txtColor
        shareColor5 = share5 > 50 ? colUp : share5 < 50 ? colDown : txtColor
        
        table.cell(dashTable, 0, rowIndex, "M5", bgcolor=bgColor5, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 1, rowIndex, f_compact(vol5), bgcolor=bgColor5, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 2, rowIndex, f_compact(upVol5), bgcolor=bgColor5, text_color=colUp, text_size=dashSize)
        table.cell(dashTable, 3, rowIndex, f_compact(downVol5), bgcolor=bgColor5, text_color=colDown, text_size=dashSize)
        table.cell(dashTable, 4, rowIndex, f_pct1(relDelta5), bgcolor=bgColor5, text_color=deltaColor5, text_size=dashSize)
        table.cell(dashTable, 5, rowIndex, f_pct0(share5), bgcolor=bgColor5, text_color=shareColor5, text_size=dashSize)
        table.cell(dashTable, 6, rowIndex, trend5, bgcolor=bgColor5, text_color=txtColor, text_size=dashSize)
        rowIndex += 1
    
    // M15
    if showM15
        [vol15, upVol15, downVol15, delta15, relDelta15, share15, trend15] = f_getVolumeData("15")
        bgColor15 = zebraRows and (rowIndex % 2 == 0) ? color.new(txtColor, 95) : color.new(color.white, 100)
        deltaColor15 = relDelta15 > 0 ? colUp : relDelta15 < 0 ? colDown : txtColor
        shareColor15 = share15 > 50 ? colUp : share15 < 50 ? colDown : txtColor
        
        table.cell(dashTable, 0, rowIndex, "M15", bgcolor=bgColor15, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 1, rowIndex, f_compact(vol15), bgcolor=bgColor15, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 2, rowIndex, f_compact(upVol15), bgcolor=bgColor15, text_color=colUp, text_size=dashSize)
        table.cell(dashTable, 3, rowIndex, f_compact(downVol15), bgcolor=bgColor15, text_color=colDown, text_size=dashSize)
        table.cell(dashTable, 4, rowIndex, f_pct1(relDelta15), bgcolor=bgColor15, text_color=deltaColor15, text_size=dashSize)
        table.cell(dashTable, 5, rowIndex, f_pct0(share15), bgcolor=bgColor15, text_color=shareColor15, text_size=dashSize)
        table.cell(dashTable, 6, rowIndex, trend15, bgcolor=bgColor15, text_color=txtColor, text_size=dashSize)
        rowIndex += 1
    
    // M30
    if showM30
        [vol30, upVol30, downVol30, delta30, relDelta30, share30, trend30] = f_getVolumeData("30")
        bgColor30 = zebraRows and (rowIndex % 2 == 0) ? color.new(txtColor, 95) : color.new(color.white, 100)
        deltaColor30 = relDelta30 > 0 ? colUp : relDelta30 < 0 ? colDown : txtColor
        shareColor30 = share30 > 50 ? colUp : share30 < 50 ? colDown : txtColor
        
        table.cell(dashTable, 0, rowIndex, "M30", bgcolor=bgColor30, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 1, rowIndex, f_compact(vol30), bgcolor=bgColor30, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 2, rowIndex, f_compact(upVol30), bgcolor=bgColor30, text_color=colUp, text_size=dashSize)
        table.cell(dashTable, 3, rowIndex, f_compact(downVol30), bgcolor=bgColor30, text_color=colDown, text_size=dashSize)
        table.cell(dashTable, 4, rowIndex, f_pct1(relDelta30), bgcolor=bgColor30, text_color=deltaColor30, text_size=dashSize)
        table.cell(dashTable, 5, rowIndex, f_pct0(share30), bgcolor=bgColor30, text_color=shareColor30, text_size=dashSize)
        table.cell(dashTable, 6, rowIndex, trend30, bgcolor=bgColor30, text_color=txtColor, text_size=dashSize)
        rowIndex += 1
    
    // H1
    if showH1
        [vol60, upVol60, downVol60, delta60, relDelta60, share60, trend60] = f_getVolumeData("60")
        bgColor60 = zebraRows and (rowIndex % 2 == 0) ? color.new(txtColor, 95) : color.new(color.white, 100)
        deltaColor60 = relDelta60 > 0 ? colUp : relDelta60 < 0 ? colDown : txtColor
        shareColor60 = share60 > 50 ? colUp : share60 < 50 ? colDown : txtColor
        
        table.cell(dashTable, 0, rowIndex, "H1", bgcolor=bgColor60, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 1, rowIndex, f_compact(vol60), bgcolor=bgColor60, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 2, rowIndex, f_compact(upVol60), bgcolor=bgColor60, text_color=colUp, text_size=dashSize)
        table.cell(dashTable, 3, rowIndex, f_compact(downVol60), bgcolor=bgColor60, text_color=colDown, text_size=dashSize)
        table.cell(dashTable, 4, rowIndex, f_pct1(relDelta60), bgcolor=bgColor60, text_color=deltaColor60, text_size=dashSize)
        table.cell(dashTable, 5, rowIndex, f_pct0(share60), bgcolor=bgColor60, text_color=shareColor60, text_size=dashSize)
        table.cell(dashTable, 6, rowIndex, trend60, bgcolor=bgColor60, text_color=txtColor, text_size=dashSize)
        rowIndex += 1
    
    // H4
    if showH4
        [vol240, upVol240, downVol240, delta240, relDelta240, share240, trend240] = f_getVolumeData("240")
        bgColor240 = zebraRows and (rowIndex % 2 == 0) ? color.new(txtColor, 95) : color.new(color.white, 100)
        deltaColor240 = relDelta240 > 0 ? colUp : relDelta240 < 0 ? colDown : txtColor
        shareColor240 = share240 > 50 ? colUp : share240 < 50 ? colDown : txtColor
        
        table.cell(dashTable, 0, rowIndex, "H4", bgcolor=bgColor240, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 1, rowIndex, f_compact(vol240), bgcolor=bgColor240, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 2, rowIndex, f_compact(upVol240), bgcolor=bgColor240, text_color=colUp, text_size=dashSize)
        table.cell(dashTable, 3, rowIndex, f_compact(downVol240), bgcolor=bgColor240, text_color=colDown, text_size=dashSize)
        table.cell(dashTable, 4, rowIndex, f_pct1(relDelta240), bgcolor=bgColor240, text_color=deltaColor240, text_size=dashSize)
        table.cell(dashTable, 5, rowIndex, f_pct0(share240), bgcolor=bgColor240, text_color=shareColor240, text_size=dashSize)
        table.cell(dashTable, 6, rowIndex, trend240, bgcolor=bgColor240, text_color=txtColor, text_size=dashSize)
        rowIndex += 1
    
    // D1
    if showD1
        [vol1D, upVol1D, downVol1D, delta1D, relDelta1D, share1D, trend1D] = f_getVolumeData("1D")
        bgColor1D = zebraRows and (rowIndex % 2 == 0) ? color.new(txtColor, 95) : color.new(color.white, 100)
        deltaColor1D = relDelta1D > 0 ? colUp : relDelta1D < 0 ? colDown : txtColor
        shareColor1D = share1D > 50 ? colUp : share1D < 50 ? colDown : txtColor
        
        table.cell(dashTable, 0, rowIndex, "D1", bgcolor=bgColor1D, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 1, rowIndex, f_compact(vol1D), bgcolor=bgColor1D, text_color=txtColor, text_size=dashSize)
        table.cell(dashTable, 2, rowIndex, f_compact(upVol1D), bgcolor=bgColor1D, text_color=colUp, text_size=dashSize)
        table.cell(dashTable, 3, rowIndex, f_compact(downVol1D), bgcolor=bgColor1D, text_color=colDown, text_size=dashSize)
        table.cell(dashTable, 4, rowIndex, f_pct1(relDelta1D), bgcolor=bgColor1D, text_color=deltaColor1D, text_size=dashSize)
        table.cell(dashTable, 5, rowIndex, f_pct0(share1D), bgcolor=bgColor1D, text_color=shareColor1D, text_size=dashSize)
        table.cell(dashTable, 6, rowIndex, trend1D, bgcolor=bgColor1D, text_color=txtColor, text_size=dashSize)

//──────────────────────────────────────────────────────────────────────────────
// Label management with windowed pruning
//──────────────────────────────────────────────────────────────────────────────
var label[] arrVol   = array.new<label>()
var label[] arrUp    = array.new<label>()
var label[] arrDown  = array.new<label>()
var label[] arrDelta = array.new<label>()
var label[] arrShare = array.new<label>()

f_prune(arr) =>
    int cutoff = bar_index - (limitBars - 1)
    for i = array.size(arr) - 1 to 0
        label L = array.get(arr, i)
        if label.get_x(L) < cutoff
            label.delete(L)
            array.remove(arr, i)

bool nthPass  = (bar_index % labelStep == 0)
bool canDraw  = nthPass

string volTxt  = f_compact(volDisp)
string upTxt   = volume == 0 ? "↑ 0" : "↑ " + f_compact(upDisp)
string downTxt = volume == 0 ? "↓ 0" : "↓ " + f_compact(downDisp)

string deltaTxt = ""
if volume == 0
    deltaTxt := "Δ 0"
else
    if deltaMode == "Absolute"
        deltaTxt := "Δ " + f_compact(deltaDisp)
    else if deltaMode == "Relative"
        deltaTxt := "Δ " + f_pct1(relDeltaPct)
    else
        deltaTxt := "Δ " + f_compact(deltaDisp) + "\n(" + f_pct0(relDeltaPct) + ")"

string shareTxt = volume == 0 ? "⇅ --%" : "⇅ " + f_pct1(shareDisp)
if volume > 0
    if shareDisp > 65
        shareTxt := "▲ " + shareTxt
    else if shareDisp < 35
        shareTxt := "▼ " + shareTxt

color baseDeltaCol = deltaDisp > 0 ? colUp : deltaDisp < 0 ? colDown : txtColor
int   deltaTransp  = useContextColors ? f_transp_for_strength(math.abs(relDeltaPct), ctxMaxPctDelta, ctxMinTransp, ctxMaxTransp) : 0
color deltaCol     = color.new(baseDeltaCol, deltaTransp)

bool  bullShare    = shareDisp > 50
color baseShareCol = volume == 0 ? txtColor : (bullShare ? colUp : colDown)
int   shareTransp  = useContextColors ? f_transp_for_strength(math.abs(shareDisp - 50.0), ctxMaxPctShare, ctxMinTransp, ctxMaxTransp) : 0
color shareCol     = color.new(baseShareCol, shareTransp)

// Create labels only if allowed, then prune outside-window ones
if showVolume and canDraw
    label l = label.new(bar_index, y1, volTxt, style=label.style_none, textcolor=txtColor, textalign=text.align_center, size=labelSize)
    array.push(arrVol, l)
    f_prune(arrVol)

if showUp and canDraw
    label l = label.new(bar_index, y2, upTxt, style=label.style_none, textcolor=colUp, textalign=text.align_center, size=labelSize)
    array.push(arrUp, l)
    f_prune(arrUp)

if showDown and canDraw
    label l = label.new(bar_index, y3, downTxt, style=label.style_none, textcolor=colDown, textalign=text.align_center, size=labelSize)
    array.push(arrDown, l)
    f_prune(arrDown)

if showDelta and canDraw
    label l = label.new(bar_index, y4, deltaTxt, style=label.style_none, textcolor=deltaCol, textalign=text.align_center, size=labelSize)
    array.push(arrDelta, l)
    f_prune(arrDelta)

if showShare and canDraw
    label l = label.new(bar_index, y5, shareTxt, style=label.style_none, textcolor=shareCol, textalign=text.align_center, size=labelSize)
    array.push(arrShare, l)
    f_prune(arrShare)

//──────────────────────────────────────────────────────────────────────────────
// Alerts
//──────────────────────────────────────────────────────────────────────────────
grpAlerts = "Alerts"
deltaThresh = input.float(0.0, "Delta Threshold (abs)", minval=0.0,
     tooltip="Trigger when |Δ| exceeds this ABSOLUTE value (units = volume).",
     group=grpAlerts)
shareGT = input.float(60.0, "UpShare >", minval=0, maxval=100,
     tooltip="Alert when UpShare% is ABOVE this bullish threshold.",
     group=grpAlerts)
shareLT = input.float(40.0, "UpShare <", minval=0, maxval=100,
     tooltip="Alert when UpShare% is BELOW this bearish threshold.",
     group=grpAlerts)
relDeltaAlertOn = input.bool(false, "Enable Δ% Alert",
     tooltip="If enabled, also evaluate Δ% thresholds on every bar.",
     group=grpAlerts)
relDeltaGT = input.float(30.0, "Δ% > +", minval=0, maxval=100,
     tooltip="Alert when relative Delta (Δ%) is ABOVE this positive level.",
     group=grpAlerts)
relDeltaLT = input.float(-30.0, "Δ% < −", minval=-100, maxval=0,
     tooltip="Alert when relative Delta (Δ%) is BELOW this negative level.",
     group=grpAlerts)

float deltaAbs = math.abs(deltaDisp)
bool condDelta   = deltaThresh > 0 and deltaAbs > deltaThresh
bool condShareGT = shareDisp > shareGT
bool condShareLT = shareDisp < shareLT
bool condRelGT   = relDeltaAlertOn and relDeltaPct > relDeltaGT
bool condRelLT   = relDeltaAlertOn and relDeltaPct < relDeltaLT

alertcondition(condDelta,   title="Delta exceeds threshold",  message="IVDG v1: |Delta| exceeded the user-defined threshold.")
alertcondition(condShareGT, title="UpShare above threshold",  message="IVDG v1: UpShare is above the bullish threshold.")
alertcondition(condShareLT, title="UpShare below threshold",  message="IVDG v1: UpShare is below the bearish threshold.")
alertcondition(condRelGT,   title="Relative Delta above +X%", message="IVDG v1: Δ% is above the bullish threshold.")
alertcondition(condRelLT,   title="Relative Delta below −X%", message="IVDG v1: Δ% is below the bearish threshold.")

