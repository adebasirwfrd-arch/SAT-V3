5. Methode Mushir's Inside Candle Indicator
hints:This indicator detects inside candle formations on the chart’s current timeframe. It highlights when a candle’s range is fully engulfed by the previous candle’s range, provided the previous candle meets specific criteria.
How It Works ?
It shows the formation of inside candle on the charts to help in find trades.[NFA]

Mother Candle Validation
The previous candle must be a “leg candle” with a strong body and minimal wicks relative to its body size, ensuring a robust structure.

Inside Candle Detection
The current candle qualifies as an inside candle if:

Its high is ≤ the previous candle’s high.
Its low is ≥ the previous candle’s low.

Why Use This Indicator?
Adapts to the chart’s current timeframe—no manual adjustments needed.
Easily gives you the identification of inside candles
Minimalistic Design
Better results in trending market

How to use it?
- when the inside candle is formed there are certain conditions:
1. if the next candle first crosses the high of inside candle, look for a potential buy trade with RR as 2:1 while stoploss being just below the low of inside candle.
2. if the next candle first crosses the low of inside candle, look for a potential sell trade with RR as 2:1 while stoploss being just above the high of inside candle.
3. if 2:1 is achieved, then increase the partial target to 3:1 while bringing the stoploss to the entry point.
4. if the high is crossed first and then the low is crossed or vice versa then the trade is invalidated.

Happy Trading!

[NFA]

11 Mar 2025
Catatan Rilis
Now you can track every inside candle that is formed on the charts (no restrictions of candle body or wick)

Source code
//@version=6
indicator("Inside Candle Indicator (Chart Timeframe)", overlay=true, shorttitle="Inside Candle")

//———— Inside Candle Check (Current Candle) —————
// The current candle is an inside candle if its range is completely within the previous candle's range.
isInside = (high < high[1]) and (low > low[1])

//———— Plotting —————
// Plot a small black circle below the candle when an inside candle is detected.
plotshape(isInside, title="Inside Candle Detected", style=shape.circle, location=location.abovebar, color=color.black, size=size.tiny)

6. Methode Volume Spread Candle
hints:Volume Spread Candle is a Solid tool for VSA (Volume Spread Analysis).

█ Setting
please put on VSCandle above the candle chart.
█ Features
Candle color reflect volume size.
Back ground color reflect Spread size.
Warning Volume is relatively large volume compared to the Volume flow (up volume MA - down volume MA).
Yellow square mark appears when Warning volume.
Volume Density is Volume / Spread.
Yellow circle mark appears when large Volume Density.
█ Usage
Abnormal Volume and Spread hint what about to happen.

Source code
//@version=5
// Original scripts is 'Volume Flow V3'  by oh92
// You need [Chart settings] → [Appearance] → [bottom margin] is set 0 %.

indicator('Volume Spread Candle', 'VSCandle', overlay=true, scale=scale.none, max_boxes_count= 500, max_labels_count=500, max_lines_count=500, precision=0, behind_chart = false)

// group
g0 = "=======================⥑ Volume ⥏======================"
g1 = "=====================⥑ Key Volume ⥏==================="
g2 = "=====================⥑ Key Spread ⥏===================="
g2_1 = "============⥑ Consecutive bars Key Spread ⥏==========="
g3 = "==================⥑ Key Volume Spread ⥏=================" 
g4 = "===================⥑ General Settings ⥏=================="

// tooltip 
t11 = 'No Demand / No Supply is significantly below Volume MA.\nVol < Vol MA x Ratio'
t12 = 'Marks appear when current Volume is larger than average Volume x Ratio. Average Volume is difference of up volume and down volume (volume flow). Volume MA is used to calculate average Volume.\n\nupVol = upBar ? vol : 0 \ndnVol = dnBar ? vol : 0\nvf_dif = upVolMA - dnVolMA'
t13 = 'Back ground color or Triangle marks appear, when consecutive Increasing Volume candles.'
t21 = 'Use Very Large Volume Color.'
t22 = 'Use Warning Volume Color.'
t23 = 'The back ground style sometimes display crushed volume scale (ex. BTCUSD), in which case, please change the Top style and turn off Raise Bottom.'
t31 = 'Volume Density is Volume / delta price.\nMarks appear when current VD is larger than average VD x Ratio. Volume MA is used to calculate average VD.'
t41 = 'Max volume is searched in VolMA length x 4.'
t42 = 'Hide bottom part of volume.'


color BLACK = #000000FF

// ———————————————————— Inputs {
color  upLargeVolclr  = input.color(#056656,                 'Large Volume (above Volume MA)',                     inline='01', group=g0)
color  dnLargeVolclr  = input.color(#801922,                 '',                                                   inline='01', group=g0)
color  upsmallVolclr  = input.color(BLACK,                     'small Volume (below Volume MA)',                     inline='02', group=g0) 
color  dnsmallVolclr  = input.color(BLACK,                     '',                                                   inline='02', group=g0) 
string volMAtype      = input.string('EMA',                    ' 》Volume MA ', options=['SMA', 'EMA'],              inline='05', group=g0)
int    MAlength       = input.int(20,                          'length',                                             inline='05', group=g0)
color  volMAclr       = input.color(color.blue,              '',                                                   inline='05', group=g0)

bool   showVS         = input.bool(true,                       'Very Large Volume',                                  inline='10', group=g1)
bool   showvs         = true // input.bool(true,                       'S/R Boxes',                                          inline='10', group=g1)
color  upveryLargeVolclr = input.color(color.new(#00FF00, 0),  '',                                                 inline='10', group=g1)
color  dnveryLargeVolclr = input.color(color.new(#FF0000, 0),  '',                                                 inline='10', group=g1)
string showvstype     = input.string('None',                   ' S/R Boxes',                                         inline='10', group=g1, options=['None', 'Present', 'Histrical'], tooltip='Very Large Volume S/R boxes are Dotted boarder and colored background.')
VSscore = showvstype == 'Histrical' ? 1 : 0
// VSscore           = input.int(0, ' 0 is Present, 1 is Histrical', inline='10', minval=0, maxval=2, group=g1)
float  stddevVS       = input.float(4.,                        ' 》STDDEV', step=0.1,                                inline='11', group=g1)

bool   showNDNS       = input.bool(true,                       'Very small volume (ND/NS)',                          inline='13', group=g1) 
color  NDNSclr        = input.color(color.white,             '',                                                   inline='13', group=g1)
string NDtype         = input.string('① Easy',                 ' Type',                                              inline='13', group=g1, options=['① Easy', '② Strict', 'Both'])
float  ratioNDNS      = input.float(0.7,                       ' 》① Ratio', step=0.1,                               inline='14', group=g1, tooltip=t11)
float  wicksize       = input.float(0.5,                       ' 》② Wick size', step=0.1, minval=0, maxval=1,                inline='15', group=g1, tooltip= 'The VSA (Volume Spread Analysis) definition for No Demand and No supply is as follows: \nNo Demand (no buyers-potential short position): The Volume within the candle formation again has to be lower than the volume of the previous 2 candles. The candle has to close bullish (green body) and the next candle has to close bearish. There has to be some sort of rejection (pin or wick) at the high of the candle. If the candle closed at the top it would not be a no demand candle. \nNo Supply (no sellers-potential long position): The Volume within the candle formation has to be lower than the volume of the previous 2 candles. The candle has to close bearish (red body) and the next candle has to close bullish. There has to be some sort of rejection (pin or wick) at the low of the candle. If the candle closed at the bottom it would not be a no supply candle.')
bool   showVF         = input.bool(true,                       'Warning Volume',                                     inline='16', group=g1)
color  VSclr          = input.color(color.yellow,            '',                                                   inline='16', group=g1)
float  ratioVF        = input.float(4,                         ' 》Ratio', step=0.1,                                 inline='17', group=g1, tooltip=t12)
string marksVF        = input.string('▫ or ⬫',                 ' Marks',                                             inline='17', group=g1) //  ◻ or ⬫ or ▫
bool   showVolumeFlow = input.bool(false,                      'Volume Flow',                                        inline='17', group=g1)
int    VSlength       = MAlength
bool   showVSline     = false
bool   showDB         = input.bool(false,                      'Double Bumps',                                       inline='18', group=g1, tooltip=t13)

bool   showSS         = input.bool(true,                       'Very Large Spread(Sigma Spike)',                     inline='20', group=g2)//, tooltip='(I recommend Sigma Spike. ATR include Hige. ATR is better to find Large Doji bar)')
bool   showss         = true // input.bool(true,                       'S/R boxes',                                          inline='20', group=g2)
string showsstype     = input.string('Present',                ' S/R Boxes',                                         inline='20', group=g2, options=['None', 'Present', 'Histrical'], tooltip='Very Large Spread S/R boxes are thin solid boarder.')
SSscore = showsstype == 'Histrical' ? 1 : 0
// SSscore           = input.int(0, ' 0 is delete old', minval=0, maxval=2, inline='20', group=g2)
float  stddevSS       = input.float(2.5,                       ' 》STDDEV', step=0.1,                                inline='21', group=g2)
int    transpSS       = input.int(80,                          ' color transparency',                                inline='21', group=g2, tooltip=t21)
bool   showSF         = input.bool(true,                       'Warning Spread',                                     inline='22', group=g2, tooltip='Spread version of Warning Volume.')
float  ratioSF        = input.float(4.5,                       ' 》Ratio', step=0.1,                                 inline='23', group=g2)
int    transpSF       = input.int(70,                          '  color transparency',                               inline='23', group=g2, tooltip=t22)
string display_style  = input.string('back ground',            ' 》Display style', options=['back ground', 'Top'],   inline='24', group=g2, tooltip=t23)

OB                    = input.bool(false,                      'Order Block',                                                inline='bb',  group=g2_1)
color  OBclr          = input.color(color.purple,            '',                                                   inline='bb', group=g2_1)
showob                = true // input.bool(true,                    'S/R Boxes',                        inline='bb',  group=g2_1)
string showobtype     = input.string('None',                   ' S/R Boxes',                                         inline='bb', group=g2_1, options=['None', 'Present', 'Histrical'], tooltip='Order Block S/R boxes are OB colored thick solid boarder.')
OBscore = showobtype == 'Histrical' ? 1 : 0
// OBscore           = input.int(1, ' 0 is delete old', minval=0, maxval=2, inline='bb', group=g2_1)
ob                    = input.int        (4,                   ' 》consecutive bars',  minval=1,                      inline='aa', group=g2_1)
percmove              = input.float      (0.08,                ' Move %',   minval=0, step=0.1,                       inline='aa', group=g2_1, tooltip='close(consecutive bar) 4 - close(first bar) 1 = Move percentage')
obbullclr             = color.new(#00FF00, 70) // input.color      (color.new(color.white, 0),   ' 》Color Support',      inline='02', group=g21)
obbearclr             = color.new(#FF0000, 70) // input.color      (color.new(color.white, 0),   'Resistance',            inline='02', group=g21)
obbullbg              = color(na) // input.color      (color.new(color.white, 100),   ' 》BgColor Support',  inline='03', group=g21)
obbearbg              = color(na) // input.color      (color.new(color.white, 100),   'Resistance',          inline='03', group=g21)
oblinestyle           = line.style_solid // get_line_style(input.string('⎯⎯⎯', ' 》Line', options=['⎯⎯⎯', '----', '····'], inline='04', group=g21))
oblinewidth           = 4 // input.int        (4,                       ' 》Box border Width',     minval=1, maxval=5,   inline='04', group=g21)


bool   showVD         = input.bool(true,                       'Volume Density',                                     inline='30', group=g3, tooltip=t31)
color  VDclr          = input.color(color.yellow,            '',                                                   inline='30', group=g3)
float  ratioVD        = input.float(1.7,                       ' 》Ratio', step=0.1,                                 inline='31', group=g3) 
// int    VDboxheight    = input.int(10,                          ' Mark size',                                         inline='31', group=g3)
string marksVD        = input.string('○',                      ' Marks',                                             inline='31', group=g3) //  ◻

string showVolorCandle = input.string('Volume and Candle',     'Display', options=['Volume and Candle', 'Volume', 'Candle'],  inline='40', group=g4)
int show_V_C = showVolorCandle == 'Volume and Candle' ? 1 : showVolorCandle == 'Volume' ? 2 : 3
bool   difborderclr   = input.bool(false,                      'Different candle border color',                      inline='41', group=g4)
color  updifclr       = input.color(color.green,             '',                                                   inline='41', group=g4)
color  dndifclr       = input.color(color.red,               '',                                                   inline='41', group=g4)
int    volumescale    = input.int(25,                          'The height of Max Volume relative to the chart (%)', minval=0, maxval=100,  inline='42', group=g4, tooltip=t41)
bool   raisebottom    = true // input.bool(true,                       'Raise Bottom',                                       inline='43', group=g4)
int    hidevolume     = 0 // input.int(0,                           '     Hide Volume (%)',  minval=0, maxval=100,             inline='43', group=g4, tooltip=t42)
color  hideclr        = BLACK // input.color(BLACK,                     '',                                                   inline='43', group=g4)
// }

// ———————————————————— Global Date {
vol = volume
increaseVol = ta.rising(vol, 1)
upBar = close > open
dnBar = close < open

var float[] scaleMax = array.new_float()
// }


// ———————————————————— Functions {
// ---------- Very Large Volume (sigma spike) ----------
volMAVS = ta.sma(vol, MAlength) // use SMA for stdev
stdevVS = ta.stdev(vol, VSlength)
veryLargeVol = volMAVS + (stddevVS * stdevVS)

// sigmaVS_ = vol / stdevVS[1]
// VS = math.max(math.abs(sigmaVS_) - stddevVS, 0) > 0 and showVS

// conditions
bool VS = vol > veryLargeVol and showVS ? true : false // use bool
bool upVS = upBar and VS ? true : false 
bool dnVS = dnBar and VS ? true : false


// ---------- Warning Volume (Volume Flow) ----------
upVol = upBar ? vol : 0 
dnVol = dnBar ? vol : 0 
upVolMA = volMAtype == 'EMA' ? ta.ema(upVol, MAlength) : ta.sma(upVol, MAlength)
dnVolMA= volMAtype == 'EMA' ? ta.ema(dnVol, MAlength) : ta.sma(dnVol, MAlength)

vf_dif = upVolMA - dnVolMA
VFclr = vf_dif >= 0 ? color.new(upveryLargeVolclr, 60) : color.new(dnveryLargeVolclr, 60)

// conditions
float upVF = ta.crossover(upVol, upVolMA * ratioVF) and showVF ? vol + ta.sma(vol, 20)/10 : na // use float for plotchar Y-axis level
float dnVF = ta.crossover(dnVol, dnVolMA* ratioVF) and showVF ? vol + ta.sma(vol, 20)/10 : na 


// ---------- Volume Coloring ----------
volMA = volMAtype == 'EMA' ? ta.ema(vol, MAlength) : ta.sma(vol, MAlength) //select MA type
volOverMA = vol > volMA // decide Large volume  
volUnderMA = vol < volMA * ratioNDNS

normalVolbar = not (volOverMA and volUnderMA)  
upLargeVol = volOverMA and upBar
dnLargeVol = volOverMA and not upBar

NDNS = showNDNS and (NDtype == 'Both' or NDtype == '① Easy' ? volUnderMA : false)

volumeclr = NDNS ? NDNSclr 
  : upBar ? upVS ? upveryLargeVolclr : upLargeVol ? upLargeVolclr : upsmallVolclr 
  : dnVS ? dnveryLargeVolclr : dnLargeVol ? dnLargeVolclr : dnsmallVolclr

// NDNS ② Strict
ND = showNDNS and (NDtype == 'Both' or NDtype == '② Strict') and (dnBar and upBar[1] and vol[1] < vol[2] and vol[1] < vol[3] and high[1] - (close[1] > open[1] ? close[1] : open[1]) > (high[1] - low[1]) * 1/3)
NS = showNDNS and (NDtype == 'Both' or NDtype == '② Strict') and (upBar and dnBar[1] and vol[1] < vol[2] and vol[1] < vol[3] and (close[1] > open[1] ? open[1] : close[1]) - low[1] > (high[1] - low[1]) * 1/3)


// ---------- Double Bumps ----------
upBump = upBar and increaseVol
dnBump = dnBar and increaseVol

// Conditions
bool upDB = upBump and upBump[1] and barstate.isconfirmed and showDB ? true : false // use float for plotshape Y-axis level
bool dnDB = dnBump and dnBump[1] and barstate.isconfirmed and showDB ? true : false


// ---------- Very Large Spread (sigma spike) ----------
changeSS = close/close[1] - 1
stdevSS = ta.stdev(changeSS, MAlength)
sigma_ = changeSS / stdevSS[1]

// condition
bool SS = math.max(math.abs(sigma_) - stddevSS, 0) > 0 and showSS


// ---------- Warning Spread (Spread Flow) ----------
upSpd = open < close ? math.abs(close - open) : 0  
dnSpd = open > close ? math.abs(close - open) : 0 
upSpdMA = volMAtype == 'EMA' ? ta.ema(upSpd, MAlength) : ta.sma(upSpd, MAlength)
dnSpdMA = volMAtype == 'EMA' ? ta.ema(dnSpd, MAlength) : ta.sma(dnSpd, MAlength)

// conditions
float upSF = ta.crossover(upSpd, upSpdMA * ratioSF) and showSF ? vol : na // use float for plotshape Y-axis level
float dnSF = ta.crossover(dnSpd, dnSpdMA * ratioSF) and showSF ? vol : na 


// ---------- Volume Density ----------
hl = high - low 
VD = vol / hl

VDMA = volMAtype == 'EMA' ? ta.ema(VD, MAlength) : ta.sma(VD, MAlength)
stdevVD = ta.stdev(VD, VSlength) 

// conditions
int largeVD = VD > VDMA + stdevVD * ratioVD  ? 0 : na 
int smallVD = VD < VDMA - stdevVD * ratioVD  ? 0 : na


// ---------- Scale Adjustment ----------
array.push(scaleMax, vol) 
if array.size(scaleMax) > MAlength * 4 //bar number to find max volume
    array.shift(scaleMax)
    
scalebase = array.max(scaleMax) // get max large volume 
upperline = scalebase * 1 / volumescale * 100 // max large volume become 1/4 vertical level on chart
// }


// ———————————————————— Outputs {
plot(upperline, 'Scale Adjustment', color(na)) 

// Very Large Spread
bgcolor(SS ? display_style == 'back ground' ? upBar ? color.new(upveryLargeVolclr, transpSS) : color.new(dnveryLargeVolclr, transpSS) : na : na, title='Very Large Spread back ground color')
// if SS and display_style == 'back ground' and upBar 
//     line.new(bar_index, low - ta.tr, bar_index, high + ta.tr, xloc.bar_index, extend.both, color.new(upveryLargeVolclr, transpSS), line.style_dotted, 4)    
// if SS and display_style == 'back ground' and not upBar 
//     line.new(bar_index, low - ta.tr, bar_index, high + ta.tr, xloc.bar_index, extend.both, color.new(dnveryLargeVolclr, transpSS), line.style_dotted, 4)  
plotshape(SS and display_style == 'Top', 'Very Large Spread', shape.square, location.top, upBar ? color.new(upveryLargeVolclr, 0) : color.new(dnveryLargeVolclr, 0), size=size.tiny)

// Warning Spread
if upSF and display_style == 'back ground'
    line.new(bar_index, low - ta.tr, bar_index, high + ta.tr, xloc.bar_index, extend.both, color.new(VSclr, transpSF), line.style_dotted, 2)  // this sometimes makes broken volume scale 
if dnSF and display_style == 'back ground' 
    line.new(bar_index, low - ta.tr, bar_index, high + ta.tr, xloc.bar_index, extend.both, color.new(VSclr, transpSF), line.style_dotted, 2)

plotshape(upSF and display_style == 'Top', 'Up Warning Spread', shape.triangleup, location.top, VSclr, size=size.tiny) // plotshape can repaint realtime
plotshape(dnSF and display_style == 'Top', 'Dn Warning Spread', shape.triangledown, location.top, VSclr, size=size.tiny)
// plotchar(upSF and display_style == 'Top', char='🟩', location=location.top, size=size.tiny, title='Bull Sigma Spike') // plotchar can repaint realtime
// plotchar(dnSF and display_style == 'Top', char='🟥', location=location.top, size=size.tiny, title='Bear Sigma Spike')

// Volume Coloring
plot(show_V_C != 3 ? volMA : na, 'Volume MA', volMAclr)
plot(show_V_C != 3 ? vol : na, 'Volume stepline', difborderclr ? upBar ? updifclr : dndifclr : upBar ? upveryLargeVolclr : dnveryLargeVolclr, 3, plot.style_stepline)
plot(show_V_C != 3 ? vol : na, 'Volume', volumeclr, 4, plot.style_columns)
plot(show_V_C != 3 ? volMA * ratioNDNS : na, 'No Demand/Supply Volume MA', color.new(volMAclr, 70))

// hide volume
plot(show_V_C != 3 ? vol * hidevolume * 0.01 : na, 'Hide volume bottom', hideclr, 1, plot.style_columns)
// volume flow
plot(showVolumeFlow ? math.abs(vf_dif) * 2 : na, 'Volume Flow', VFclr, 1, plot.style_area) // volume flow x 2 


// ND/NS
plotchar(ND ? high : na,'No Demand', '⋂', location.abovebar, NDNSclr, - 1, 'ND', NDNSclr, true, size.tiny, force_overlay=true)
plotchar(NS ? low : na,'No Supply', '⋃', location.belowbar, NDNSclr, - 1, 'NS', NDNSclr, true, size.tiny, force_overlay=true)
plotshape(ND ? true : na, 'No Demand (strict)', shape.square, raisebottom ? location.belowbar : location.bottom, NDNSclr, offset= -1, size=size.tiny) // upDB is true or false. location.absolute cant be used since marks are always displayed.
plotshape(NS ? true : na, 'No Supply (strict)', shape.square, raisebottom ? location.belowbar : location.bottom, NDNSclr, offset= -1, size=size.tiny)

// Double Bumps
plotshape(show_V_C != 3 ? upDB : na, 'Up Double Bump', shape.triangleup, raisebottom ? location.belowbar : location.bottom, upveryLargeVolclr, size=size.tiny) // upDB is true or false. location.absolute cant be used since marks are always displayed.
plotshape(show_V_C != 3 ? dnDB : na, 'Dn Double Bump', shape.triangleup, raisebottom ? location.belowbar : location.bottom, dnveryLargeVolclr, size=size.tiny)

// Warning Volume
plotchar(show_V_C != 3 ? upVF : na, 'Up Warning Volume', marksVF, location.absolute, VSclr, size=size.small)
plotchar(show_V_C != 3 ? dnVF : na, 'Dn Warning Volume', marksVF, location.absolute, VSclr, size=size.small)

// Volume Density
plotshape(show_V_C != 3 and showVD ? largeVD : na, 'Volume Density', shape.circle, location.absolute, VDclr, size=size.tiny) // plotshape can repaint realtime // largeVD is 0 or na. 0 is displayed only when location.absolute. na is not displayed.
// Raise bottom for Volume Density
// if showVD and show_V_C != 3 
//     for i = 0 to 1000 by 20
//         label.new(bar_index[i], 0, '' + '\n' + '', color= color(na), style= label.style_label_center)// this make under space


// colored candle
plotcandle(show_V_C != 2 ? open : na, high, low , close 
  , color= NDNS ? NDNSclr 
  : upBar ? upVS ? upveryLargeVolclr : upLargeVol ? upLargeVolclr : upsmallVolclr
  : dnVS ? dnveryLargeVolclr : dnLargeVol ? dnLargeVolclr : dnsmallVolclr 
  , wickcolor= difborderclr ? upBar ? updifclr : dndifclr : upBar ? upVS ? upveryLargeVolclr : upLargeVolclr : dnVS ? dnveryLargeVolclr : dnLargeVolclr
  , bordercolor= difborderclr ? upBar ? updifclr : dndifclr : upBar ? upVS ? upveryLargeVolclr : upLargeVolclr : dnVS ? dnveryLargeVolclr : dnLargeVolclr
  , force_overlay= true)

plotcandle(show_V_C != 2 ? high : na, high, low, low // Warning Volume marks
  , color=color(na), wickcolor=color(na), bordercolor= upVF or dnVF ? upBar ? VSclr : VSclr : color(na)
  , force_overlay= true) 

plotchar(show_V_C != 2 and showVD and largeVD == 0 ? close : na, 'Volume Density Candle', marksVD, location.absolute, VDclr, size=size.tiny, force_overlay=true) 

// VDboxsize = syminfo.mintick*VDboxheight
// VDboxhigh = largeVD ? upBar ? high + VDboxsize*2 : low - VDboxsize : na
// VDboxlow = largeVD ? upBar ? high + VDboxsize : low - VDboxsize*2 : na

// plotcandle(show_V_C != 2 ? VDboxhigh : na, VDboxhigh, VDboxlow, VDboxlow // volume Density marks
//   , color= showVD and largeVD ? VDclr : color(na), wickcolor=color(na), bordercolor= showVD and largeVD ? VDclr : color(na)
//   , force_overlay= true) 
// }

// ————— Alert
// alertcondition(upDB or dnDB, 'TLD: Configured Markers', 'TLD Marker')


if raisebottom and barstate.isconfirmed
    for i = 0 to 1000 by 20
        label.new(bar_index[i], 0, '' + '\n' + '', color=color(na), style=label.style_label_center, textcolor=color.white, size=size.normal)// this make under space



////////////////////////// Support and Resistance
// group
g01= "===========⥑ Supply and Demand Zone Settings ⥏=========="
g011="===========⥑ Supply and Demand Zone Settings ⥏=========="
g11='Middle Pivot'
g21='Order Block (Large Move)'
g15='Sigma Spike and FVG (small Move)'
g20='FVG'
g30='Volume Spike'

//tooltips
t00 = 'Allows to display historical Structure or only the recent ones'

//Line Style function
get_line_style(style) =>
    out = switch style
        '⎯⎯⎯'  => line.style_solid  // for spread
        '----' => line.style_dashed // for spread and volume
        '····' => line.style_dotted // for volume

// ----------Inputs -------------
frontRun        = input.bool       (false,                   'Front Run Display',           inline='99',  group=g011, tooltip= 'Only Present Boxes. Histrical Boxes are not showed.')
width           = input.int        (2,                       ' 》width',                    inline='100', group=g011, minval=1)
offset          = input.int        (1,                       'offset',                      inline='100', group=g011, minval=0)

changelvl       = input.bool       (true,                    'Move box levels with price touch',         inline='00', group=g011, tooltip='Default Price touch is HighLow.')
CHL             = input.string     ('HighLow',               '', options=['Close', 'HighLow'],  inline='00', group=g011)
// wick            = input.bool       (true,                    'Use HighLow for price touch',               group=g01)
changecolor     = input.bool       (true,               'Change box border color with price touch',        inline="t",  group=g011) // , tooltip='need delete old box')
// testbgclr      = input.color      (color.new(color.red, 50),   'tested bg color',           inline="t",          group=g01)
testborderclr   = input.color      (color.new(color.white, 70),   '',        inline="t",              group=g011)
deleteline      = true // input.bool(true, 'Delete used lines (not for FrontRun)', group=g011)
maxlines        = 100//input.int(10,            'Maximum Lines Displayed',     minval=1, maxval=500,                  group=g2)


vsbullclr       = #056656 // input.color      (color.new(color.yellow, 100), ' 》Color Support',        inline= '08', group= g30)//color.new(color.green, 20)
vsbearclr       = #801922 // input.color      (color.new(color.yellow, 100), 'Resistance',              inline= '08', group= g30)//color.new(color.red, 20)
vsbullbg        = color.new(#00FF00, 85) // input.color      (color.new(color.yellow, 70), ' 》BgColor Support',    inline= '09', group= g30)//color.new(color.green, 20)
vsbearbg        = color.new(#FF0000, 85) // input.color      (color.new(color.yellow, 70), 'Resistance',            inline= '09', group= g30)//color.new(color.red, 20)
vslinestyle     = line.style_dotted // get_line_style(input.string('⎯⎯⎯',        ' 》Line', options=['⎯⎯⎯', '----', '····'], inline='10', group=g30))
vslinewidth     = 1 // input.int        (2,                       'Width',                       inline= '10', group= g30, minval= 1, maxval= 3)

sigmabullclr    = color.new(#00FF00, 70) // input.color      (color.new(color.white, 0),   ' 》Color  Support',    inline='22', group=g15)
sigmabearclr    = color.new(#FF0000, 70) // input.color      (color.new(color.white, 0),   'Resistance',           inline='22', group=g15)
sigmabullbg     = color(na) // input.color      (color.new(color.white, 50),   ' 》BgColor  Support',    inline='23', group=g15)
sigmabearbg     = color(na) // input.color      (color.new(color.white, 50),   'Resistance',             inline='23', group=g15)
sigmalinestyle  = line.style_solid // get_line_style(input.string('⎯⎯⎯',        ' 》Line', options=['⎯⎯⎯', '----', '····'], inline="24",   group=g15))
sslinewidth     = 1 // input.int        (1,                       'Width', minval= 1, maxval= 3,  inline="24", group= g15)


// ---------- function -----------
// Box draw function
control_box1(bullbear, pivotHighBoxArray, score) =>
    source = CHL == 'HighLow' ? bullbear ? high : low : close

    if array.size(pivotHighBoxArray) > 0
        for i = array.size(pivotHighBoxArray) - 1 to 0 by 1
            cutbox = array.get(pivotHighBoxArray, i)
            boxlowzone = box.get_bottom(cutbox)
            boxhighzone = box.get_top(cutbox)
            boxrightzone = box.get_right(cutbox) 
            
            if frontRun
                if na or bar_index + width - 1 + offset == boxrightzone and (bullbear ? boxlowzone < source : boxhighzone > source)
                    if changelvl and bullbear
                        box.set_bottom(cutbox, source)
                    if changelvl and not bullbear
                        box.set_top(cutbox, source)
                    if changecolor //and (zonetype == 0 or zonetype == 2)
                        box.set_border_color(cutbox, testborderclr)
                    // if changecolor and (zonetype == 1 or zonetype == 3)
                    //     box.set_bgcolor(cutbox, testbgclr)
                if na or bar_index + width - 1 + offset == boxrightzone and (bullbear ? boxhighzone > source : boxlowzone < source)//and not(high > boxhighzone) and not(high > boxlowzone and low < boxlowzone or high > boxhighzone and low < boxhighzone)
                    box.set_right(cutbox, bar_index + width + offset)
                    box.set_left(cutbox,  bar_index + offset)
                else if bar_index + width - 1 + offset == boxrightzone and (bullbear ? boxhighzone <= source : boxlowzone >= source) //and not(high > boxhighzone) and not(high > boxlowzone and low < boxlowzone or high > boxhighzone and low < boxhighzone)
                    box.delete(cutbox)

            else
                if na or bar_index - 1 == boxrightzone and (bullbear ? boxlowzone < source : boxhighzone > source)//and not(high > boxhighzone) and not(high > boxlowzone and low < boxlowzone or high > boxhighzone and low < boxhighzone)
                    if changelvl and boxhighzone > source and bullbear // fixed for old boxes
                        box.set_bottom(cutbox, source)
                    if changelvl and boxlowzone < source and not bullbear // fixed for old boxes 
                        box.set_top(cutbox, source)
                    if changecolor //and (zonetype == 0 or zonetype == 2)
                        box.set_border_color(cutbox, testborderclr)
                    // if changecolor and (zonetype == 1 or zonetype == 3)
                    //     box.set_bgcolor(cutbox, testbgclr)
                if na or bar_index - 1 == boxrightzone and (bullbear ? boxhighzone > source : boxlowzone < source)//and not(high > boxhighzone) and not(high > boxlowzone and low < boxlowzone or high > boxhighzone and low < boxhighzone)
                    box.set_right(cutbox, bar_index)
                else if deleteline and bar_index - 1 == boxrightzone and (bullbear ? boxhighzone <= source : boxlowzone >= source)//and not(high > boxhighzone) and not(high > boxlowzone and low < boxlowzone or high > boxhighzone and low < boxhighzone)
                    if array.get(score, i) == 0 
                        box.delete(cutbox)


// -------- Order Block function ----------- from 'Institutional OrderBlock Pressure', 'IOBP'
int offset2 = ob + 1
int bearcandle = 0
int bullcandle = 0
OBhigh      = high[offset2]
OBlow       = low[offset2]
OBbar_index = bar_index[offset2]

//Bearish/Bullish Candle Detection
for i = 1 to ob by 1
    bearcandle := bearcandle  + (close[i] < open[i] or math.abs(close[i] - open[i]) < ta.atr(20)/4 ? 1 : 0) // accept doji cnadles 
for i = 1 to ob by 1
    bullcandle := bullcandle  + (close[i] > open[i] or math.abs(close[i] - open[i]) < ta.atr(20)/4 ? 1 : 0)
//OrderBlock Calculation
abs     = math.abs(close[offset2] - close[1]) / close[offset2] * 100
absmove = abs >= percmove
OBbeardir = close[offset2] > open[offset2] // first bar
OBbulldir = close[offset2] < open[offset2]
//Conditions
bool bearOB = OBbeardir and (bearcandle == (ob)) and absmove and OB
bool bullOB  = OBbulldir and (bullcandle == (ob)) and absmove and OB

// ------------ sigma spike -------------
//conditions
bool bearSS  = dnBar and SS and showss and not (showsstype == 'None') ? true : false 
bool bullSS  = upBar and SS and showss and not (showsstype == 'None') ? true : false 

// --------- Volume spike ----------{
//Conditions
bool bearVS  = dnBar and VS and showvs and not (showvstype == 'None') ? true : false 
bool bullVS  = upBar and VS and showvs and not (showvstype == 'None') ? true : false 

// --------- plot ----------
bool bullbear  = na
int zonetype   = na
var box[]  bullbox     = array.new_box(0, na)
var box[]  bearbox     = array.new_box(0, na)
var int[]  bullboxscore     = array.new_int(0, na)
var int[]  bearboxscore     = array.new_int(0, na)

create_box(bullbear, zonehigh_, zonelow_, bgclr, borderclr, borderstyle, borderwidth, score) =>
    float zonehigh     = zonehigh_
    float zonelow      = zonelow_
    zone = bullbear ? bearbox : bullbox
    zonescore = bullbear ? bearboxscore : bullboxscore
    array.push(zone, box.new(frontRun ? bar_index + offset : bar_index, zonehigh, frontRun ? bar_index +  width+ offset : bar_index, zonelow
      , bgcolor=  bgclr
      , border_color= borderclr
      , border_style= borderstyle
      , border_width= borderwidth
      , force_overlay=true))
    array.push(zonescore, score)
    // zonetype := bearOB ? 0 : bearSS ? 1 : bearVS ? 2 : 3
    if array.size(zone) > maxlines // delete box
        box.delete(array.shift(zone))
        array.shift(zonescore)


plotchar(bearOB? high : na,'Order Block', '⩞', location.abovebar, OBclr, - ob - 1, 'OB', OBclr, true, size.tiny, force_overlay=true)
plotchar(bullOB? low : na, 'Order Block', '⩣', location.belowbar, OBclr, - ob - 1, 'OB', OBclr, true, size.tiny, force_overlay=true)
if bearOB and showob and not (showobtype == 'None')
    OBhigh := OBhigh < high[offset2 -1] ? high[offset2 -1] : OBhigh // search hihget high in 1st or 2nd OB bars
    create_box(false, OBhigh, OBlow, obbearbg, color.new(OBclr, 60), oblinestyle, oblinewidth, OBscore)
if bullOB and showob and not (showobtype == 'None')
    OBlow := OBlow > low[offset2 -1] ? low[offset2 -1] : OBlow // search lowest low in 1st or 2nd OB bars
    create_box(true, OBhigh, OBlow, obbullbg, color.new(OBclr, 60), oblinestyle, oblinewidth, OBscore)

if bearSS[1] // for not count next bar as touched
    create_box(false, high[1], high, sigmabearbg, sigmabearclr, sigmalinestyle, sslinewidth, SSscore)
if bullSS[1] 
    create_box(true, low, low[1], sigmabullbg, sigmabullclr, sigmalinestyle, sslinewidth, SSscore)

if bearVS[1] and high[1] > high // need avoid mistake zone
    create_box(false, high[1], high, vsbearbg, vsbearclr, vslinestyle, vslinewidth, VSscore)
if bullVS[1] and low[1] < low
    create_box(true, low, low[1], vsbullbg, vsbullclr, vslinestyle, vslinewidth, VSscore)
// if bearVS
//     create_box(false, high, low, vsbearbg, vsbearclr, vslinestyle, vslinewidth, 0)
// if bullVS
//     create_box(true, high, low, vsbullbg, vsbullclr, vslinestyle, vslinewidth, 0)


control_box1(false, bearbox, bearboxscore)
control_box1(true, bullbox, bullboxscore)

7. Methode HTF Candles
hints:Features
• 15-minute, 1-hour, 4-hour, and previous-day daily candles
• Visualizes the remaining time and number of candles from the lower timeframe that form the next higher-timeframe candle.”

Source code
//@version=6
indicator('MTF Candles', overlay = true)
  
show_mtc = input.bool(true, "Show MTF Candles")
candle_gap = 6
 
getTimeComponents(ms) => 
    totalSeconds = math.floor(ms / 1000)
    [math.floor(totalSeconds / 60), totalSeconds % 60]


draw_candle(idx, o, h, l, c, normal_color) =>
    col = o > c ? color.red : color.green
    if not normal_color
        col:= o > c ? color.new(color.red,50) : color.aqua
    line.delete(line.new(idx, h, idx, math.max(o, c), color=col, width=1)[1])
    line.delete(line.new(idx, math.min(o, c), idx, l, color=col, width=1)[1])
    line.delete(line.new(idx, o, idx, c, color=col, width=3)[1])

draw_5m_candles(base_x, normal_color) =>
    [o0, h0, l0, c0] = request.security(syminfo.tickerid, "5", [open[0], high[0], low[0], close[0]])
    [o1, h1, l1, c1] = request.security(syminfo.tickerid, "5", [open[1], high[1], low[1], close[1]])
    [o2, h2, l2, c2] = request.security(syminfo.tickerid, "5", [open[2], high[2], low[2], close[2]])
    [o3, h3, l3, c3] = request.security(syminfo.tickerid, "5", [open[3], high[3], low[3], close[3]])
    [o4, h4, l4, c4] = request.security(syminfo.tickerid, "5", [open[4], high[4], low[4], close[4]])
    draw_candle(base_x + 0, o4, h4, l4, c4, normal_color)
    draw_candle(base_x + 1, o3, h3, l3, c3, normal_color)
    draw_candle(base_x + 2, o2, h2, l2, c2, normal_color)
    draw_candle(base_x + 3, o1, h1, l1, c1, normal_color)
    draw_candle(base_x + 4, o0, h0, l0, c0, normal_color)
    math.max(h0, h1, h2, h3, h4)

draw_15_candles(tf, base_x, label_text, normal_color) =>
    [o0, h0, l0, c0] = request.security(syminfo.tickerid, tf, [open[0], high[0], low[0], close[0]])
    [o1, h1, l1, c1] = request.security(syminfo.tickerid, tf, [open[1], high[1], low[1], close[1]])
    [o2, h2, l2, c2] = request.security(syminfo.tickerid, tf, [open[2], high[2], low[2], close[2]])
    [o3, h3, l3, c3] = request.security(syminfo.tickerid, tf, [open[3], high[3], low[3], close[3]])
    [o4, h4, l4, c4] = request.security(syminfo.tickerid, tf, [open[4], high[4], low[4], close[4]])
    draw_candle(base_x + 0, o4, h4, l4, c4, normal_color)
    draw_candle(base_x + 1, o3, h3, l3, c3, normal_color)
    draw_candle(base_x + 2, o2, h2, l2, c2, normal_color)
    draw_candle(base_x + 3, o1, h1, l1, c1, normal_color)
    draw_candle(base_x + 4, o0, h0, l0, c0, normal_color)
    math.max(h0, h1, h2, h3, h4)

draw_1h_candles(tf, base_x, label_text, normal_color) =>
    [o0, h0, l0, c0] = request.security(syminfo.tickerid, tf, [open[0], high[0], low[0], close[0]])
    [o1, h1, l1, c1] = request.security(syminfo.tickerid, tf, [open[1], high[1], low[1], close[1]])
    [o2, h2, l2, c2] = request.security(syminfo.tickerid, tf, [open[2], high[2], low[2], close[2]])
    [o3, h3, l3, c3] = request.security(syminfo.tickerid, tf, [open[3], high[3], low[3], close[3]])
    draw_candle(base_x + 0, o3, h3, l3, c3, normal_color)
    draw_candle(base_x + 1, o2, h2, l2, c2, normal_color)
    draw_candle(base_x + 2, o1, h1, l1, c1, normal_color)
    draw_candle(base_x + 3, o0, h0, l0, c0, normal_color)
    math.max(h0, h1, h2, h3)

draw_4h_candles(base_x, normal_color) =>
    [o0, h0, l0, c0] = request.security(syminfo.tickerid, "240", [open[0], high[0], low[0], close[0]])
    [o1, h1, l1, c1] = request.security(syminfo.tickerid, "240", [open[1], high[1], low[1], close[1]])
    [o2, h2, l2, c2] = request.security(syminfo.tickerid, "240", [open[2], high[2], low[2], close[2]])
    draw_candle(base_x + 0, o2, h2, l2, c2, normal_color)
    draw_candle(base_x + 1, o1, h1, l1, c1, normal_color)
    draw_candle(base_x + 2, o0, h0, l0, c0, normal_color)
    math.max(h0, h1, h2)

show_time_labels(base_x, max_high) =>
    label_height = max_high * 1.005

    time_left_4h = request.security(syminfo.tickerid, "240", time_close) - timenow
    [min4h, sec4h] = getTimeComponents(math.max(0, time_left_4h))
    label.delete(label.new(base_x + 1, label_height, str.format("{0}:{1}:{2}", math.floor(min4h / 60), min4h%60, sec4h), textcolor=color.lime, style=label.style_none, size=size.normal)[1])

    time_left_1h = request.security(syminfo.tickerid, "60", time_close) - timenow
    [min1h, sec1h] = getTimeComponents(math.max(0, time_left_1h))
    label.delete(label.new(base_x + 6, label_height, str.format("{0}:{1}", min1h, sec1h), textcolor=color.lime, style=label.style_none, size=size.normal)[1])

    time_left_15m = request.security(syminfo.tickerid, "15", time_close) - timenow
    [min15m, sec15m] = getTimeComponents(math.max(0, time_left_15m))
    label.delete(label.new(base_x + 12, label_height, str.format("{0}:{1}", min15m, sec15m), textcolor=color.lime, style=label.style_none, size=size.normal)[1])

    time_left_5m = request.security(syminfo.tickerid, "5", time_close) - timenow
    [min5m, sec5m] = getTimeComponents(math.max(0, time_left_5m))
    label.delete(label.new(base_x + 18, label_height, str.format("{0}:{1}", min5m, sec5m), textcolor=color.lime, style=label.style_none, size=size.normal)[1])

if barstate.islast and show_mtc
    base_x = bar_index + 3
    offset = 0

    h_4h = draw_4h_candles(base_x + offset, false)
    offset := offset + 4

    h_1h = draw_1h_candles("60", base_x + offset, "1h", true)
    offset := offset + 5

    h_15m = draw_15_candles("15", base_x + offset, "15m", false)
    offset := offset + candle_gap

    h_5m = draw_5m_candles(base_x + offset, true)

    max_high = math.max(h_4h, h_1h, h_15m, h_5m)

    show_time_labels(base_x, max_high)
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

timeframe_input = input.timeframe("D", "Timeframe", options=["1", "3", "5", "15", "30", "45", "60", "90", "120", "180", "240", "300", "360", "480", "600", "720", "840", "D", "2D", "3D", "4D", "5D", "W", "2W", "3W", "M", "2M", "3M", "4M", "6M", "12M"])
bars_back = input.int(1, "Target Candle(offset from the last bar)", minval=1, group='----------------------------------------- OLHC Region')
extend_left = input.bool(true, "Extend the range to the left")
line_width = 2

var line line_open = na
var line line_high = na
var line line_low = na
var line line_close = na
var box box_upper = na
var box box_lower = na

tf_open = request.security(syminfo.tickerid, timeframe_input, open[bars_back], lookahead=barmerge.lookahead_on)
tf_high = request.security(syminfo.tickerid, timeframe_input, high[bars_back], lookahead=barmerge.lookahead_on)
tf_low = request.security(syminfo.tickerid, timeframe_input, low[bars_back], lookahead=barmerge.lookahead_on)
tf_close = request.security(syminfo.tickerid, timeframe_input, close[bars_back], lookahead=barmerge.lookahead_on)

line.delete(line_open)
line.delete(line_high)
line.delete(line_low)
line.delete(line_close)
box.delete(box_upper)
box.delete(box_lower)

c_oc = color.new(color.green, 100)
c_hl = color.new(color.white, 100)
c_box = color.new(color.gray, 75)
extend_option = extend_left ? extend.left : extend.none

line_open := line.new(bar_index + 5, tf_open, bar_index + 15, tf_open, color=c_oc, width=line_width, style=line.style_solid, extend=extend_option)
line_close := line.new(bar_index + 5, tf_close, bar_index + 15, tf_close, color=c_oc, width=line_width, style=line.style_solid, extend=extend_option)
line_high := line.new(bar_index + 5, tf_high, bar_index + 15, tf_high, color=c_hl, width=line_width, style=line.style_dotted, extend=extend_option)
line_low := line.new(bar_index + 5, tf_low, bar_index + 15, tf_low, color=c_hl, width=line_width, style=line.style_dotted, extend=extend_option)

if tf_close < tf_open
    box_upper := box.new(bar_index + 5, tf_high, bar_index + 15, tf_open, border_color=na, bgcolor=c_box, extend=extend_option)
    box_lower := box.new(bar_index + 5, tf_close, bar_index + 15, tf_low, border_color=na, bgcolor=c_box, extend=extend_option)
else
    box_upper := box.new(bar_index + 5, tf_high, bar_index + 15, tf_close, border_color=na, bgcolor=c_box, extend=extend_option)
    box_lower := box.new(bar_index + 5, tf_open, bar_index + 15, tf_low, border_color=na, bgcolor=c_box, extend=extend_option)

