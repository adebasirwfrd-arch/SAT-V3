10. methode Big Candle
hints:Big Candles, most of the times, indicate actions by market makers . Also the candle high and low can be thought of as liquidity zones.

Source code
// This Pine Script® code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © brahma

//@version=5
indicator("Big Candle Up/Down Alert", overlay=true)

// Set your threshold for big candle (% move from low to high)
threshold = 1.2*ta.atr(14) / close * 100  // adaptive threshold

// Calculate % range of current candle
candleSize = (high - low) / low * 100

// Define big up and big down candles
bigUp = candleSize > threshold and close > open
bigDown = candleSize > threshold and close < open

// Plot label below bar for up and down separately
plotshape(bigUp, title="Big Up Candle", location=location.belowbar, style=shape.labelup,
     text="BIG↑", textcolor=color.white, size=size.small, color=color.green)

plotshape(bigDown, title="Big Down Candle", location=location.belowbar, style=shape.labelup,
     text="BIG↓", textcolor=color.white, size=size.small, color=color.red)
     // Optional alert conditions
alertcondition(bigUp, title="Big Up Candle Alert", message="Big UP candle on {{ticker}}")
alertcondition(bigDown, title="Big Down Candle Alert", message="Big DOWN candle on {{ticker}}")

11. Methode CRT + PO3 Range Theory
Hints:What It Does
Accumulation Phase: On each higher‐timeframe bar (e.g. 2-hour), it draws a shaded zone where price is hanging out. That’s when we assume “big players” are quietly building positions.

Manipulation Phase: If price briefly pokes above or below that zone but then slips back inside, it marks that wick as a shake-out.

Distribution Phase: When price finally closes cleanly outside the zone, it draws another shaded area and drops a “Distribution” label plus a big LONG or SHORT arrow on that bar.

You can tweak it so it only shows signals when a bar closes (no more weird flashing mid-bar), or even allow “direct” Distribution on a clean breakout without waiting for a fake wick first.

How to Set It Up
Add the script from your Indicators list.

Pick your HTF (I like 2-hour or 4-hour).

Turn “Show Zone Labels” on or off—these are the little “Accumulation/Manipulation/Distribution” tags.

Turn “Show Entry Signals” on to get the big LONG/SHORT arrows.

If you hate flicker, check “Show signals only at bar close.”

If you want to catch a swift breakout (no fake-out needed), check “Allow direct Distribution on clean breakout.”

There are also sliders for zone colors, transparency, label size, and how far above/below the bars the labels sit.

Why It’s Still a Beta
I’m not a CRT/PO3 guru—this is more of a hobby project and a little facination for this strategy.

There might be edge cases where it misses a shake-out or flags a Distribution too early.

I take no responsibility for your trades—please only run it on a demo account until we’ve worked out the quirks.

Source code
//@version=5
indicator("CRT + PO3 Range Theory", overlay=true, explicit_plot_zorder=true)

// Inputs (defaults set to match your GUI screenshot)
htf                    = input.timeframe("120",    "HTF for CRT Range")                                  // 2 hours
showZoneText           = input.bool(false,         "Show Zone Labels")                                    // off by default
showEntries            = input.bool(true,          "Show Entry Signals")                                  // on by default
signalOnClose          = input.bool(true,          "Show signals only at bar close")                      // on by default
allowDirectDist        = input.bool(false,         "Allow direct Distribution on clean breakout")         // off by default
distBars               = input.int(1,              "Distribution Bar Duration (bars)", minval=1)         // default 1
zoneAccumBg            = input.color(color.gray,   "Accumulation Zone Color")                            // gray
zoneManipBg            = input.color(color.red,    "Manipulation Zone Color")                            // red
zoneDistBg             = input.color(color.green,  "Distribution Zone Color")                           // green
zoneBgTransparency     = input.int(70,             "Zone Transparency (%)", minval=0, maxval=100)       // default 70%
accumTxtColor          = input.color(color.aqua,   "Accumulation Text Color")                            // cyan
manipTxtColor          = input.color(color.red,    "Manipulation Text Color")                            // red
distTxtColor           = input.color(color.green,  "Distribution Text Color")                            // green
zoneLabelSize          = input.string("tiny",      "Zone Label Size",   options=["tiny","small","normal","large","huge"]) // tiny
zoneLabelOffsetTicks   = input.int(150,            "Zone Label Offset (ticks)", minval=1)               // default 150
distBarOffsetTicks     = input.int(850,            "Distribution Label Offset (ticks)", minval=1)       // default 850
entryLongOffsetTicks   = input.int(1500,           "Entry LONG Offset (ticks)", minval=0)               // default 1500
entryShortOffsetTicks  = input.int(1500,           "Entry SHORT Offset (ticks)", minval=0)              // default 1500
distBarColor           = input.color(color.green,  "Distribution Bar Label Color")                      // green
entryLongColor         = input.color(color.green,  "Entry LONG Label Color")                            // green
entryShortColor        = input.color(color.red,    "Entry SHORT Label Color")                           // red
entryLabelSize         = input.string("normal",    "Entry Label Size",   options=["tiny","small","normal","large","huge"]) // normal

// Helpers
sizeFrom(s)            => s=="tiny"?size.tiny:s=="small"?size.small:s=="normal"?size.normal:s=="large"?size.large:size.huge
zoneLblSizeConst       = sizeFrom(zoneLabelSize)
entryLblSizeConst      = sizeFrom(entryLabelSize)
tick                   = syminfo.mintick

// HTF Data (single line)
[htfHigh, htfLow, _, _, htfTime] = request.security(syminfo.tickerid, htf, [high, low, open, close, time], ignore_invalid_symbol=true)

// Range variables
var float rangeHigh = na
var float rangeLow  = na

// Detect false‐break and breakout
manipUp  = high > rangeHigh  and close < rangeHigh
manipDn  = low  < rangeLow   and close > rangeLow
directUp = high > rangeHigh  and close > rangeHigh
directDn = low  < rangeLow   and close < rangeLow
distUp   = (manipUp[1] and close > rangeHigh) or (allowDirectDist and directUp)
distDn   = (manipDn[1] and close < rangeLow)  or (allowDirectDist and directDn)

// Phase tracking
var string phase   = "accum"
var float  zoneY   = na
var label  zoneLabel = na

// On new HTF bar → Accumulation
if ta.change(htfTime)
    rangeHigh := htfHigh
    rangeLow  := htfLow
    phase      := "accum"
    zoneY      := htfHigh + tick * zoneLabelOffsetTicks
    if showZoneText
        zoneLabel := label.new(bar_index, zoneY, "Accumulation", yloc=yloc.price, style=label.style_label_down, size=zoneLblSizeConst, color=color.new(color.white,0), textcolor=accumTxtColor)

// First Manipulation bar
if phase=="accum" and (manipUp or manipDn)
    phase := "manip"
    if showZoneText
        label.new(bar_index, zoneY, "Manipulation", yloc=yloc.price, style=label.style_label_down, size=zoneLblSizeConst, color=color.new(color.white,0), textcolor=manipTxtColor)

// First Distribution bar
if phase=="manip" and (distUp or distDn)
    phase := "dist"
    if showZoneText
        label.new(bar_index, zoneY, "Distribution", yloc=yloc.price, style=label.style_label_down, size=zoneLblSizeConst, color=color.new(color.white,0), textcolor=distTxtColor)

// Plot CRT range & background
plot(rangeHigh, "CRT High", color=color.red, linewidth=2)
plot(rangeLow,  "CRT Low",  color=color.green, linewidth=2)
bgcolor(phase=="accum"?color.new(zoneAccumBg,zoneBgTransparency):phase=="manip"?color.new(zoneManipBg,zoneBgTransparency):color.new(zoneDistBg,zoneBgTransparency))

// Distribution & Entry on breakout-up
if showEntries and distUp and (not signalOnClose or barstate.isconfirmed)
    label.new(bar_index, low - tick * distBarOffsetTicks,   "Distribution", yloc=yloc.price, style=label.style_label_up,   size=size.large,       color=color.new(color.white,0), textcolor=distBarColor)
    label.new(bar_index, low - tick * entryLongOffsetTicks, "LONG",         yloc=yloc.price, style=label.style_label_up,   size=entryLblSizeConst, color=color.new(color.white,0), textcolor=entryLongColor)

// Distribution & Entry on breakout-down
if showEntries and distDn and (not signalOnClose or barstate.isconfirmed)
    label.new(bar_index, high + tick * distBarOffsetTicks,  "Distribution", yloc=yloc.price, style=label.style_label_down, size=size.large,       color=color.new(color.white,0), textcolor=distBarColor)
    label.new(bar_index, high + tick * entryShortOffsetTicks,"SHORT",        yloc=yloc.price, style=label.style_label_down, size=entryLblSizeConst, color=color.new(color.white,0), textcolor=entryShortColor)

Methode 12:Internal Candle Strength [LuxAlgo]
hints:The Internal Candle Strength tool allows traders to divide each chart bar into multiple rows of custom size and inspect the strength of the lower timeframes trends located within each row.

This tool effectively helps traders in identifying the power dynamic between bulls and bears within multiple areas within each bar, providing the ability to conduct LTF analysis.

🔶 USAGE

The strength displayed within each row ranges from 0% to 100%, with 0% being the most bearish and 100% being the most bullish.

Traders should be aware of the extreme probabilities located at the higher/lower end of the bars, as this can signal a change in strength and price direction.
Traders can select the lower timeframe to pull the data from or the row size in the scale of the chart. Selecting a lower timeframe will provide more data to evaluate an area's strength.

Do note that only a timeframe lower than the chart timeframe should be selected.

🔹 Row Size

Selecting a smaller row size will increase the number of rows per bar, allowing for a more detailed analysis. A lower value will also generally mean that less data will be considered when calculating the strength of a specific area.

As we can see on the chart above (all BTCUSD 30m), by selecting a different row size, traders can control how many rows are displayed per bar.

🔶 SETTINGS

Timeframe: Lower timeframe used to calculate the candle strength.
Row Size: Size of each row on the chart scale, expressed as a fraction of the candle range.
14 Jul 2025
Catatan Rilis
- Improved row construction
- Added recommended row size dashboard
Source code
// This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) https://creativecommons.org/licenses/by-nc-sa/4.0/
// © LuxAlgo

//@version=6
indicator('Internal Candle Strength [LuxAlgo]', 'LuxAlgo - Internal Candle Strength', overlay=true, max_lines_count = 500, max_boxes_count = 500)
//---------------------------------------------------------------------------------------------------------------------}
//CONSTANTS & STRINGS & INPUTS
//---------------------------------------------------------------------------------------------------------------------{
timeframeInput  = input.timeframe(  '1',  'Timeframe')
sizeInput       = input(            20.,  'Row Size', inline = 'size')
autoInput       = input.bool(       true, 'Auto',     inline = 'size')

//---------------------------------------------------------------------------------------------------------------------}
//DATA STRUCTURES & VARIABLES
//---------------------------------------------------------------------------------------------------------------------{
var table t_able = table.new(position.bottom_right,2,2
     , bgcolor      = #1e222d
     , border_color = #373a46
     , border_width = 1
     , frame_color  = #373a46
     , frame_width  = 1)

//---------------------------------------------------------------------------------------------------------------------}
//USER-DEFINED FUNCTIONS
//---------------------------------------------------------------------------------------------------------------------{
ohlc()=> [open, high, low, close]

//---------------------------------------------------------------------------------------------------------------------}
//MUTABLE VARIABLES & EXECUTION
//---------------------------------------------------------------------------------------------------------------------{
volatility    = math.round_to_mintick(0.1 * ta.atr(200))
parsedSize    = autoInput ? volatility : sizeInput
n             = bar_index
idx           = math.max(math.round((high - low) / parsedSize), 1)
[o, h, l, c]  = request.security_lower_tf(syminfo.tickerid, timeframeInput, ohlc())

min           = low
max           = low
float avg     = na 
color css     = na

for i = 0 to idx-1
    max += (high - low) / idx
    num = array.new<float>()
    den = array.new<float>()

    for [index, value] in o
        if array.get(h, index) > min and array.get(l, index) < max
            diff = array.get(c, index) - array.get(o, index)

            array.push(num, diff)
            array.push(den, math.abs(diff))

    strength  = 50 * (array.sum(num) / array.sum(den)) + 50
    css       := color.from_gradient(strength, 0, 100, color.red, color.teal)

    box.new(n, max, n+1, min
      , text = str.tostring(strength, format.percent)
      , text_color = css
      , bgcolor = color.new(#5d606b, 80)
      , border_color = na)

    line.new(n, min, n+1, min, color = css)    
    
    min := max

line.new(n, min, n+1, min, color = css)

plotcandle(open, math.max(close, open), math.min(close, open), open
  , bordercolor = #00000000
  , color = #00000000
  , wickcolor = close > open ? color.teal : color.red)

if barstate.islast
    t_able.cell(0,0,'Current Row Size',text_color = color.new(color.white,50))
    t_able.cell(0,1,'Optimal Row Size',text_color = color.new(color.white,50))
    t_able.cell(1,0,str.tostring(parsedSize),text_color = color.new(color.white,50))
    t_able.cell(1,1,str.tostring(volatility),text_color = color.new(color.white,50))
    
//---------------------------------------------------------------------------------------------------------------------}

13. Methode Smart Bar Counter with Alerts
hints:🚀 Smart Bar Counter with Alerts 🚀

-----------------------------------------------------
Overview
-----------------------------------------------------
Ever wanted to count a specific number of bars from a key point on your chart—such as after a Break of Structure (BOS), the start of a new trading session, or from any point of interest—without having to stare at the screen?

This "Smart Bar Counter" indicator was created to solve this exact problem. It's a simple yet powerful tool that allows you to define a custom "Start Point" and a "Target Bar Count." Once the target count is reached, it can trigger an Alert to notify you immediately.


-----------------------------------------------------
Key Features
-----------------------------------------------------
• Manual Start Point: Precisely select the date and time from which you want the count to begin, offering maximum flexibility in your analysis.
• Custom Bar Target: Define exactly how many bars you want to count, whether it's 50, 100, or 200 bars.
• On-Chart Display: A running count is displayed on each bar after the start time, allowing you to visually track the progress.
• Automatic Alerts: Set up alerts to be notified via TradingView's various channels (pop-up, mobile app, email) once the target count is reached.


-----------------------------------------------------
How to Use
-----------------------------------------------------
1. Add this indicator to your chart.

2. Go to the indicator's Settings (Gear Icon ⚙️).
- Select Start Time: Set the date and time you wish to begin counting.
- Number of Bars to Count: Input your target number.

3. Set up the Alert ([u]Very Important![/u]).
- Right-click on the chart > Select "Add alert."
- In the "Condition" dropdown, select this indicator: Smart Bar Counter with Alerts.
- In the next dropdown, choose the available alert condition.
- Set "Options" to Once Per Bar Close.
- Choose your desired notification methods under "Alert Actions."
- Click "Create."


-----------------------------------------------------
Use Cases
-----------------------------------------------------
• Post-Event Analysis: Count bars after a key event like a Break of Structure (BOS) or Change of Character (CHoCH) to observe subsequent price action.
• Time-based Analysis: Use it to count bars after a market open for a specific session (e.g., London, New York).
• Strategy Backtesting: Useful for testing trading rules that are based on time or a specific number of bars.

Source Code
translate to english first 
//@version=5
indicator("Smart Bar Counter with Alerts", overlay=true)

// --- ส่วนตั้งค่า Input จากผู้ใช้ ---
i_startTime = input.time(timestamp("07 Jun 2025 7:00 +0700"), title="เลือกเวลาเริ่มต้นนับ")
i_barTarget = input.int(2, title="จำนวนแท่งเทียนที่ต้องการนับ", minval=1)
i_showAlerts = input.bool(true, title="เปิด/ปิด การแจ้งเตือน")

// --- ส่วนประมวลผลและนับแท่งเทียน ---
var int barCount = 0 // ใช้ 'var' เพื่อให้ค่า barCount ถูกเก็บไว้ข้ามแท่งเทียน

// เริ่มนับเมื่อเวลาของแท่งเทียนปัจจุบัน >= เวลาที่ตั้งค่าไว้
if (time >= i_startTime)
    barCount += 1
else
    barCount := 0 // รีเซ็ตตัวนับถ้ายังไม่ถึงเวลาเริ่มต้น

// --- ส่วนแสดงผลบนกราฟ ---
// แสดงตัวเลขนับบนแท่งเทียนเมื่อเริ่มนับแล้ว
if (barCount > 0)
    label.new(bar_index, high, text=str.tostring(barCount),
              color=color.new(color.blue, 70),
              textcolor=color.white,
              style=label.style_label_down,
              yloc=yloc.abovebar)

// --- ส่วนเงื่อนไขและการแจ้งเตือน ---
alertCondition = (barCount == i_barTarget)

if (alertCondition and i_showAlerts)
    alert("ครบจำนวน " + str.tostring(i_barTarget) + " แท่งเทียนแล้ว!", alert.freq_once_per_bar)

14. Methode LRC
hints:LRC (Linear Regression Candle) [SpUn]

Overview
The LRC (Linear Regression Candle) indicator applies linear regression to the open, high, low, and close prices, creating smoothed "candles" that help filter market noise. It provides trend-confirmation signals and highlights potential reversal points based on regression crossovers.

Key Features
Smoothed Candles: Uses linear regression to calculate synthetic OHLC values, reducing noise.

Multi-Timeframe Support: Optional higher timeframe analysis for better trend confirmation.

Visual Signals: Color-coded candles and labels highlight bullish/bearish control zones.

Customizable Settings: Adjustable regression length, colors, and timeframe options.

How to Use
Signals & Interpretation

🟢 Bullish Signal (BUY): When the regression open crosses above the regression close (green candle).

🔴 Bearish Signal (SELL): When the regression open crosses below the regression close (red candle).

Control Zones:

Strong Bullish (Controlbull): Confirmed uptrend (bright green).

Bullish (Bull): Regular uptrend (light green).

Strong Bearish (Controlbear): Confirmed downtrend (dark red).

Bearish (Bear): Regular downtrend (orange).

Neutral (Gray): No clear trend.

Recommended Settings
Linear Regression Length: Default 8 (adjust for sensitivity).

Timeframe: Default current chart, but can switch to higher timeframes (e.g., 1D, 1W).

Bar Colors: Toggle on/off for visual clarity.

Labels: Displays "Control" markers at key reversal points.

Example Use Cases
Trend Confirmation: Use higher timeframe LRC to validate the primary trend.

Reversal Signals: Watch for BUY/SELL crossovers with strong color confirmation.

Noise Reduction: Helps avoid false breakouts in choppy markets.

Source code
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
//@Spunsen
//@version=5

indicator('LRC', 'LRCandle [SpUn]', true)
bool Alternativetimeframe = input.bool(false)
string alternative = input.string('1D', 'Timeframe', options = ['3','5','15','30','60','120','180','240','480','720','960','1D','2D','3D','4D','5D','1W','1M','3M'])
linreg_length      = input.int(title='Linear Regression Length', minval=1, maxval=200, defval=8)
BarColors          = input.bool(true)
Labels             = input.bool(false)
lopen              = ta.linreg(open,  linreg_length, 0) 
lhigh              = ta.linreg(high,  linreg_length, 0) 
llow               = ta.linreg(low,   linreg_length, 0) 
lclose             = ta.linreg(close, linreg_length, 0) 

string timeframe = switch 
    Alternativetimeframe => alternative
    timeframe.period == "1"   => "30"
    timeframe.period == "3"   => "60" 
    timeframe.period == "5"   => "120"
    timeframe.period == "15"  => "240"
    timeframe.period == "30"  => "480"
    timeframe.period == "45"  => "480"
    timeframe.period == "60"  => "720"
    timeframe.period == "120" => "720"
    timeframe.period == "180" => "D"
    timeframe.period == "240" => "D"  
    timeframe.period == "D"   => "W"  
    timeframe.period == "W"   => "M"  
    timeframe.period == "M"   => "3M"
    => alternative

[L_open, L_high, L_low, L_close] = request.security( syminfo.tickerid,timeframe, [lopen, lhigh, llow, lclose],barmerge.gaps_off ,barmerge.lookahead_on)

SEL = ta.cross(L_open, L_close)[1] and L_open >= L_close
BUY = ta.cross(L_open, L_close)[1] and L_open <= L_close

Controlbull  = input.color(#1b5e20) 
Bull         = input.color(#81c784)
Controlbear  = input.color(#801922)
Bear         = input.color(#f57c00)
Neutral      = input.color(#787b86)

color_ca = L_open < L_close and BUY ? Controlbull : L_open < L_close ? Bull: L_open > L_close and SEL? Controlbear: L_open > L_close ? Bear: Neutral

plotshape(not Labels ? na : (SEL ? L_high : na), style=shape.labeldown, color=color.new(#e0b29c,100), location=location.absolute, textcolor=color.black, text='ᐍ\nControl')
plotshape(not Labels ? na : (BUY ? L_low : na) , style=shape.labelup  , color=color.new(#e0b29c,100) , location=location.absolute, textcolor=color.black, text='ᐏ\nControl')
barcolor (not BarColors ? na : color_ca)

15. Methode Candle Breakout Oscillator [LuxAlgo]

hints:The Candle Breakout Oscillator tool allows traders to identify the strength and weakness of the three main market states: bullish, bearish, and choppy.

Know who controls the market at any given moment with an oscillator display with values ranging from 0 to 100 for the three main plots and upper and lower thresholds of 80 and 20 by default.

🔶 USAGE
The Candle Breakout Oscillator represents the three main market states, with values ranging from 0 to 100. By default, the upper and lower thresholds are set at 80 and 20, and when a value exceeds these thresholds, a colored area is displayed for the trader's convenience.

This tool is based on pure price action breakouts. In this context, we understand a breakout as a close above the last candle's high or low, which is representative of market strength. All other close positions in relation to the last candle's limits are considered weakness.

So, when the bullish plot (in green) is at the top of the oscillator (values above 80), it means that the bullish breakouts (close below the last candle low) are at their maximum value over the calculation window, indicating an uptrend. The same interpretation can be made for the bearish plot (in red), indicating a downtrend when high.

On the other hand, weakness is indicated when values are below the lower threshold (20), indicating that breakouts are at their minimum over the last 100 candles. Below are some examples of the possible main interpretations:

There are three main things to look for in this oscillator:
Value reaches extreme
Value leaves extreme
Bullish/Bearish crossovers


As we can see on the chart, before the first crossover happens the bears come out of strength (top) and the bulls come out of weakness (bottom), then after the crossover the bulls reach strength (top) and the bears weakness (bottom), this process is repeated in reverse for the second crossover.
The other main feature of the oscillator is its ability to identify periods of sideways trends when the sideways values have upper readings above 80, and trending behavior when the sideways values have lower readings below 20. As we just saw in the case of bullish vs. bearish, sideways values signal a change in behavior when reaching or leaving the extremes of the oscillator.

🔶 DETAILS

🔹 Data Smoothing

The tool offers up to 10 different smoothing methods. In the chart above, we can see the raw data (smoothing: None) and the RMA, TEMA, or Hull moving averages.

🔹 Data Weighting
Users can add different weighting methods to the data. As we can see in the image above, users can choose between None, Volume, or Price (as in Price Delta for each breakout).

🔶 SETTINGS

Window: Execution window, 100 candles by default


🔹 Data

Smoothing Method: Choose between none or ten moving averages
Smoothing Length: Length for the moving average
Weighting Method: Choose between None, Volume, or Price


🔹 Thresholds

Top: 80 by default
Bottom: 20 by default
Skrip open-source

Dengan semangat TradingView yang sesungguhnya, pembuat skrip ini telah menjadikannya sebagai sumber terbuka, sehingga para trader dapat meninjau dan memverifikasi fungsinya. Salut untuk penulisnya! Meskipun Anda dapat menggunakannya secara gratis, perlu diingat bahwa penerbitan ulang kode ini tunduk pada Tata Tertib kami.


LuxAlgo

Ikuti
Get exclusive indicators & AI trading strategies: luxalgo.com

Free 150k+ community: discord.gg/lux

All content provided by LuxAlgo is for informational & educational purposes only. Past performance does not guarantee future results.
Juga di:
Pernyataan Penyangkalan
Informasi dan publikasi ini tidak dimaksudkan, dan bukan merupakan, saran atau rekomendasi keuangan, investasi, trading, atau jenis lainnya yang diberikan atau didukung oleh TradingView. Baca selengkapnya di Ketentuan Penggunaan.

Source code
// This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) https://creativecommons.org/licenses/by-nc-sa/4.0/
// © LuxAlgo

//@version=6
indicator('Candle Breakout Oscillator [LuxAlgo]','LuxAlgo - Candle Breakout Oscillator')
//---------------------------------------------------------------------------------------------------------------------}
//CONSTANTS & STRINGS & INPUTS
//---------------------------------------------------------------------------------------------------------------------{
GREEN                   = #089981
RED                     = #F23645

bullColor               = color.new(GREEN,50)
bearColor               = color.new(RED,50)
sidewaysColor           = color.new(color.silver,50)

NONE                    = 'None'
VOLUME                  = 'Volume'
PRICE                   = 'Price'
RMA                     = 'RMA'
SMA                     = 'SMA'
TMA                     = 'TMA'
EMA                     = 'EMA'
DEMA                    = 'DEMA'
TEMA                    = 'TEMA'
HMA                     = 'HMA'
WMA                     = 'WMA'
SWMA                    = 'SWMA'
VWMA                    = 'VWMA'

DATA_GROUP              = 'DATA'
THRESHOLDS_GROUP        = 'THRESHOLDS'

windowInput             = input.int(    100,    'Window')

smoothingInput          = input.string( RMA,    'Smoothing Method', group = DATA_GROUP,         options=[NONE,RMA,SMA,TMA,EMA,DEMA,TEMA,HMA,WMA,SWMA,VWMA])
smoothingLengthInput    = input.int(    2,      'Smoothing Length', group = DATA_GROUP,         step = 1,   minval = 1, maxval = 100)
weightTypeInput         = input.string( NONE,   'Weighting Method', group = DATA_GROUP,         options=[NONE,VOLUME,PRICE])

topThresholdInput       = input.int(    80,     'Top',              group = THRESHOLDS_GROUP,   minval = 50,maxval = 100)
bottomThresholdInput    = input.int(    20,     'Bottom',           group = THRESHOLDS_GROUP,   minval = 0, maxval = 50)

//---------------------------------------------------------------------------------------------------------------------}
//DATA STRUCTURES & VARIABLES
//---------------------------------------------------------------------------------------------------------------------{
var array<float> bulls          = array.new<float>()
var array<float> bears          = array.new<float>()
var array<float> sideways       = array.new<float>()
var array<float> volumes        = array.new<float>()
var array<float> bullWeights    = array.new<float>()
var array<float> bearWeights    = array.new<float>()
var array<float> sidewayWeights = array.new<float>()

//---------------------------------------------------------------------------------------------------------------------}
//USER-DEFINED FUNCTIONS
//---------------------------------------------------------------------------------------------------------------------{
parseWeight(float weight) => weightTypeInput != NONE ? (weightTypeInput == VOLUME ? volume : weight) : 1

addData(array<float> a_rray, float value, int size, float weight) =>
    a_rray.push(value * parseWeight(weight))
    if a_rray.size() > size
        a_rray.shift()

addWeight(array<float> a_rray, float value, int size) =>
    a_rray.push(value)
    if a_rray.size() > size
        a_rray.shift()

normalize(array<float> a_rray, int window, array<float> weights) =>
    value = weightTypeInput != NONE ? a_rray.sum() / (weightTypeInput == VOLUME ? volumes.sum() : weights.sum()) : a_rray.sum()
    100 * (value - ta.lowest(value, window)) / (ta.highest(value, window) - ta.lowest(value, window))

smooth(float data) =>
    switch smoothingInput
        RMA     => ta.rma(data,smoothingLengthInput)
        SMA     => ta.sma(data,smoothingLengthInput)
        TMA     => ta.sma(ta.sma(data,smoothingLengthInput),smoothingLengthInput)
        EMA     => ta.ema(data,smoothingLengthInput)
        DEMA    => 2 * ta.ema(data,smoothingLengthInput) - ta.ema(ta.ema(data,smoothingLengthInput),smoothingLengthInput)
        TEMA    => 3 * ta.ema(data,smoothingLengthInput) - 3 * ta.ema(ta.ema(data,smoothingLengthInput),smoothingLengthInput) + ta.ema(ta.ema(ta.ema(data,smoothingLengthInput),smoothingLengthInput),smoothingLengthInput)
        HMA     => ta.hma(data,smoothingLengthInput)
        WMA     => ta.wma(data,smoothingLengthInput)
        SWMA    => ta.swma(data)
        VWMA    => ta.vwma(data,smoothingLengthInput)
        => data
//---------------------------------------------------------------------------------------------------------------------}
//MUTABLE VARIABLES & EXECUTION
//---------------------------------------------------------------------------------------------------------------------{
bull            = close > high[1]
bear            = close < low[1]
sideway         = not bull and not bear
bullWeight      = math.abs(close - high[1])
bearWeight      = math.abs(close - low[1])
sidewayWeight   = 1

addData(bulls, bull ? +1 : -1, windowInput,bullWeight)
addData(bears, bear ? +1 : -1, windowInput,bearWeight)
addData(sideways, sideway ? +1 : -1, windowInput,sidewayWeight)
addWeight(volumes,volume,windowInput)
addWeight(bullWeights,bullWeight,windowInput)
addWeight(bearWeights,bearWeight,windowInput)
addWeight(sidewayWeights,sidewayWeight,windowInput)

bullsNormalized     = smooth(normalize(bulls,windowInput,bullWeights))
bearsNormalized     = smooth(normalize(bears,windowInput,bearWeights))
sidewaysNormalized  = smooth(normalize(sideways,windowInput,sidewayWeights))

bullPlot            = plot(bullsNormalized,'Bullish', bullColor)
bearPlot            = plot(bearsNormalized,'Bearish', bearColor)
sidewaysPlot        = plot(sidewaysNormalized,'Sideways',sidewaysColor)
topPlot             = plot(topThresholdInput,'Top',color(na))
bottomPlot          = plot(bottomThresholdInput,'Bottom',color(na))

bullishCross        = bullsNormalized > bearsNormalized and bullsNormalized[1] <= bearsNormalized[1]
bearishCross        = bearsNormalized > bullsNormalized and bearsNormalized[1] <= bullsNormalized[1]

plotshape(bullsNormalized,'Bullish Cross',shape.circle,location.absolute,bullishCross ? color.new(bullColor,0) : color(na), size = size.tiny)
plotshape(bearsNormalized,'Bearish Cross',shape.circle,location.absolute,bearishCross ? color.new(bearColor,0) : color(na), size = size.tiny)

fill(bullPlot,topPlot, bullsNormalized > topThresholdInput ? bullColor : color(na),'Bullish Top Fill')
fill(bullPlot,bottomPlot ,bullsNormalized < bottomThresholdInput ? bullColor : color(na),'Bullish Bottom Fill')
fill(bearPlot, topPlot, bearsNormalized > topThresholdInput ? bearColor : color(na),'Bearish Top Fill')
fill(bearPlot, bottomPlot, bearsNormalized < bottomThresholdInput ? bearColor : color(na),'Bearish Bottom Fill')
fill(sidewaysPlot, bottomPlot, sidewaysNormalized < bottomThresholdInput ? sidewaysColor : color(na),'Sideways Bottom Fill')

hline(topThresholdInput,'Top Threshold')
hline(bottomThresholdInput,'Bottom Threshold')
//---------------------------------------------------------------------------------------------------------------------}

16. Methode VWAP + Candle-Rating SELL (close, robust)
hints:xThis multi‐timeframe setup first scans the 15-minute chart for strong bearish candles (body position in the bottom 40% of their range, i.e. rating 4 or 5) that close below the session VWAP. When it finds the first such “setup” of a trading period, it pins the low of that 15-minute candle as a trigger level and draws a persistent red line there. On the 5-minute chart, the strategy then waits for a similarly strong bearish candle (rating 4 or 5) to close below that marked low—at which point it emits a one‐time SELL signal. The trigger level remains in place (and additional sell signals are locked out) until the market “rescues” the price: a 15-minute bullish candle (rating 1 or 2) closing back above VWAP clears the old setup and allows the next valid bearish 15-minute candle to form a new trigger. This design ensures you only trade the most significant breakdowns after a clear bearish bias and avoids repeated signals until a genuine bullish reversal resets the system.

source code
//@version=5
indicator("VWAP + Candle-Rating SELL (close, robust)", overlay=true)

// 1) Grab only the previous closed 15-min bar (VWAP, OHLC, bar_index)
[v15, c15, o15, h15, l15, b15] = request.security(syminfo.tickerid, "15", [ta.vwap[1], close[1], open[1], high[1], low[1], bar_index[1]], lookahead=barmerge.lookahead_on)

// 2) Candle-rating helper (if/else ladder)
f_rate(_o, _h, _l, _c) =>
    rng = math.max(_h - _l, 0.001)
    pct = _c < _o ? (_c - _l)/rng : (_h - _c)/rng
    if _c < _o
        if pct < 0.2
            5
        else if pct < 0.4
            4
        else if pct < 0.6
            3
        else if pct < 0.8
            2
        else
            1
    else
        0

cr15 = f_rate(o15, h15, l15, c15)
cr5  = f_rate(open, high, low,   close)

// 3) New 15-min bearish setup?
new15   = ta.change(b15) != 0
valid15 = new15 and (cr15 == 4 or cr15 == 5) and c15 < v15

var float triggerLow = na
var int   setupBar   = na
if valid15
    triggerLow := l15
    setupBar   := b15

// 4) Draw red line at that 15-min low
plot(valid15 ? l15 : na, title="15m Setup Low", style=plot.style_linebr, color=color.red, linewidth=2)

// 5) SELL when a 5-min candle (cr5==4 or 5) closes below that line
sell = (b15 == setupBar) and (cr5 == 4 or cr5 == 5) and close < triggerLow
plotshape(sell, title="SELL", style=shape.labeldown, location=location.abovebar, text="SELL", color=color.red)

// 6) Clear so it fires only once per setup
if sell
    triggerLow := na
    setupBar   := na

17. Methode Moving Average Candles
hints:**Moving Average Candles — MA-Based Smoothed Candlestick Overlay**

This script replaces traditional price candles with smoothed versions calculated using various types of moving averages. Instead of plotting raw price data, each OHLC component (Open, High, Low, Close) is independently smoothed using your selected moving average method.

---

### 📌 Features:
- Choose from 13 MA types: `SMA`, `EMA`, `RMA`, `WMA`, `VWMA`, `HMA`, `T3`, `DEMA`, `TEMA`, `KAMA`, `ZLEMA`, `McGinley`, `EPMA`
- Fully configurable moving average length (1–1000)
- Color-coded candles based on smoothed Open vs Close
- Works directly on price charts as an overlay

---

### 🎯 Use Cases:
- Visualize smoothed market structure more clearly
- Reduce noise in price action for better trend analysis
- Combine with other indicators or strategies for confluence

---

> ⚠️ **Note:** Since all OHLC values are based on moving averages, these candles do **not** represent actual market trades. Use them for trend and structure analysis, not trade entries based on precise levels.

---

*Created to support traders seeking a cleaner visual representation of price dynamics.*

Source code
//@version=6
indicator("Moving Average Candles", "MA Candles", overlay=true)

ma_type = input.string(title="MA Type", defval="SMA", options=["SMA", "EMA", "RMA", "WMA", "VWMA", "HMA", "T3", "DEMA", "TEMA", "KAMA", "ZLEMA", "McGinley", "EPMA"])
ma_length = input.int(title="MA Length", defval=14, minval=1, maxval=1000)

// DEMA Calculation
dema(src, len) =>
    ema1 = ta.ema(src, len)
    ema2 = ta.ema(ema1, len)
    2 * ema1 - ema2

// TEMA Calculation
tema(src, len) =>
    ema1 = ta.ema(src, len)
    ema2 = ta.ema(ema1, len)
    ema3 = ta.ema(ema2, len)
    3 * (ema1 - ema2) + ema3

// T3 MA Calculation
t3(src, len) =>
    xe1_1 = ta.ema(src, len)
    xe2_1 = ta.ema(xe1_1, len)
    xe3_1 = ta.ema(xe2_1, len)
    xe4_1 = ta.ema(xe3_1, len)
    xe5_1 = ta.ema(xe4_1, len)
    xe6_1 = ta.ema(xe5_1, len)
    b_1 = 0.7
    c1_1 = -b_1*b_1*b_1
    c2_1 = 3*b_1*b_1+3*b_1*b_1*b_1
    c3_1 = -6*b_1*b_1-3*b_1-3*b_1*b_1*b_1
    c4_1 = 1+3*b_1+b_1*b_1*b_1+3*b_1*b_1
    c1_1 * xe6_1 + c2_1 * xe5_1 + c3_1 * xe4_1 + c4_1 * xe3_1

// KAMA Calculation
kama(src, len) =>
    mom = math.abs(ta.change(src))
    volatility = math.sum(math.abs(ta.change(src)), len)
    er = volatility != 0 ? mom/volatility : 0
    fastSC = 2/(2+1)
    slowSC = 2/(30+1)
    sc = er * (fastSC - slowSC) + slowSC
    sc2 = sc * sc
    var float kama = na
    kama := na(kama) ? src : kama + sc2 * (src - kama)
    kama

// ZLEMA Calculation
zlema(src, len) =>
    lag = (len - 1) / 2
    ema1 = ta.ema(src + (src - src[int(lag)]), len)
    ema1

// McGinley Dynamic
mcg(src, len) =>
    var float mg = na
    mg := na(mg) ? src : mg + (src - mg) / (len * math.pow(src/mg, 4))
    mg

// EPMA Calculation
epma(src, len) =>
    alpha = 2 / (len + 1)
    sum = math.sum(src[1], len-1)
    (src * alpha) + (sum * (1 - alpha)) / (len-1)

// Function to calculate MA based on type
calc_ma(src, len, type) =>
    float result = 0
    result := switch type
        "SMA" => ta.sma(src, len)
        "EMA" => ta.ema(src, len)
        "RMA" => ta.rma(src, len)
        "WMA" => ta.wma(src, len)
        "VWMA" => ta.vwma(src, len)
        "HMA" => ta.hma(src, len)
        "T3" => t3(src, len)
        "DEMA" => dema(src, len)
        "TEMA" => tema(src, len)
        "KAMA" => kama(src, len)
        "ZLEMA" => zlema(src, len)
        "McGinley" => mcg(src, len)
        "EPMA" => epma(src, len)
        => ta.sma(src, len)
    result

open_ = calc_ma(open, ma_length, ma_type)
high_ = calc_ma(high, ma_length, ma_type)
low_ = calc_ma(low, ma_length, ma_type)
close_ = calc_ma(close, ma_length, ma_type)

candle_color = close_ >= open_ ? color.green : color.red

plotcandle(open_, high_, low_, close_, title="MA Candles", color=candle_color, wickcolor = candle_color, bordercolor = candle_color)
