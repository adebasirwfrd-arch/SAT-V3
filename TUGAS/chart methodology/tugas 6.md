17. Metode CRT with Trend Filter
hints:Explanation of Functionality
translate to english first
The CRT RED DOG with Trend Filter indicator is a tool used to identify buy and sell signals on a price chart. It filters signals based on the market trend to ensure higher accuracy.

Main Components of the Indicator
Moving Average (EMA) Settings

Users can set the moving average (EMA) length as desired, with a default value of 50 days.
This moving average is used to determine the market trend.
Determining Market Trend

Uptrend: Occurs when the closing price is above the moving average.
Downtrend: Occurs when the closing price is below the moving average.
Identifying Buy and Sell Signals

Buy Signal: Occurs when the current bar's low is lower than the previous bar's low, and the closing price is higher than the previous bar's close, during an uptrend.
Sell Signal: Occurs when the current bar's high is higher than the previous bar's high, and the closing price is lower than the previous bar's close, during a downtrend.
Displaying Signals on the Chart

Buy signals are displayed with a green arrow below the candlestick.
Sell signals are displayed with a red arrow above the candlestick.

Time frame Day >> 15M

Source code
//@version=5
indicator("CRT with Trend Filter", overlay=true)

// การตั้งค่าค่าเฉลี่ยเคลื่อนที่ Moving Average settings

maLength = input.int(50, title="MA Length", minval=1)

// คำนวณค่าเฉลี่ยเคลื่อนที่ตามค่าที่ตั้งไว้ Calculate the moving average based on the set length
ma = ta.ema(close, maLength)

// เงื่อนไขแนวโน้มขาขึ้น Determine market trend
uptrend = close > ma

// เงื่อนไขแนวโน้มขาลง Determine market trend
downtrend = close < ma

// เงื่อนไขลูกศรเขียว: Low ของแท่งปัจจุบัน < Low ของแท่งก่อนหน้า และราคาปิดต้องสูงกว่าแท่งก่อนหน้า ในแนวโน้มขาขึ้น
// Buy signal condition: Current bar's low < previous bar's low and close > previous bar's close during an uptrend

longCondition = low < low[1] and close > close[1] and uptrend
plotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, title="Buy Signal")

// เงื่อนไขลูกศรแดง: High ของแท่งปัจจุบัน > High ของแท่งก่อนหน้า และราคาปิดต้องต่ำกว่าแท่งก่อนหน้า ในแนวโน้มขาลง
// Sell signal condition: Current bar's high > previous bar's high and close < previous bar's close during a downtrend

shortCondition = high > high[1] and close < close[1] and downtrend
plotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, title="Sell Signal")

18. Methode Big Candles Filter
hints:How It Works

A candle is considered "big" only if its body (distance from open to close) exceeds the barHeight value.
** NOT calculated by Range !!!

Features :
Bullish candles (close > open) are marked with a green "Buy" triangle if the body is large enough.
Bearish candles (close < open) are marked with a red "Sell" triangle if the body is large enough.
The bars are colored for big candles, and optional labels show the open and close prices.

Source code
//Big Candles Filter _ by IpchiXD (Modified)
//@version=6
indicator('Big Candles Filter', overlay = true)

// Input for bar height threshold
var float barHeight = input.float(80, 'Bar Height', minval = 0)
var bool showOpen = input.bool(true, 'Show Candlestick Open Value')
var bool showClose = input.bool(false, 'Show Candlestick Close Value')
var float LabelOffset = input.float(15, 'Label Offset', minval = 0)

// Define conditions for big candles based on close-to-open difference
bool bigUp = close > open and close - open > barHeight
bool bigDown = close < open and open - close > barHeight

// Plot shapes for big candles
plotshape(bigUp, title = 'Big Up', location = location.top, color = color.green, style = shape.triangleup, text = 'Buy')
plotshape(bigDown, title = 'Big Down', location = location.top, color = color.red, style = shape.triangledown, text = 'Sell')

// Color the bars based on conditions
barcolor(bigDown ? color.rgb(255, 152, 0) : bigUp ? color.rgb(242, 255, 0) : color.rgb(0, 0, 0))

// Display open value if enabled
if showOpen
    if bigUp
        label.new(bar_index, low - LabelOffset, 'Open: ' + str.tostring(open), color = color.green, textcolor = color.white, style = label.style_label_up)
    if bigDown
        label.new(bar_index, high + LabelOffset, 'Open: ' + str.tostring(open), color = color.red, textcolor = color.white, style = label.style_label_down)

// Display close value if enabled with offset to avoid overlap
if showClose
    if bigUp
        label.new(bar_index, high + LabelOffset, 'Close: ' + str.tostring(close), color = color.green, textcolor = color.white, style = label.style_label_down)
    if bigDown
        label.new(bar_index, low - LabelOffset, 'Close: ' + str.tostring(close), color = color.red, textcolor = color.white, style = label.style_label_up)

19. Methode BBr1 Candle Range Volitility Gap Indicator
Hints:Modified Candle Range Volatility Gap Indicator
1. Useful to analyze bars body and wicks and volatility of security.
2. Added a Percentage Option - easier to analyze across different securities.
2. Added a Standard Deviation ("1 std dev= 68.2%, 2 std dev=95.4%, 3 std dev=99.7%, etc") based upon user defined lookback period.
3. Added the ability to include Gaps in Analysis. (Gaps are when the prior closing cost does not equal opening price)
4. Possible Uses setting up stop losses, trailing entries/exits (inside range or outside range).
5. Use it with other indicators in determining if to make an entry or close entry.


Reposted Original Description by © ka66 Kamal Advani
tradingview.com/v/jK6eszlT/
Visually shows the Body Range (open to close) and Candle Range (high to low).

Semi-transparent overlapping area is the full Candle Range, and fully-opaque smaller area is the Body Range. For aesthetics and visual consistency, Candle Range follows the direction of the Body Range, even though technically it's always positive (high - low).

The different plots for each range type also means the UI will allow deselecting one or the other as needed. For example, some strategies may care only about the Body Range, rather than the entire Candle Range, so the latter can be hidden to reduce noise.

Threshold horizontal lines are plotted, so the trader can modify these high and low levels as needed through the user interface. These need to be configured to match the instrument's price range levels for the timeframe. The defaults are pretty arbitrary for +/- 0.0080 (80 pips in a 4-decimal place forex pair). Where a range reaches or exceeds a threshold, it's visually marked as well with a shape at the Body or Candle peak, to assist with quicker visual potential setup scanning, for example, to anticipate a following reversal or continuation.

Source code
//@version=6
indicator('BBr1 Candle Range Volitility Gap Indicator', shorttitle = 'BB Cnd-Rng-Vol-Gap', precision = 4, overlay = false)

/////////////
// @BBItsTime release 1
// Modified Current Candle Range Volatility Gap Indicator.
// 1. Useful to analyze bars body and wicks and volatility of security.
// 2. Added a Percentage Option - easier to analyze across different securities.
// 3. Added a Standard Deviation ("1 std dev= 68.2%, 2 std dev=95.4%, 3 std dev=99.7%, etc") based upon user defined lookback period.
// 4. Added the ability to include Gaps in Analysis.  (Gaps are when the prior closing cost does not equal opening price)
// 5. Possible Uses setting up stop losses, trailing entries/exits (inside range or outside range).
// 6. Use it with other indicators in determining if to make an entry or close entry.



// // © ka66 Kamal Advani
// Current Candle Range Indicator.
//
// Visually shows the the body range (open to close) and candle range (high to low).
// Semi-transparent area is the candle range, and fully-opaque smaller area is the
// is the body range. Candle Range follows the direction of the body range, even
// though technically it's always positive. The different plots for each range
// type also means the UI will allow deselecting one or the other as needed. E.g.
// some strategies may care only about the body range, rather than the entire
// candle range, so the latter can be hidden to reduce noise.
//
// Threshold horizontal lines are plotted, so the trader can modify these high and
// low levels as needed through the user interface, for a quick visual scan of
// potential strength or reversal that might follow ranges reaching certain
// thresholds. These need to be configured to match the instrument's price
// range levels for the timeframe. The defaults are pretty arbitrary for +/- 0.0020
// (20 pips in a 4-decimal place forex pair).
//
// Where a range reaches or exceeds a threshold, it's visually marked as well
// with a shape, to assist with quicker setup (visual) scanning.
//
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ka66 Kamal Advani
//////////////


/////////////
// Current Candle Range Indicator.
//////////////

// Inputs 
// New input for percentage or pips
plotMode = input.string("Percentage", title = "Plot Mode", options = ["Pips", "Percentage"])
IncludePrevCandleClosing = input.bool(false, title = 'Include Previous Candle Closing as Starting Point', tooltip = 'Including the (Gaps) Previous Candle Closing will include Gap Ups and Gap Downs an added to Candle Body Calcs in Analysis, thus when enabled may not match up with candle color/direction on charts.  ie Gap up on opening from previous close but candle closes down on closing ')
useStdDevThresholds = input.bool(true, title = 'Use Standard Deviation Thresholds', tooltip = 'If unchecked, uses fixed threshold values')
lookbackPeriod = input.int(200, 'Lookback Period for StdDev', minval = 1, maxval = 500)
stdDevMultiplier = input.float(3.0, 'Standard Deviation Multiplier', minval = 0.1, step = 0.1, tooltip = "1 std dev= 68.2%, 2 std dev=95.4%, 3 std dev=99.7%")
positiveThreshold = input.float(0.0080, 'Positive/Bullish Range Threshold (Pips) ', group = 'Fixed Thresholds Pips')
negativeThreshold = input.float(-0.0080, 'Negative/Bearish Range Threshold (Pips)', group = 'Fixed Thresholds Pips')
useAbsoluteValues = input.bool(false, title = 'Show Both Up and Down Candles in Absolute/Positive Scale', tooltip = 'Threshold comparison will still be directional')

positiveThreshold1 = plotMode == "Pips" ? positiveThreshold : positiveThreshold *100 // * 10000
negativeThreshold1 = plotMode == "Pips" ? negativeThreshold : negativeThreshold *100 //* 10000

    


// Processing
open1 = IncludePrevCandleClosing ? close[1] : open

bullish = close > open1

// Calculate standard deviation of body range
bodyRange = close - open1
bodyRangeAbs = math.abs(bodyRange)
//candleRangeAbs = IncludePrevCandleClosing ? (high - low) + (close -close[1]) : high - low   //** check calc added gaps up or down to the base and Candle Range
candleRangeAbs = IncludePrevCandleClosing and bullish? high - low + (open - open1) : IncludePrevCandleClosing and bullish==false ? high - low + (open1-open) : high - low   //add gap to high-** check calc added gaps up or down to the base and Candle Range
candleRangeDirectional = bullish ? candleRangeAbs : -candleRangeAbs

// Convert to percentage if selected
bodyRangePerc = bullish ? bodyRangeAbs / open1 * 100 : (bodyRangeAbs / open1 * 100) * -1
bodyRangePercAbs = math.abs(bodyRangePerc)
candleRangePerc = bullish ? candleRangeAbs / open1 * 100 : (candleRangeAbs / open1 * 100) * -1
candleRangePercAbs = math.abs(candleRangePerc)


//results = if ? then : else

// Choose mode based on user selection
bodyRangeFinal = plotMode == "Percentage" ? bodyRangePerc : bodyRange
candleRangeFinal = plotMode == "Percentage" ? candleRangePerc : candleRangeDirectional

// Calculate standard deviation
bodyRangeMean = ta.sma(bodyRangeFinal, lookbackPeriod)
bodyRangeStdDev = ta.stdev(bodyRangeFinal, lookbackPeriod)

// Dynamic thresholds based on standard deviation
posStdDevThreshold = bodyRangeMean + (bodyRangeStdDev * stdDevMultiplier)
negStdDevThreshold = bodyRangeMean - (bodyRangeStdDev * stdDevMultiplier)


// Select which thresholds to use based on user input
activePosThreshold = useStdDevThresholds ? posStdDevThreshold : positiveThreshold1
activeNegThreshold = useStdDevThresholds ? negStdDevThreshold : negativeThreshold1

thresholdReached(ser) =>
    bullish ? ser >= activePosThreshold ? ser : na : ser <= activeNegThreshold ? ser : na

bodyRangeAtOrExceedsThreshold = thresholdReached(bodyRangeFinal)
bodyRangeAtOrExceedsThresholdAbs = math.abs(bodyRangeAtOrExceedsThreshold)
candleRangeAtOrExceedsThreshold = thresholdReached(candleRangeFinal)
candleRangeAtOrExceedsThresholdAbs = math.abs(candleRangeAtOrExceedsThreshold)

// Output
bodyRangeCol = bullish ? color.green : color.red
candleRangeCol = color.new(bodyRangeCol, 57)
var bodyRangeThresholdChar = '◉'
var candleRangeThresholdChar = '◍'
var positiveThresholdLineColor = color.new(color.green, 55)
var negativeThresholdLineColor = color.new(color.red, 55)

//if plotMode == "Pips"
//    if useStdDevThresholds


//    if useAbsoluteValues
//        activeNegThreshold := activeNegThreshold * -1
//if plotMode == "Percentage" //"Percentage"   
//    if useStdDevThresholds


//    if useAbsoluteValues
//        activeNegThreshold := activeNegThreshold * -1

hline(0, title = "Zero Line", linestyle = hline.style_solid, linewidth = 2)
plot(useAbsoluteValues ? activePosThreshold : activePosThreshold, title = "Positive Threshold Line", color = positiveThresholdLineColor, style = plot.style_line)

//plot(activeNegThreshold, title = "Negative Threshold Line", color = negativeThresholdLineColor, style = plot.style_line)


//plot(useAbsoluteValues ? activeNegThreshold : negativeThreshold, title = "Negative Threshold Line", color = negativeThresholdLineColor, style = plot.style_line)
plot(useAbsoluteValues ? activeNegThreshold *-1 : activeNegThreshold, title = "Negative Threshold Line", color = negativeThresholdLineColor, style = plot.style_line)

//plot(bodyRangeFinal, title = "Body Range", color = bodyRangeCol, linewidth = 2, style = plot.style_histogram)
plot(useAbsoluteValues and plotMode == "Pips"? bodyRangeAbs : useAbsoluteValues and plotMode == "Percentage" ? bodyRangePercAbs : bodyRangeFinal, title = "Body Range", color = bodyRangeCol, linewidth = 2, style = plot.style_histogram)
//plot(candleRangeFinal, title = "Directional Candle Range", color = candleRangeCol, linewidth = 2, style = plot.style_histogram)
plot(useAbsoluteValues and plotMode == "Pips" ? candleRangeAbs : useAbsoluteValues and plotMode == "Percentage" ? candleRangePercAbs :candleRangeFinal, title = "Directional Candle Range", color = candleRangeCol, linewidth = 2, style = plot.style_histogram)

//plotchar(bodyRangeAtOrExceedsThreshold, char = bodyRangeThresholdChar, title = "Body Range At Or Exceeds Threshold", location = location.absolute, color = color.silver)
plotchar(useAbsoluteValues ? bodyRangeAtOrExceedsThresholdAbs : bodyRangeAtOrExceedsThreshold, char = bodyRangeThresholdChar, title = "Body Range At Or Exceeds Threshold", location = location.absolute, color = color.silver)

//plotchar(candleRangeAtOrExceedsThreshold, char = candleRangeThresholdChar, title = "Candle Range At Or Exceeds Threshold", location = location.absolute, color = color.orange)
plotchar(useAbsoluteValues ? candleRangeAtOrExceedsThresholdAbs : candleRangeAtOrExceedsThreshold, char = candleRangeThresholdChar, title = "Candle Range At Or Exceeds Threshold", location = location.absolute, color = color.orange)

20. Methode EBP Candle Marker
HINTS: ### **EBP Candle Marker – TradingView Indicator**

The **EBP Candle Marker** is a specialized TradingView indicator designed to identify and highlight potential liquidity sweep candles. This indicator visually emphasizes key price action patterns where the market sweeps previous highs or lows and closes in the opposite direction, often signaling potential reversals or liquidity grabs.

---

### 📊 **Indicator Logic:**

1. **Bullish Sweep:**
- The current candle’s **low** is lower than the previous candle’s **low** (indicating a liquidity sweep).
- The **close** is above both the **open** and **close** of the previous candle.

2. **Bearish Sweep:**
- The current candle’s **high** is higher than the previous candle’s **high** (indicating a liquidity sweep).
- The **close** is below both the **open** and **close** of the previous candle.

---

### 🎨 **Visual Representation:**
- **Yellow Candle Body:** Highlights any candle meeting the bullish or bearish sweep conditions.

---

### 🔔 **Alert Functionality:**
The indicator supports setting custom alerts in TradingView for:
- **Bullish Sweep Detected** – Notifies when a bullish sweep occurs.
- **Bearish Sweep Detected** – Notifies when a bearish sweep occurs.

These alerts are compatible across any timeframe, providing flexibility to monitor key market conditions.

---

### 📈 **Use Cases:**
- **Liquidity Sweep Detection:** Identify areas where the market may be triggering stop-loss orders or liquidity hunts.
- **Reversal Confirmation:** Enhance trade confirmation by identifying potential reversal zones.
- **Scalping & Swing Trading:** Suitable for both short-term and long-term trading strategies across multiple timeframes.

sOURCE CODE
//@version=5
indicator("EBP Candle Marker", overlay = true)

// Function to check bullish sweep
isBullishSweep(c) =>
    low[c] < low[c + 1] and close[c] > open[c + 1] and close[c] > close[c + 1]

// Function to check bearish sweep
isBearishSweep(c) =>
    high[c] > high[c + 1] and close[c] < open[c + 1] and close[c] < close[c + 1]

// Check conditions
bullishSweep = isBullishSweep(0)
bearishSweep = isBearishSweep(0)

// Highlight the candle body if criteria is met
barcolor(bullishSweep ? color.yellow : na)
barcolor(bearishSweep ? color.gray : na)

// Alert conditions
alertcondition(bullishSweep, title = "Bullish Sweep", message = "Bullish Sweep Detected")
alertcondition(bearishSweep, title = "Bearish Sweep", message = "Bearish Sweep Detected")

21. mETHODE Candle Momentum Exhaustion
HINTS:Candle Momentum Exhaustion

The Candle Momentum Exhaustion indicator is designed to help traders spot potential turning points in a trend by identifying when the prevailing momentum may be “running on empty.” The indicator works by comparing the size of each candle’s body (the absolute difference between the open and close) to the average body size over a recent period. When a candle’s body exceeds a user‐defined multiple of this average, it is flagged as an “exhaustion” candle.
• A bullish exhaustion (shown with a red down–facing triangle above the bar) occurs when a very large bullish candle (close > open) is detected, suggesting that buyers may have pushed the price too far and the rally could be near its end.
• A bearish exhaustion (shown with a green up–facing triangle below the bar) occurs when a very large bearish candle (close < open) is detected, implying that selling pressure might be overdone.

These signals can alert you to a potential reversal or consolidation point. The script also includes alert conditions so that you can set up notifications whenever an exhaustion signal is generated.

How It Works
1. Average Candle Body:
The script computes a simple moving average (SMA) of the absolute candle bodies over a user-defined period (default is 14 bars).
2. Exhaustion Candidate:
A candle is flagged as an exhaustion candidate if its body size exceeds the average by more than the set multiplier (default is 2.0).
3. Signal Identification:
• If the exhaustion candle is bullish (close > open), it is marked with a red down–facing triangle above the bar.
• If it is bearish (close < open), it is marked with a green up–facing triangle below the bar.
4. Alerts:
The built-in alertcondition() calls allow you to set alerts (via TradingView’s alert system) so that you can be notified when an exhaustion event occurs.

Risk Disclaimer:

This indicator is provided for educational and informational purposes only and does not constitute financial, investment, or trading advice. Trading and investing involve significant risk, and you should not rely solely on this indicator when making any trading decisions. Past performance is not indicative of future results. Always perform your own due diligence and consult with a qualified financial advisor before making any financial decisions. The creator of this indicator shall not be held responsible for any losses incurred through its use.

source code
// Candle Momentum Exhaustion Indicator
//@version=6
indicator("Candle Momentum Exhaustion", overlay=true)

// Input Parameters
consecutiveCandles = input(3, "Number of Consecutive Candles")
showAlerts = input(true, "Enable Alerts")

// Calculating Candle Components
candleTrend = close > open ? 1 : close < open ? -1 : 0

// Detecting Consecutive Candles in the Same Trend
var int[] trends = array.new_int(consecutiveCandles, na)
var bool highlightCandle = false

if na(candleTrend) == false
    array.shift(trends)
    array.push(trends, candleTrend)

    if array.size(trends) == consecutiveCandles
        sameTrend = true
        firstTrend = array.get(trends, 0)
        for i = 1 to consecutiveCandles - 1
            if array.get(trends, i) != firstTrend or firstTrend == 0
                sameTrend := false
                break

        highlightCandle := sameTrend

// Plotting Signals on Chart
plotshape(highlightCandle and candleTrend == 1, location=location.belowbar, color=color.green, style=shape.triangleup, size=size.tiny, title="Bullish Signal")
plotshape(highlightCandle and candleTrend == -1, location=location.abovebar, color=color.red, style=shape.triangledown, size=size.tiny, title="Bearish Signal")

// Alerts for Signals
alertcondition(highlightCandle and candleTrend == 1, title="Bullish Signal Alert", message="Three consecutive green candles detected!")
alertcondition(highlightCandle and candleTrend == -1, title="Bearish Signal Alert", message="Three consecutive red candles detected!")

// Highlighting Only the Third Consecutive Candle
barcolor(highlightCandle ? (candleTrend == 1 ? color.black : color.black) : na)

22. Methode Color candle by time
hints:This indicator, written in Pine Script v5, allows you to highlight candles (using a user-selected color) that fall within a user-defined time range. Candles outside this range maintain their original appearance.

How it Works and Key Benefits:

- Time Interval Customization: By specifying start and end hours/minutes, you can emphasize only the desired market session.
- Choice of Preferred Color: The body, wicks, and borders of the candles within the selected range are uniformly colored, based on the user’s chosen tone.
- Enhanced Focus on Price Action: By focusing on the most relevant trading hours, your analysis becomes more streamlined and intuitive, without altering the rest of the session’s candle appearance.

!! DO NOT FORGET TO SELECT THE OPTION: 'BRING TO FRONT' IN THE INDICATOR'S VISUAL ORDER !!

Source code
//@version=5
indicator(title="Color candle by time", overlay=true)

// ─────────────────────────────────────────────
// 1. INPUT: Start and end time
// ─────────────────────────────────────────────
startHour   = input.int(9,  title="Start hour (H)",   minval=0, maxval=23)
startMinute = input.int(30, title="Start minute (M)", minval=0, maxval=59)

endHour     = input.int(15, title="End hour (H)",    minval=0, maxval=23)
endMinute   = input.int(0,  title="End minute (M)",  minval=0, maxval=59)

// Converts times into total minutes starting from 00:00
startTime = startHour * 60 + startMinute
endTime   = endHour   * 60 + endMinute

// Current bar’s minutes (hour * 60 + minute)
currentTime = hour(time) * 60 + minute(time)

// Checks if the bar's time is within the interval
inRange = (currentTime >= startTime) and (currentTime <= endTime)

// If the bar is within the interval, color it yellow; otherwise, do not display it (na)
myColor = inRange ? color.yellow : na

// ─────────────────────────────────────────────
// 2. Manually draw the candles
// ─────────────────────────────────────────────
plotcandle(open, high, low, close, title = "Custom candles",color = myColor, wickcolor = myColor, bordercolor  = myColor)

23. Methode BullDozz MA-Candlesticks
hints:BullDozz MA-Candlesticks 🏗️📊

The BullDozz MA-Candlesticks indicator transforms traditional candlesticks by replacing their Open, High, Low, and Close values with various types of Moving Averages (MAs). This helps traders visualize market trends with smoother price action, reducing noise and enhancing decision-making.

🔹 Features:
✅ Choose from multiple MA types: SMA, EMA, WMA, DEMA, TEMA, LSMA
✅ Customizable MA period for flexibility
✅ Candlestick colors based on trend: Green for bullish, Red for bearish
✅ Works on any market and timeframe

This indicator is perfect for traders who want a clearer perspective on price movement using moving average-based candlesticks. 🚀 Try it now and refine your market analysis! 📈🔥

Source code
//@version=5
indicator("BullDozz MA-Candlesticks", overlay=true)

// Functions to calculate different types of MAs
// Double Exponential Moving Average (DEMA) calculation
dema(source, length) =>
    ema1 = ta.ema(source, length)
    ema2 = ta.ema(ema1, length)
    2 * ema1 - ema2

// Triple Exponential Moving Average (TEMA) calculation
tema(source, length) =>
    ema1 = ta.ema(source, length)
    ema2 = ta.ema(ema1, length)
    ema3 = ta.ema(ema2, length)
    3 * ema1 - 3 * ema2 + ema3

// Input parameters for MA period and type
MAPeriod = input.int(10, title="MA Period", minval=1)
MAType = input.string("SMA", title="MA Type", options=["SMA", "EMA", "WMA", "DEMA", "TEMA", "LSMA"])

// Function to choose MA type
ma(source, length, type) =>
    switch type
        "SMA" => ta.sma(source, length)
        "EMA" => ta.ema(source, length)
        "WMA" => ta.wma(source, length)
        "DEMA" => dema(source, length)
        "TEMA" => tema(source, length)
        "LSMA" => ta.linreg(source, length, 0)
        => ta.sma(source, length) // Default to SMA

// Calculate MAs for Open, High, Low, and Close
MAOpen = ma(open, MAPeriod, MAType)
MAHigh = ma(high, MAPeriod, MAType)
MALow = ma(low, MAPeriod, MAType)
MAClose = ma(close, MAPeriod, MAType)

// Plot the candlesticks on the main chart
plotcandle(MAOpen, MAHigh, MALow, MAClose, color=(MAOpen < MAClose ? color.green : color.red), wickcolor=color.gray, bordercolor=color.black)

24. Methode Bull vs Bear Candles
hints:The Bull vs Bear Candles indicator helps you analyze market sentiment by counting and comparing bullish and bearish candles. It tracks the number of bullish candles and calculates their percentage, then does the same for bearish candles. Based on this data, the indicator determines whether bulls or bears are in control. Additionally, it counts the total number of candles within the selected range, giving you a clearer picture of price action. Use this tool to quickly assess market trends and make more informed trading decisions. 🚀

Source code

// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © yourtradingbuddy

//@version=6
indicator("Bull vs Bear Candles", overlay=true)

var total_above = 0
var total_below = 0
var total_draw = 0
var total_count = 0

is_above = close > open and barstate.isconfirmed
is_below = close < open and barstate.isconfirmed

if (barstate.isconfirmed)
    if (is_above)
        total_above := total_above + 1
    else if (is_below)
        total_below := total_below + 1
    else
        total_draw := total_draw + 1

    total_count := total_count + 1

if (barstate.islast)
    table = table.new(position.bottom_right, 10, 10, color.black, border_width=3)

    row = 0
    table.cell(table, 0, row, text=total_above > total_below ? "BULL WINS" : (total_above < total_below ? "BEAR WINS" : "NEUTRAL"), text_color=color.white, bgcolor=total_above > total_below ? color.green : (total_above < total_below ? color.red : color.gray))
    table.merge_cells(table, 0, 0, 1, 2)

    table.cell(table, 2, row, text="Bulls", text_color=color.white, bgcolor=color.green)
    table.cell(table, 3, row, text=str.tostring((total_above), "#,###"), text_color=color.green, bgcolor=color.white)
    table.cell(table, 4, row, text=str.tostring((total_above / total_count), "#,###.##%"), text_color=color.green, bgcolor=color.white)
    row += 1

    table.cell(table, 2, row, text="Bears", text_color=color.white, bgcolor=color.red)
    table.cell(table, 3, row, text=str.tostring((total_below), "#,###"), text_color=color.red, bgcolor=color.white)
    table.cell(table, 4, row, text=str.tostring((total_below / total_count), "#,###.##%"), text_color=color.red, bgcolor=color.white)
    row += 1

    table.cell(table, 2, row, text="Draw", text_color=color.white, bgcolor=color.gray)
    table.cell(table, 3, row, text=str.tostring((total_draw), "#,###"), text_color=color.gray, bgcolor=color.white)
    table.cell(table, 4, row, text=str.tostring((total_draw / total_count), "#,###.##%"), text_color=color.gray, bgcolor=color.white)
    row += 1

    table.cell(table, 0, row, text=str.tostring(total_count, "#,### Candles"), text_color=color.black, bgcolor=color.white)
    table.merge_cells(table, 0, row, 4, row)

25. Methode Last Candle Close Above/Below Alert
hints:How it works:

The script calculates whether the close of each candle is above or below the close of the previous candle, same as the initial code.

isLastBar is checked and the last candle to be created is the only one that will receive the condition from this variable.

If a highlight is needed it will use this criteria and apply the correct color for the last candle only, and any other candle will not be colored.

If alerts are enabled they will only work for the last bar too.

How to Use:

Add this script to your TradingView chart.

Use the inputs to set the desired timeframe to analyze, whether you want an alert for candles closing above or closing below and the background colors.

The last candle will highlight yellow when the close is higher or lower than the previous candle.

Alerts will be triggered on the last candle if you enable the alert conditions.

Key Features:

Timeframe Selection: You can choose a different timeframe in the settings.
Candle Highlight: Candles that close above or below the previous candle are highlighted in yellow.

Alerts: Alerts are configurable to trigger for "Close Above" or "Close Below" conditions, based on your selection in the settings.

Source code
//@version=5
indicator("Last Candle Close Above/Below Highlight", overlay=true)

// Input settings
timeframeInput = input.timeframe("", title="Select Timeframe")
alertConditionAbove = input.bool(true, title="Alert for Close Above")
alertConditionBelow = input.bool(true, title="Alert for Close Below")

// Get data from the selected timeframe
var sourceTF = timeframeInput == "" ? timeframe.period : timeframeInput
closeTF = request.security(syminfo.tickerid, sourceTF, close)

// Conditions for close above or below the previous candle
closeAbove = closeTF > closeTF[1]
closeBelow = closeTF < closeTF[1]

// Identify the last bar using barstate.islast
isLastBar = barstate.islast

// Plotting yellow background for the last candle only
bgcolor(isLastBar and closeAbove ? color.yellow : na, title="Last Candle Close Above")
bgcolor(isLastBar and closeBelow ? #ff0cbe : na, title="Last Candle Close Below")

// Alerts for the last bar
if isLastBar and closeAbove and alertConditionAbove
    alert("Last Candle closed above the previous candle!", alert.freq_once_per_bar_close)

if isLastBar and closeBelow and alertConditionBelow
    alert("Last Candle closed below the previous candle!", alert.freq_once_per_bar_close)

26. Methode Truly Bullish & Bearish Candle
hints:This Pine Script indicator identifies and highlights truly bullish and bearish candles on your chart. Truly bullish candles are characterized by a strong bullish close significantly above the specific percentage, suggesting strong buying pressure. Conversely, truly bearish candles exhibit a strong bearish close significantly below the specific percentage, indicating strong selling pressure. By identifying these candles, traders can gain insights into potential shifts in market sentiment and make more informed trading decisions.

Key Features:

Identifies truly bullish and bearish candles based on strong open/close differentials.
Highlights these candles on the chart for easy visualization.
Helps traders identify potential reversals or continuations in market trends.
Customizable parameters for fine-tuning to suit individual trading strategies.
Compatible with various timeframes and trading instruments.


Usage Instructions:

Apply the indicator to your chart.
Configure the settings according to your preferences.
Look for highlighted truly bullish and bearish candles as potential entry or exit signals.
Consider additional analysis and risk management strategies to confirm trading decisions.

Source bode
// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © mayureshjadhav12

//@version=5
indicator("Truly Bullish & Bearish Candle", "Bullish & Bearish Candle", true)

showBuySellBPre = input.bool(1, "Show Buy Sell Body Pressure")
candlePer = input.float(75.50, "Bullish or Bearish Per (%)", minval = 51, maxval = 100)

neutralColor = input.color(color.new(color.aqua,80), "Neutral Candle color")

// Calculate middle point of the candle
middle_point = (high + low) / 2

// Formula {
// Calculate candle range
candle_range = high - low
//}

// Calculate percentage value
body_value = ((100 - candlePer) / 100 ) * candle_range
newupper_point = (body_value + middle_point)
newlower_point = (middle_point - body_value)

barcolor(showBuySellBPre ? close > newupper_point ? na : close < newlower_point ? na :neutralColor : na)

27. Methode Volume Delta Candles HTF [TradingFinder] LTF Volume Candles
hints:In financial markets, understanding the concepts of supply and demand and their impact on price movements is of paramount importance. Supply and demand, as fundamental pillars of economics, reflect the interaction between buyers and sellers.

When buyers' strength surpasses that of sellers, demand increases, and prices tend to rise. Conversely, when sellers dominate buyers, supply overtakes demand, causing prices to drop. These interactions play a crucial role in determining market trends, price reversal points, and trading decisions.

Volume Delta Candles offer traders a practical way to visualize trading activity within each candlestick. By integrating data from lower timeframes or live market feeds, these candles eliminate the need for standalone volume indicators.

They present the proportions of buying and selling volume as intuitive colored bars, making it easier to interpret market dynamics at a glance. Additionally, they encapsulate critical metrics like peak delta, lowest delta, and net delta, allowing traders to grasp the market's internal order flow with greater precision.

In financial markets, grasping the interplay between supply and demand and its influence on price movements is crucial for successful trading. These fundamental economic forces reflect the ongoing balance between buyers and sellers in the market.

When buyers exert greater strength than sellers, demand dominates, driving prices upward. Conversely, when sellers take control, supply surpasses demand, and prices decline. Understanding these dynamics is essential for identifying market trends, pinpointing reversal points, and making informed trading decisions.

Volume Delta Candles provide an innovative method for evaluating trading activity within individual candlesticks, offering a simplified view without relying on separate volume indicators. By leveraging lower timeframe or real-time data, this tool visualizes the distribution of buying and selling volumes within a candle through color-coded bars.

This visual representation enables traders to quickly assess market sentiment and understand the forces driving price action. Buyer and seller strength is a critical concept that focuses on the ratio of buying to selling volumes. This ratio not only provides insights into the market's current state but also serves as a leading indicator for detecting potential shifts in trends.

Traders often rely on volume analysis to identify significant supply and demand zones, guiding their entry and exit strategies. Delta Candles translate these complex metrics, such as Maximum Delta, Minimum Delta, and Final Delta, into an easy-to-read visual format using Japanese candlestick structures, making them an invaluable resource for analyzing order flows and market momentum.

By merging the principles of supply and demand with comprehensive volume analysis, tools like the indicator introduced here offer unparalleled clarity into market behavior. This indicator calculates the relative strength of supply and demand for each candlestick by analyzing the ratio of buyers to sellers.

cuplikan



🔵How to Use

The presented indicator is a powerful tool for analyzing supply and demand strength in financial markets. It helps traders identify the strengths and weaknesses of buyers and sellers and utilize this information for better decision-making.

🟣Analyzing the Highest Volume Trades on Candles

A unique feature of this indicator is the visualization of price levels with the highest trade volume for each candlestick. These levels are marked as black lines on the candles, indicating prices where most trades occurred. This information is invaluable for identifying key supply and demand zones, which often act as support or resistance levels.

cuplikan


cuplikan



🟣Trend Confirmation

The indicator enables traders to confirm bullish or bearish trends by observing changes in buyer and seller strength. When buyer strength increases and demand surpasses supply, the likelihood of a bullish trend continuation grows. Conversely, decreasing buyer strength and increasing seller strength may signal a potential bearish trend reversal.

cuplikan


cuplikan



🟣Adjusting Timeframes and Calculation Methods

Users can customize the indicator's candlestick timeframe to align with their trading strategy. Additionally, they can switch between moving average and current candle modes to achieve more precise market analysis.

This indicator, with its accurate and visual data display, is a practical and reliable tool for market analysts and traders. Using it can help traders make better decisions and identify optimal entry and exit points.

🔵Settings

Lower Time Frame Volume: This setting determines which timeframe the indicator should use to identify the price levels with the highest trade volume. These levels, displayed as black lines on the candlesticks, indicate prices where the most trades occurred.
It is recommended that users align this timeframe with their primary chart’s timeframe.

As a general rule:

If the main chart’s timeframe is low (e.g., 1-minute or 5-minute), it is better to keep this setting at a similarly low timeframe.
As the main chart’s timeframe increases (e.g., daily or weekly), it is advisable to set this parameter to a higher timeframe for more aligned data analysis.

Cumulative Mode:

Current Candle: Strength is calculated only for the current candlestick.

EMA (Exponential Moving Average): The strength is calculated using an exponential moving average, suitable for identifying longer-term trends.


Calculation Period: The default period for the exponential moving average (EMA) is set to 21. Users can modify this value for more precise analysis based on their specific requirements.

Ultra Data: This option enables users to view more detailed data from various market sources, such as Forex, Crypto, or Stocks. When activated, the indicator aggregates and displays volume data from multiple sources.

🟣Table Settings

Show Info Table: This option determines whether the information table is displayed on the chart. When enabled, the table appears in a corner of the chart and provides details about the strength of buyers and sellers.

Table Size: Users can adjust the size of the text within the table to improve readability.

Table Position: This setting defines the table’s placement on the chart.

cuplikan



🔵Conclusion

The indicator introduced in this article is designed as an advanced tool for analyzing supply and demand dynamics in financial markets. By leveraging buyer and seller strength ratios and visually highlighting price levels with the highest trade volume, it aids traders in identifying key market zones.

Key features, such as adjustable analysis timeframes, customizable calculation methods, and precise volume data display, allow users to tailor their analyses to market conditions.
This indicator is invaluable for analyzing support and resistance levels derived from trade volumes, enabling traders to make more accurate decisions about entering or exiting trades.

By utilizing real market data and displaying the highest trade volume lines directly on the chart, it provides a precise perspective on market behavior. These features make it suitable for both novice and professional traders aiming to enhance their analysis and trading strategies.

With this indicator, traders can gain a better understanding of supply and demand dynamics and operate more intelligently in financial markets. By combining volume data with visual analysis, this tool provides a solid foundation for effective decision-making and improved trading performance. Choosing this indicator is a significant step toward refining analysis and achieving success in complex financial markets.

Source code
// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © TFlab

//@version=6
indicator('Volume Delta Candles HTF [TradingFinder] LTF Volume Candles ', 'TFlab Cumulative Candles', overlay = true)

TF = input.timeframe('5', 'Lower Time Frame Volume')
CumMode = input.string('EMA', 'Cumulative Mode', ['Current Candle', 'EMA'])
Period = input.int(21, 'Period')
UltraData = input.bool(false, '', inline = 'Data')
Market = input.string('Forex', 'Market Ultra Data', options = ['Forex', 'Crypto', 'Stock'], inline = 'Data')

//Info Table
Show_Info_Table = input(true, 'Info Table', group = 'Table')
Size = input.string(size.normal, 'Table Text Size', options = [size.small, size.normal])
Position = input.string(position.top_right, 'Table Position', options = [position.top_left, position.top_center, position.top_right, position.middle_left, position.middle_center, position.middle_right, position.bottom_left, position.bottom_center, position.bottom_right])

//Run Error
// if volume[1] == 0
//     runtime.error('This symbol does not have volume data available.')
var string a = ''
var string b = ''
var string c = ''
var string d = ''
var string e = ''
var string f = ''
var string g = ''
var string h = ''
var string i = ''
var string j = ''
var string k = ''
var string l = ''
var string m = ''
var string n = ''
var string o = ''
var string p = ''
var string q = ''
var string r = ''
var string s = ''
var string t = ''
var string u = ''
var string v = ''
var string w = ''
var string x = ''
var string y = ''
var string z = ''
float HVC = na

switch Market 
    'Forex' => 
	    a := 'FX'
	    b := 'OANDA'
	    c := 'FOREXCOM'
	    d := 'FX_IDC'
	    e := 'PEPPERSTONE'
	    f := 'CAPITALCOM'
	    g := 'ICMARKETS'
	    h := 'EIGHTCAP'
	    i := 'SAXO'
	    j := 'BLACKBULL'
	    k := 'VANTAGE'
	    l := 'FUSIONMARKETS'
	    m := 'FPMARKETS'
	    n := 'GBEBROKERS'
	    o := 'IBKR'
	    p := 'ACTIVTRADES'
	    q := 'EASYMARKETS'
	    r := 'FXOPEN'
	    s := 'CITYINDEX'
	    t := 'AFTERPRIME'
	    u := 'SKILLING'
	    v := 'WHSELFINVEST'
	    w := 'TRADENATION'
	    x := 'THINKMARKETS'
	    y := 'CFI'
	    z := 'PHILLIPNOVA'
	    z
    'Crypto' => 

	    a := 'BITSTAMP'
	    b := 'COINBASE'
	    c := 'INDEX'
	    d := 'CRYPTO'
	    e := 'BINANCE'
	    f := 'BITFINEX'
	    g := 'KRAKEN'
	    h := 'OANDA'
	    i := 'PEPPERSTONE'
	    j := 'GEMINI'
	    k := 'EIGHTCAP'
	    l := 'ICMARKETS'
	    m := 'VANTAGE'
	    n := 'CAPITALCOM'
	    o := 'FOREXCOM'
	    p := 'FX'
	    q := 'BLACKBULL'
	    r := 'SAXO'
	    s := 'FUSIONMARKETS'
	    t := 'CRYPTOCOM'
	    u := 'EASYMARKETS'
	    v := 'OKCOIN'
	    w := 'FPMARKETS'
	    x := 'AFTERPRIME'
	    y := 'ACTIVTRADES'
	    z := 'BTSE'
	    z
    'Stock' => 

	    a := '-'
	    b := '-'
	    c := '-'
	    d := '-'
	    e := '-'
	    f := '-'
	    g := '-'
	    h := '-'
	    i := '-'
	    j := '-'
	    k := '-'
	    l := '-'
	    m := '-'
	    n := '-'
	    o := '-'
	    p := '-'
	    q := '-'
	    r := '-'
	    s := '-'
	    t := '-'
	    u := '-'
	    v := '-'
	    w := '-'
	    x := '-'
	    y := '-'
	    z := '-'
	    z

[P, Vol] = request.security_lower_tf(syminfo.tickerid, TF, [close, volume])
V = nz(request.security(syminfo.tickerid, timeframe.period, volume, ignore_invalid_symbol = true))
Va = nz(request.security(a + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vb = nz(request.security(b + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vc = nz(request.security(c + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vd = nz(request.security(d + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Ve = nz(request.security(e + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vf = nz(request.security(f + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vg = nz(request.security(g + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vh = nz(request.security(h + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vi = nz(request.security(i + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vj = nz(request.security(j + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vk = nz(request.security(k + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vl = nz(request.security(l + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vm = nz(request.security(m + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vn = nz(request.security(n + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vo = nz(request.security(o + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vp = nz(request.security(p + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vq = nz(request.security(q + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vr = nz(request.security(r + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vs = nz(request.security(s + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vt = nz(request.security(t + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vu = nz(request.security(u + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vv = nz(request.security(v + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vw = nz(request.security(w + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vx = nz(request.security(x + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vy = nz(request.security(y + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))
Vz = nz(request.security(z + ':' + syminfo.ticker, timeframe.period, volume, ignore_invalid_symbol = true))



Vsum = V + Va + Vb + Vc + Vd + Ve + Vf + Vg + Vh + Vi + Vj + Vk + Vl + Vm + Vn + Vo + Vp + Vq + Vr + Vs + Vt + Vu + Vv + Vw + Vx + Vy + Vz

Volume = if UltraData
    Vsum
else
    volume

Buying = Volume * ((close - low) / (high - low))
Selling = Volume * ((high - close) / (high - low))

delta_ratio = math.abs(Buying / Volume)

// Data
Cumulative = if CumMode == 'EMA'
    ta.ema(delta_ratio, Period)
else
    delta_ratio

//Highest Volume Candle
if Vol.size() > 0
    HVC := P.get(Vol.indexof(Vol.max()))
    HVC
    //Delete Basa Candle
barcolor(#ffffff00)
//Buy Side
plotcandle(close > open ? open : close, high, low, close > open ? open + (close - open) * Cumulative : close + (open - close) * Cumulative, color = close > open ? #089981 : na, wickcolor = #00000000, bordercolor = #00000000, display = display.all)
//Sell Side
plotcandle(close > open ? open + (close - open) * Cumulative : close + (open - close) * Cumulative, high, low, close > open ? close : open, color = open > close ? #f23645 : na, wickcolor = #00000000, bordercolor = #00000000, display = display.all)
//High Volume Price
plotcandle(HVC, HVC, HVC, HVC, color = #000000, wickcolor = #000000, bordercolor = #000000)

//Table
var Info_Table = table.new(Position, 3, 4, bgcolor = #0d1a3f, border_color = color.rgb(28, 48, 109), border_width = 1, frame_color = #373a46, frame_width = 1)

if Show_Info_Table
    table.cell(Info_Table, 0, 0, 'Info Table', text_color = color.white, text_size = Size)
    table.merge_cells(Info_Table, 0, 0, 2, 0)
    table.cell(Info_Table, 0, 1, 'Method', text_color = color.white, text_size = Size)
    table.cell(Info_Table, 1, 1, 'Demand Strength', text_color = color.white, text_size = Size)
    table.cell(Info_Table, 2, 1, 'Supply Strength', text_color = color.white, text_size = Size)


    table.cell(Info_Table, 0, 2, 'Current Candle', text_color = color.white, text_size = Size)
    table.cell(Info_Table, 0, 3, 'Moving Average', text_color = color.white, text_size = Size)

    table.cell(Info_Table, 1, 2, str.tostring((delta_ratio) * 100 , '#.##') + '\t' +'%', text_color = #56a3a6, text_size = Size)
    table.cell(Info_Table, 1, 3, str.tostring((ta.ema(delta_ratio, Period)) * 100 , '#.##') + '\t' +'%', text_color = #56a3a6, text_size = Size)

    table.cell(Info_Table, 2, 2, str.tostring((1 - delta_ratio) * 100 , '#.##') + '\t' +'%', text_color = #db504a, text_size = Size)
    table.cell(Info_Table, 2, 3, str.tostring((ta.ema(1 - delta_ratio, Period)) * 100 , '#.##') + '\t' +'%', text_color = #db504a, text_size = Size)

