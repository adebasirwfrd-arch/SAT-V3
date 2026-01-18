
buat question marks button for hinths di top bar saat di click akan menunjukan hints masing masing methode

TRANSLATE KE BAHASA INGGRIS LALU TAMBAHKAN KE METHODE DI TOP BAR

Berikut masing masing methodologi untuk dimasukan ke top bar methode

1.Methode Crypto Accumulation Candle Finder

hints for Methode Crypto Accumulation Candle Finder :This indicator give you long entry signal to dectect MM's entry time.
it's recommended to use it in 5min. time frame.



//@version=5
indicator("Crypto Accumulation Candle Finder (매집봉 찾기)", shorttitle="매집봉", overlay=true)

// 사용자 입력 설정
volume_multiplier = input.float(2.0, title="평균 거래량 대비 배수", minval=1.0, tooltip="현재 거래량이 최근 평균 거래량의 몇 배 이상이어야 하는지 설정합니다.")
len = input.int(20, title="거래량 평균 기간", minval=1, tooltip="거래량 평균을 계산할 기간(캔들 수)을 설정합니다.")
wick_body_ratio = input.float(1.5, title="꼬리/몸통 비율 최소값", minval=0.5, tooltip="꼬리 길이가 몸통 길이의 몇 배 이상이어야 하는지 설정합니다.")
is_wick_upper = input.bool(true, title="긴 윗꼬리 매집봉 찾기", tooltip="긴 윗꼬리(매물 소화형) 매집봉을 찾으려면 체크하세요.")
is_wick_lower = input.bool(true, title="긴 아래꼬리 매집봉 찾기", tooltip="긴 아래꼬리(매수세 유입형) 매집봉을 찾으려면 체크하세요.")

// 거래량 조건: 현재 거래량이 평균 거래량보다 x배 이상 높은 경우
avg_volume = ta.sma(volume, len)
volume_condition = volume >= avg_volume * volume_multiplier

// 캔들 분석
body_range = math.abs(close - open)
// 몸통이 0인 경우(도지 캔들) 계산 오류 방지를 위해 최소값 설정
safe_body_range = math.max(body_range, syminfo.mintick)

upper_wick = high - math.max(open, close)
lower_wick = math.min(open, close) - low

// 꼬리/몸통 비율 조건
upper_wick_condition = is_wick_upper and upper_wick >= safe_body_range * wick_body_ratio
lower_wick_condition = is_wick_lower and lower_wick >= safe_body_range * wick_body_ratio

// 최종 매집봉 조건
is_accumulation_candle = volume_condition and (upper_wick_condition or lower_wick_condition)

// --- 수정된 부분 ---
// 1. bgcolor는 if문 밖에서 조건 연산자(삼항 연산자)를 사용하는 것이 권장됩니다.
bgcolor(is_accumulation_candle ? color.new(color.purple, 70) : na, title="매집봉 발견")

// 2. 가독성을 위해 차트 상단/하단에 아이콘 표시 (선택 사항)
plotshape(is_accumulation_candle, style=shape.triangleup, location=location.belowbar, color=color.purple, size=size.small, title="매집 신호")

alertcondition(is_accumulation_candle, title="매집봉 알림", message="잠재적인 매집봉이(가) 발견되었습니다!")
// 알림 설정

2. Methode Nooner's Heikin-Ashi/Bull-Bear Candles
hints : Candles are colored red and green when Heikin-Ashi and Bull/Bear indicator agree. They are colored yellow when they disagree.

//@version=6
indicator("#1 HA/BB Candles", overlay=true)

/// ——— Inputs
lengthInput = input.int(13, "BBP Length", minval=1)
bodyTransp  = input.int(50, "Body Transparency (0=solid, 100=invisible)", minval=0, maxval=100)

// ——— Bull-Bear Power (BBP)
emaVal     = ta.ema(close, lengthInput)
bullPower  = high - emaVal
bearPower  = low  - emaVal
bbp        = bullPower + bearPower
bbpBull    = bbp >= 0

// ——— Heikin Ashi calculations
ha_close = (open + high + low + close) / 4
var float ha_open = na
ha_open := na(ha_open[1]) ? (open + close) / 2 : (ha_open[1] + ha_close[1]) / 2
ha_high  = math.max(high, math.max(ha_close, ha_open))
ha_low   = math.min(low,  math.min(ha_close, ha_open))
haBull   = ha_close >= ha_open

/// ——— Agreement / Disagreement logic
agree       = haBull == bbpBull
baseColor   = haBull ? color.green : color.red  // green/red base color
bodyColor   = agree ? color.new(baseColor, bodyTransp) : color.new(color.yellow, bodyTransp)
wickColor   = agree ? baseColor : color.yellow
borderColor = agree ? baseColor : color.yellow

// ——— Draw custom candles
plotcandle(open, high, low, close,
     title       = "HA × BBP Candles",
     color       = bodyColor,     // body color (with transparency)
     wickcolor   = wickColor,     // solid wick
     bordercolor = borderColor)   // solid border


3. Methode Daily Candle by Natantia
hints : Introduction to the Daily Candle Indicator

The Daily Candle Indicator is a powerful and customizable tool designed for traders to visualize daily price action on any chart timeframe.

This Pine Script (version 5) indicator, built for platforms like TradingView, overlays a single candle representing the day's open, high, low, and close prices, with options to adjust its appearance and session focus.
Key Features:

Customizable Appearance: Users can set the colors for bullish (default green) and bearish (default white) candles, as well as the wick color (default white). The horizontal offset and candle thickness can also be adjusted to fit the chart layout.

Dynamic Updates: The candle updates on the last bar, with wicks drawn to reflect the daily high and low, providing a clear snapshot of the day's price movement.

source code
//@version=5
indicator("Daily Candle by Natantia", overlay=true, max_boxes_count=1, max_lines_count=4)

// Settings
bullish_color_input   = input.color(color.rgb(126, 233, 39), "Bull Candle Color", group="Colors")
bearish_color_input   = input.color(color.rgb(255, 255, 255), "Bear Candle Color", group="Colors")

bull_wick_color_input = input.color(color.lime,  "Bull Wick Color", group="Colors")
bear_wick_color_input = input.color(color.red,   "Bear Wick Color", group="Colors")

horizontal_offset     = input.int(50, "Horizontal Offset", minval=1, maxval=100, group="Position")
candle_thickness      = input.int(10, "Candle Thickness", minval=5, maxval=50, group="Position")

// Get daily data
daily_open  = request.security(syminfo.tickerid, "D", open)
daily_high  = request.security(syminfo.tickerid, "D", high)
daily_low   = request.security(syminfo.tickerid, "D", low)
daily_close = request.security(syminfo.tickerid, "D", close)

// Is candle bullish
is_bullish = daily_close >= daily_open
body_color = is_bullish ? bullish_color_input : bearish_color_input
wick_color = is_bullish ? bull_wick_color_input : bear_wick_color_input

// Candle coordinates
body_top    = math.max(daily_open, daily_close)
body_bottom = math.min(daily_open, daily_close)

current_bar = bar_index
right_edge  = current_bar + horizontal_offset
body_left   = right_edge - candle_thickness/2
body_right  = right_edge + candle_thickness/2

// Variables to store drawings
var box  daily_box  = na
var line upper_line = na
var line lower_line = na

if barstate.islast
    // Clear old drawings
    if not na(daily_box)
        box.delete(daily_box)
    if not na(upper_line)
        line.delete(upper_line)
    if not na(lower_line)
        line.delete(lower_line)

    // Draw body
    daily_box := box.new(body_left, body_top, body_right, body_bottom, 
                         bgcolor=body_color, border_color=body_color)

    // Upper wick
    if daily_high > body_top
        upper_line := line.new(right_edge, body_top, right_edge, daily_high, 
                               color=wick_color, width=2)

    // Lower wick
    if daily_low < body_bottom
        lower_line := line.new(right_edge, body_bottom, right_edge, daily_low, 
                               color=wick_color, width=2)

3. Methode CFR - Candle Formation Ratio
hints :Description

The CFR - Candle Formation Ratio is a powerful, flexible tool for detecting highly specific candle structures — including small-body candles, dojis, and accumulation-type formations.
With the latest update, you can now track up to three completely different candle formation types simultaneously, each with its own independent configuration.

This indicator helps traders identify candles that signal indecision, absorption, or localized accumulation/distribution behavior — often useful in market structure and volume context.

🧭 Key Features

✅ Multi-Formation System
You can now define up to three separate candlestick formations at once.
Each formation has its own customizable settings for body size, wick ratio, and body position.
Instantly visualize multiple structure types on the same chart, each with a different color.


✅ Doji-Logic Enhancement
Candles with a body size of zero (open = close) are now properly detected.
Even if a candle has no body, it will be recognized if its midpoint lies within your defined body-position range.
This enables precise detection of pure doji and spinning-top structures.


✅ Cleaner English Interface
All settings, tooltips, and group labels are now in English, improving usability.
Each formation is separated by a clear section line in the settings panel, making configuration intuitive.


✅ Advanced Body & Wick Filtering
Filter by maximum body size (as a % of total candle height).
Require that upper or lower wicks are at least X times larger than the body.
Define where the body must be located within the candle — for example, between 40 % and 60 % of the full range.


✅ Visual Output
Displays a single arrow marker below the candle when conditions are met.
Each formation can have its own color, making multiple pattern types easy to distinguish
.


🧩Use Cases
Identifying accumulation or distribution phases.
Spotting reversal points (hammer / shooting star / doji zones).
Filtering market structure signals based on precise candle shape.
Combining with volume or trend context for high-probability setups.


⚠️ Notes
This version is fully English-translated, including tooltips and section names.
Future updates may include formation grouping logic and built-in alerts.
For users of the earlier Turkish version: settings are now equivalent, but translated and reorganized for clarity.

Source code 
//@version=6
indicator("CFR - Candle Formation Ratio", overlay=true)

// ---------- MAIN ----------
groupMain = "CANDLESTICK SETTINGS"
// put input.int on a single line (positional min/max/step) to avoid parser issues
formationCount = input.int(1, "Candle formations", 1, 3, 1, group=groupMain, tooltip="Select how many candle formations you want to track (1-3).")

// ---------- helper function ----------
f_candle_signal(_maxBody, _minWickRatio, _bodyMin, _bodyMax) =>
    candleRange = high - low
    bodySize    = math.abs(close - open)
    upperWick   = high - math.max(open, close)
    lowerWick   = math.min(open, close) - low
    bodyPerc    = candleRange > 0 ? (bodySize / candleRange) * 100 : na
    upperRatio  = bodySize > 0 ? upperWick / bodySize : na
    lowerRatio  = bodySize > 0 ? lowerWick / bodySize : na
    bodyMid     = (open + close) / 2
    bodyPos     = candleRange > 0 ? ((bodyMid - low) / candleRange) * 100 : na

    // conditions (keep each logical expression on one line)
    condBodySize = not na(bodyPerc) and bodyPerc <= _maxBody
    condWick = (not na(upperRatio) and upperRatio >= _minWickRatio) or (not na(lowerRatio) and lowerRatio >= _minWickRatio)
    condBodyPos = not na(bodyPos) and bodyPos >= _bodyMin and bodyPos <= _bodyMax

    // doji handling: if body == 0 then only check the body-position range
    condDoji = bodySize == 0 and condBodyPos

    // return
    (condBodySize and condWick and condBodyPos) or condDoji

// ---------- FORMATION 1 ----------
group1 = "──── CANDLE STICK FORMATION #1 ────"
maxBody1    = input.float(10.0, "Maximal body length in %", minval=0.0, step=0.1, group=group1,
     tooltip="Defines how large the candle body may be in relation to the full candle (high - low).")
wickRatio1  = input.float(2.0, "Body in wicks (x)", minval=0.1, step=0.1, group=group1,
     tooltip="How many times the body must fit into the wick (wick/body).")
bodyPosMin1 = input.float(0.0, "Body - start (min %)", minval=0.0, maxval=100.0, step=0.1, group=group1,
     tooltip="Minimum vertical position (%) where the body should start (0 = low).")
bodyPosMax1 = input.float(100.0, "Body - end (max %)", minval=0.0, maxval=100.0, step=0.1, group=group1,
     tooltip="Maximum vertical position (%) where the body should end (100 = high).")
color1      = input.color(color.new(color.blue, 0), "Color indicator", group=group1)

signal1 = formationCount >= 1 and f_candle_signal(maxBody1, wickRatio1, bodyPosMin1, bodyPosMax1)

// ---------- FORMATION 2 ----------
group2 = "──── CANDLE STICK FORMATION #2 ────"
maxBody2    = input.float(10.0, "Maximal body length in %", minval=0.0, step=0.1, group=group2)
wickRatio2  = input.float(2.0, "Body in wicks (x)", minval=0.1, step=0.1, group=group2)
bodyPosMin2 = input.float(0.0, "Body - start (min %)", minval=0.0, maxval=100.0, step=0.1, group=group2)
bodyPosMax2 = input.float(100.0, "Body - end (max %)", minval=0.0, maxval=100.0, step=0.1, group=group2)
color2      = input.color(color.new(color.orange, 0), "Color indicator", group=group2)

signal2 = formationCount >= 2 and f_candle_signal(maxBody2, wickRatio2, bodyPosMin2, bodyPosMax2)

// ---------- FORMATION 3 ----------
group3 = "──── CANDLE STICK FORMATION #3 ────"
maxBody3    = input.float(10.0, "Maximal body length in %", minval=0.0, step=0.1, group=group3)
wickRatio3  = input.float(2.0, "Body in wicks (x)", minval=0.1, step=0.1, group=group3)
bodyPosMin3 = input.float(0.0, "Body - start (min %)", minval=0.0, maxval=100.0, step=0.1, group=group3)
bodyPosMax3 = input.float(100.0, "Body - end (max %)", minval=0.0, maxval=100.0, step=0.1, group=group3)
color3      = input.color(color.new(color.purple, 0), "Color indicator", group=group3)

signal3 = formationCount >= 3 and f_candle_signal(maxBody3, wickRatio3, bodyPosMin3, bodyPosMax3)

// ---------- PLOT ----------
plotshape(signal1, title="Formation 1", style=shape.triangleup, location=location.belowbar, color=color1, size=size.small)
plotshape(signal2, title="Formation 2", style=shape.triangleup, location=location.belowbar, color=color2, size=size.small)
plotshape(signal3, title="Formation 3", style=shape.triangleup, location=location.belowbar, color=color3, size=size.small)

4. Methode Renko Bands
Hints : This is renko without the candles, just the endpoint plotted as a line with bands around it that represent the brick size. The idea came from thinking about what renko actually gives you once you strip away the visual brick format. At its core, renko is a filtered price series that only updates when price moves a fixed amount, which means it's inherently a trend-following mechanism with built-in noise reduction. By plotting just the renko price level and surrounding it with bands at the brick threshold distances, you get something that works like regular volatility bands while still behaving as a trend indicator.

The center line is the current renko price, which trails actual price based on whichever brick sizing method you've selected. When price moves enough to complete a brick in the renko calculation, the center line jumps to the new brick level. The bands sit at plus and minus one brick size from that center line, showing you exactly how far price needs to move before the next brick would form. This makes the bands function as dynamic breakout levels. When price touches or crosses a band, you know a new renko brick is forming and the trend calculation is updating.

What makes this cool is the dual-purpose nature. You can use it like traditional volatility bands where the outer edges represent boundaries of normal price movement, and breaks beyond those boundaries signal potential trend continuation or exhaustion. But because the underlying calculation is renko rather than standard deviation or ATR around a moving average, the bands also give you direct insight into trend state. When the center line is rising consistently and price stays near the upper band, you're in a clean uptrend. When it's falling and price hugs the lower band, downtrend. When the center line is flat and price is bouncing between both bands, you're ranging.

The three brick sizing methods work the same way as standard renko implementations. Traditional sizing uses a fixed price range, so your bands are always the same absolute distance from the center line. ATR-based sizing calculates brick range from historical volatility, which makes the bands expand and contract based on the ATR measurement you chose at startup. Percentage-based sizing scales the brick size with price level, so the bands naturally widen as price increases and narrow as it decreases. This automatic scaling is particularly useful for instruments that move proportionally rather than in fixed increments.

The visual simplicity compared to full renko bricks makes this more practical for overlay use on your main chart. Instead of trying to read brick patterns in a separate pane or cluttering your price chart with boxes and lines, you get a single smoothed line with two bands that convey the same information about trend state and momentum. The center line shows you the filtered trend direction, the bands show you the threshold levels, and the relationship between price and the bands tells you whether the current move has legs or is stalling out.

From a trend-following perspective, the renko line naturally stays flat during consolidation and only moves when directional momentum is strong enough to complete bricks. This built-in filter removes a lot of the whipsaw that affects moving averages during choppy periods. Traditional moving averages continue updating with every bar regardless of whether meaningful directional movement is happening, which leads to false signals when price is just oscillating. The renko line only responds to sustained moves that meet the brick size threshold, so it tends to stay quiet when price is going nowhere and only signals when something is actually happening.

The bands also serve as natural stop-loss or profit-target references since they represent the distance price needs to move before the trend calculation changes. If you're long and the renko line is rising, you might place stops below the lower band on the theory that if price falls far enough to reverse the renko trend, your thesis is probably invalidated. Conversely, the upper band can mark levels where you'd expect the current brick to complete and potentially see some consolidation or pullback before the next brick forms.

What this really highlights is that renko's value isn't just in the brick visualization, it's in the underlying filtering mechanism. By extracting that mechanism and presenting it in a more traditional band format, you get access to renko's trend-following properties without needing to commit to the brick chart aesthetic or deal with the complications of overlaying brick drawings on a time-based chart. It's renko after all, so you get the trend filtering and directional clarity that makes renko useful, but packaged in a way that integrates more naturally with standard technical analysis workflows.
7 Nov 2025
Catatan Rilis
This update introduces a major internal redesign focused on performance, stability, and long-term reliability. The original version stored a continuously growing history array, which could eventually overflow on long charts. This issue has now been fully resolved. The script no longer uses any history array at all.

Renko processing has been rebuilt around a lightweight state-based model that tracks only what is required: the current brick, the held reference value, the upper and lower brick thresholds, the active trend direction, and the trend color. This produces the same visual output as before, but with a far cleaner and more efficient internal engine.

All three calculation modes—ATR, Percent, and Static—have been rewritten to operate on the new structure. Their behavior is now more consistent, smoother, and less prone to edge-case drift or accumulation errors. Smoothing, color gradients, and candle coloring continue to behave exactly as in the previous release.

A new input has also been added to allow custom selection of the close source used in Renko calculations, giving the script more flexibility for alternative data inputs.

Overall, this update delivers a much faster and safer version of Renko Bands while preserving the familiar visual structure and behavior.

source code
// This Pine Script® code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © The_Peaceful_Lizard

//@version=6
indicator("Renko Bands", overlay = true)


// HEAD {


// enums {


//@enum Renko brick size calculation methods.
//@field atr ATR-based brick size. Dynamic sizing based on volatility.
//@field percent Percentage-based brick size. Fixed percentage of current price.
//@field static Static absolute value brick size. Fixed price distance.
enum RenkoStyle
    atr = "ATR"
    percent = "Percent"
    static = "Static Value"


//@enum Direction of trend state.
//@field up Uptrend state.
//@field down Downtrend state.
//@field nan No trend / inactive.
enum Direction
    up = "Up"
    down = "Down"
    nan = "No Trend"


// enums }


// types {


//@type Renko brick tracking container with history and level management.
//@field history Array of historical Renko brick prices (most recent first).
//@field current Current smoothed Renko brick price.
//@field last Last confirmed Renko brick price (unsmoothed).
//@field high_level Upper threshold for next brick formation.
//@field low_level Lower threshold for next brick formation.
//@field direction Current trend direction (up/down/nan).
//@field colour Current gradient color based on price position and direction.
type Renko
    float current
    float hold
    float high_level
    float low_level
    Direction direction
    color colour


// types }


// helpers {


//@function Running Moving Average (RMA) for ATR calculation with bar-limited denominator.
//@param source Input value.
//@param length RMA period.
//@returns RMA value with alpha = 1 / min(length, bar_index + 1).
atr_rma(float source, float length)=>
    float alpha = 1 / math.min(length, bar_index + 1)
    float i_alpha = 1 - alpha
    float rma = source
    rma := source * alpha + nz(rma[1], rma) * i_alpha
    rma


//@function True range of current bar.
//@returns Max of: (high - low), abs(high - prev_close), abs(low - prev_close).
tr()=>
    math.max(high - low
             , math.abs(high - nz(close[1], math.max(open, close)))
             , math.abs(low - nz(close[1], math.min(open, close)))
             )


//@function Average True Range using RMA smoothing.
//@param period ATR period.
//@returns ATR(period).
atr(float period)=>
    atr_rma(tr(), period)


// helpers }


// renko {


//@function Initialize a new Renko object with default values.
//@returns Renko instance with history initialized to [open, open].
init_renko()=>
    var Renko renko = Renko.new(open, open, open, open, Direction.nan, na)
    renko


//@function Compute gradient color based on close position relative to Renko levels.
//@param self Renko instance.
//@param bullish Color for uptrend/bullish positioning.
//@param bearish Color for downtrend/bearish positioning.
//@returns Gradient color interpolated between bearish, neutral (chart.fg_color), and bullish.
method get_color(Renko self, color bullish, color bearish)=>
    var color colour = chart.fg_color
    float value = self.current
    float delta = value - nz(value[1], value)

    colour := switch self.direction
        Direction.up => color.from_gradient(close, self.low_level, self.current, chart.fg_color, bullish)
        Direction.down => color.from_gradient(close, self.current, self.high_level, bearish, chart.fg_color)
        => color.from_gradient(close, self.low_level, self.high_level, bearish, bullish)

    colour


//@function Update Renko using ATR-based brick sizing.
//@param self Renko instance.
//@param close_source Source for detecting when the price makes a new range.
//@param period ATR calculation period.
//@param multiplier ATR multiplier for brick size.
//@param hold_until_new If true, lock ATR value until new brick forms; if false, recalculate every bar.
//@returns Self with updated levels and history.
method atr(Renko self, float close_source, float period, float multiplier, bool hold_until_new)=>
    float atr = atr(period) * multiplier

    var float renko_atr = atr

    if not hold_until_new
        renko_atr := atr

    int new_bars = math.floor(math.abs(self.hold - close_source) / renko_atr)
    int direction = close_source > self.hold ? 1 : -1

    if new_bars > 0
        self.direction := direction == 1 ? Direction.up : Direction.down

        while new_bars > 0
            float new_open = self.hold + renko_atr * direction
            self.hold := new_open
            new_bars := math.floor(math.abs(new_open - close_source) / renko_atr)

        if hold_until_new
            renko_atr := atr

    self.current := self.hold
    self.high_level := self.hold + renko_atr
    self.low_level := self.hold - renko_atr

    self


//@function Update Renko using percentage-based brick sizing.
//@param self Renko instance.
//@param close_source Source for detecting when the price makes a new range.
//@param percent_change Percentage change required for new brick (e.g., 0.5 = 0.5%).
//@param hold_until_new If true, lock percentage base until new brick; if false, recalculate from each brick.
//@returns Self with updated levels and history.
method percent(Renko self, float close_source, float percent_change, bool hold_until_new)=>
    float percent = percent_change * 0.01

    float up_level = self.hold * (1 + percent)
    float down_level = self.hold * (1 - percent)

    self.high_level := up_level
    self.low_level := down_level

    float up_range = math.abs(self.hold - up_level)
    float down_range = math.abs(self.hold - down_level)

    bool new_up = close_source >= up_level
    bool new_down = close_source <= down_level

    if new_up
        self.direction := Direction.up

        int new_bars = math.floor(math.abs(close_source - self.hold) / up_range)

        while new_bars > 0
            up_range := hold_until_new ? up_range : math.abs(self.hold - self.hold * (1 + percent))
            float new = self.hold + up_range
            self.hold := new
            new_bars := math.floor(math.abs(close_source - self.hold) / up_range)

    else if new_down
        self.direction := Direction.down

        int new_bars = math.floor(math.abs(close_source - self.hold) / down_range)

        while new_bars > 0
            down_range := hold_until_new ? down_range : math.abs(self.hold - self.hold * (1 - percent))
            float new = self.hold - down_range
            self.hold := new
            new_bars := math.floor(math.abs(close_source - self.hold) / down_range)

    self.high_level := self.hold * (1 + percent)
    self.low_level := self.hold * (1 - percent)
    self.current := self.hold
    self


//@function Update Renko using static absolute brick sizing.
//@param self Renko instance.
//@param close_source Source for detecting when the price makes a new range.
//@param static_change Fixed price distance for brick formation (rounded to tick size).
//@returns Self with updated levels and history.
method static(Renko self, float close_source, float static_change)=>
    float static_distance = math.round_to_mintick(static_change)

    int new_bars = math.floor(math.abs(self.current - close_source) / static_distance)
    int direction = close_source > self.current ? 1 : -1

    while new_bars > 0
        self.direction := direction == 1 ? Direction.up : Direction.down

        float new = self.hold + static_distance * direction
        self.hold := new
        new_bars := math.floor(math.abs(self.hold - close_source) / static_distance)

    self.current := self.hold
    self.high_level := self.hold + static_distance
    self.low_level := self.hold - static_distance

    self


//@function Main Renko calculator with style dispatch and smoothing.
//@param close_source Source for detecting when the price makes a new range.
//@param atr_period ATR calculation period (used if style = atr).
//@param atr_multiplier ATR multiplier (used if style = atr).
//@param percent_change Percentage change threshold (used if style = percent).
//@param static_change Static price distance (used if style = static).
//@param hold_atr_until_new Lock ATR value until new brick (ATR mode).
//@param hold_percent_until_new Lock percentage base until new brick (percent mode).
//@param smoothing RMA smoothing period applied to current level and thresholds.
//@param bullish_color Color for bullish gradient.
//@param bearish_color Color for bearish gradient.
//@param style Renko calculation style (atr, percent, or static).
//@returns Renko object with calculated levels, smoothing applied, and color assigned.
renko(float close_source, float atr_period, float atr_multiplier, float percent_change, float static_change, bool hold_atr_until_new, bool hold_percent_until_new, float smoothing, color bullish_color, color bearish_color, simple RenkoStyle style)=>
    var Renko renko = init_renko()

    switch style
        RenkoStyle.atr => renko.atr(close_source, atr_period, atr_multiplier, hold_atr_until_new)
        RenkoStyle.percent => renko.percent(close_source, percent_change, hold_percent_until_new)
        RenkoStyle.static => renko.static(close_source, static_change)
        => renko

    renko.current := atr_rma(renko.current, smoothing)
    renko.high_level := atr_rma(renko.high_level, smoothing)
    renko.low_level := atr_rma(renko.low_level, smoothing)
    renko.colour := renko.get_color(bullish_color, bearish_color)

    renko


// renko }


// HEAD }


// BODY {


// inputs {


var const string global_group = "Global Settings"
var const string trend_color_inline = "trend_color_inline"

var const string close_source_tt = "The closing source for the renko calculations."

var const string renko_style_tt = "Renko brick size calculation method.\n\n"
 + "• ATR - Dynamic brick size based on Average True Range.\n"
 + "• Percent - Fixed percentage of current price for brick size.\n"
 + "• Static Value - Fixed absolute price distance for bricks."

var const string smoothing_tt = "RMA smoothing period for Renko levels.\n"
 + "Larger values create smoother, more stable bands.\n"
 + "Minimum value of 1 disables smoothing."

var const string static_color_tt = "Fixed color for Renko line when trend coloring is disabled.\n"
 + "Used when 'Use Trend Color' is turned off."

var const string trend_color_tt = "Gradient colors for trend-based coloring.\n"
 + "Renko line and candles interpolate between these colors based on price position.\n\n"
 + "• Left color - Bullish/uptrend color.\n"
 + "• Right color - Bearish/downtrend color."

var const string show_renko_line_tt = "Toggle display of the main Renko centerline.\n"
 + "The line tracks the current smoothed Renko brick price."

var const string use_polar_color_tt = "Enable dynamic gradient coloring based on trend.\n\n"
 + "• Enabled - Uses gradient between bullish and bearish colors.\n"
 + "• Disabled - Uses static color for Renko line."

var const string enable_candle_color_tt = "Apply trend-based gradient coloring to chart candles.\n"
 + "Colors candles based on position relative to Renko levels."

float close_source = input.source(close, "Close Source", tooltip = close_source_tt, group = global_group)
var RenkoStyle renko_style = input.enum(RenkoStyle.atr, "Style", tooltip = renko_style_tt, group = global_group)
float smoothing = input.float(1.25, "Smoothing", minval = 1, step = 0.125, tooltip = smoothing_tt, group = global_group)
color static_color = input.color(color.blue, "Static Color", tooltip = static_color_tt, group = global_group)
color bullish_color = input.color(#00FF00, "Trend Color", inline = trend_color_inline, group = global_group)
color bearish_color = input.color(#FF0000, "", inline = trend_color_inline, tooltip = trend_color_tt, group = global_group)
bool show_renko_line = input.bool(true, "Show Renko Line", tooltip = show_renko_line_tt, group = global_group)
bool use_polar_color = input.bool(true, "Use Trend Color", tooltip = use_polar_color_tt, group = global_group)
bool enable_candle_color = input.bool(true, "Candle Color", tooltip = enable_candle_color_tt, group = global_group)


var const string atr_group = "ATR Settings"
bool atr_active = renko_style == RenkoStyle.atr

var const string atr_period_tt = "Period for ATR calculation.\n"
 + "Longer periods create smoother, less sensitive brick sizing.\n\n"
 + "Only active when Style is set to ATR."

var const string atr_multiplier_tt = "Multiplier applied to ATR value for brick size.\n"
 + "Larger multipliers create wider bricks and less frequent updates.\n\n"
 + "Only active when Style is set to ATR."

var const string hold_atr_until_new_tt = "Control when ATR brick size recalculates.\n\n"
 + "• Enabled - Lock ATR value until a new brick forms (more stable).\n"
 + "• Disabled - Recalculate ATR every bar (more responsive).\n\n"
 + "Only active when Style is set to ATR."

float atr_period = input.float(14, "ATR Period", minval = 1, tooltip = atr_period_tt, active = atr_active, group = atr_group)
float atr_multiplier = input.float(2, "ATR Multiplier", minval = 0, step = 0.125, tooltip = atr_multiplier_tt, active = atr_active, group = atr_group)
bool hold_atr_until_new = input.bool(true, "Hold ATR Until New Renko", tooltip = hold_atr_until_new_tt, active = atr_active, group = atr_group)


var const string percent_group = "Percent Settings"
bool percent_active = renko_style == RenkoStyle.percent

var const string percent_change_tt = "Percentage change required for new brick formation.\n"
 + "For example, 0.5 means a 0.5% move from the last brick creates a new brick.\n\n"
 + "Only active when Style is set to Percent."

var const string hold_percent_until_new_tt = "Control when percentage base recalculates.\n\n"
 + "• Enabled - Lock percentage calculation to original brick price (compounding).\n"
 + "• Disabled - Recalculate percentage from each new brick (non-compounding).\n\n"
 + "Only active when Style is set to Percent."

float percent_change = input.float(0.5, "Percent Change", minval = 0.001, step = 0.001, tooltip = percent_change_tt, active = percent_active, group = percent_group)
bool hold_percent_until_new = input.bool(false, "Hold Percent Until New Renko", tooltip = hold_percent_until_new_tt, active = percent_active, group = percent_group)


var const string static_group = "Static Settings"
bool static_active = renko_style == RenkoStyle.static

var const string static_change_tt = "Fixed price distance for brick formation.\n"
 + "New bricks form when price moves this absolute amount from the last brick.\n"
 + "Value is automatically rounded to the instrument's minimum tick size.\n\n"
 + "Only active when Style is set to Static Value."

float static_change = input.float(25, "Static Change", minval = 1, step = 0.01, tooltip = static_change_tt, active = static_active, group = static_group)


// inputs }


// calc {


Renko renko = renko(close_source, atr_period, atr_multiplier, percent_change, static_change, hold_atr_until_new, hold_percent_until_new, smoothing, bullish_color, bearish_color, renko_style)
float renko_line = show_renko_line ? renko.current : na
color renko_color = use_polar_color ? renko.colour : static_color
color candle_color = enable_candle_color ? renko.colour : na


// calc }


// plot {


plot(renko_line, "Renko Line", renko_color, 2)
plot(renko.high_level, "Renko Max", bullish_color)
plot(renko.low_level, "Renko Min", bearish_color)
barcolor(candle_color)


// plot }


// BODY }

