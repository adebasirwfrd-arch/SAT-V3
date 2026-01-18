import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ccxt

# Setup Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import Config

# Page Config
st.set_page_config(
    page_title="SAT-V3 MULTI-CRYPTO",
    page_icon="🔱",
    layout="wide"
)

# Clean CSS (white background)
st.markdown("""
<style>
    .bullish { color: #26a69a; font-weight: bold; }
    .bearish { color: #ef5350; font-weight: bold; }
    .neutral { color: #ffa726; font-weight: bold; }
    .param-row { font-size: 0.85em; display: flex; justify-content: space-between; margin: 3px 0; padding: 2px; }
    div.stButton > button { border-radius: 4px; font-weight: bold; font-size: 0.85em; }
</style>
""", unsafe_allow_html=True)

# File Paths
DATA_FILE = Config.LIVE_DATA_FILE
CMD_FILE = Config.COMMANDS_FILE

# Council Strategy Templates
COUNCIL_STRATEGIES = {
    "📈 Trend Master": {
        "name": "Trend Master",
        "indicators": ["EMA 200", "Ichimoku Cloud"],
        "description": "Trend following with EMA 200 and Ichimoku"
    },
    "🏗️ Structure Master": {
        "name": "Structure Master", 
        "indicators": ["Support/Resistance", "Donchian"],
        "description": "Support/Resistance zones with Donchian Channels"
    },
    "📊 Volume Master": {
        "name": "Volume Master",
        "indicators": ["OBV", "Volume Bars"],
        "description": "Volume analysis with OBV indicator"
    },
    "🦈 Smart Money": {
        "name": "Smart Money",
        "indicators": ["FVG", "Order Block"],
        "description": "Fair Value Gap and Order Block detection"
    },
    "🕯️ Pattern Master": {
        "name": "Pattern Master",
        "indicators": ["Candlestick Patterns"],
        "description": "Candlestick pattern recognition"
    },
    "📐 Geometry Master": {
        "name": "Geometry Master",
        "indicators": ["Fibonacci"],
        "description": "Fibonacci retracement levels"
    },
    "🎯 Indicator Master": {
        "name": "Indicator Master",
        "indicators": ["RSI", "MACD", "Stochastic"],
        "description": "Classic oscillators"
    },
    "⚡ Full Analysis": {
        "name": "Full Analysis",
        "indicators": ["All"],
        "description": "Complete indicator suite"
    }
}

@st.cache_resource
def get_exchange():
    try:
        return ccxt.binance({'options': {'defaultType': 'spot'}})
    except:
        return None

exchange = get_exchange()

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

@st.cache_data(ttl=60)
def fetch_ohlcv(symbol, timeframe='1h', limit=100):
    try:
        if exchange:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
    except:
        pass
    
    # Fallback simulation - different data per symbol AND timeframe
    coin = symbol.split('/')[0]
    
    # Create unique seed per coin + timeframe combination
    tf_multiplier = {'15m': 1, '1h': 2, '4h': 3, '1d': 4}.get(timeframe, 1)
    seed = (hash(coin) % 10000) * tf_multiplier
    np.random.seed(seed)
    
    # Different frequency per timeframe
    freq_map = {'15m': '15min', '1h': '1h', '4h': '4h', '1d': '1D'}
    freq = freq_map.get(timeframe, '1h')
    
    # Different volatility per timeframe
    vol_map = {'15m': 0.005, '1h': 0.015, '4h': 0.03, '1d': 0.05}
    volatility_factor = vol_map.get(timeframe, 0.015)
    
    dates = pd.date_range(end=datetime.now(), periods=limit, freq=freq)
    base = {'BTC': 95000, 'ETH': 3300, 'SOL': 140, 'BNB': 600, 'TON': 6, 'XRP': 2}.get(coin, 100)
    returns = np.random.randn(limit) * volatility_factor
    prices = base * np.exp(np.cumsum(returns))
    
    # Generate realistic OHLC with both bullish and bearish candles
    ohlc_data = []
    for i, close in enumerate(prices):
        is_bullish = np.random.random() > 0.45
        candle_vol = close * volatility_factor * np.random.random()
        
        if is_bullish:
            open_price = close - candle_vol
            high = close + candle_vol * 0.5
            low = open_price - candle_vol * 0.3
        else:
            open_price = close + candle_vol
            high = open_price + candle_vol * 0.3
            low = close - candle_vol * 0.5
        
        ohlc_data.append({
            'timestamp': dates[i],
            'open': open_price,
            'high': max(high, open_price, close),
            'low': min(low, open_price, close),
            'close': close,
            'volume': np.random.randint(1000, 10000)
        })
    
    return pd.DataFrame(ohlc_data)

def calculate_indicators(df):
    """Calculate all technical indicators"""
    # Moving Averages
    df['EMA20'] = df['close'].ewm(span=20).mean()
    df['EMA50'] = df['close'].ewm(span=50).mean()
    df['EMA200'] = df['close'].ewm(span=200, min_periods=50).mean()
    df['SMA20'] = df['close'].rolling(20).mean()
    
    # Bollinger Bands
    df['BB_mid'] = df['close'].rolling(20).mean()
    df['BB_std'] = df['close'].rolling(20).std()
    df['BB_upper'] = df['BB_mid'] + 2 * df['BB_std']
    df['BB_lower'] = df['BB_mid'] - 2 * df['BB_std']
    
    # Donchian Channels (Structure Master)
    df['DC_upper'] = df['high'].rolling(20).max()
    df['DC_lower'] = df['low'].rolling(20).min()
    df['DC_mid'] = (df['DC_upper'] + df['DC_lower']) / 2
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    
    # MACD
    df['MACD'] = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()
    df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    
    # OBV (Volume Master)
    df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    
    # Stochastic
    low14 = df['low'].rolling(14).min()
    high14 = df['high'].rolling(14).max()
    df['Stoch_K'] = 100 * (df['close'] - low14) / (high14 - low14)
    df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()
    
    # Fibonacci Levels (Geometry Master)
    period_high = df['high'].max()
    period_low = df['low'].min()
    diff = period_high - period_low
    df['Fib_0'] = period_low
    df['Fib_236'] = period_low + 0.236 * diff
    df['Fib_382'] = period_low + 0.382 * diff
    df['Fib_500'] = period_low + 0.5 * diff
    df['Fib_618'] = period_low + 0.618 * diff
    df['Fib_786'] = period_low + 0.786 * diff
    df['Fib_1'] = period_high
    
    return df

def create_chart(df, symbol, strategy="⚡ Full Analysis"):
    """Create TradingView-style chart based on selected strategy"""
    
    df = calculate_indicators(df)
    
    # Determine chart layout based on strategy
    if strategy in ["📊 Volume Master"]:
        rows, heights = 3, [0.6, 0.2, 0.2]
        titles = (symbol, 'Volume', 'OBV')
    elif strategy in ["🎯 Indicator Master"]:
        rows, heights = 4, [0.5, 0.15, 0.15, 0.2]
        titles = (symbol, 'RSI', 'Stochastic', 'MACD')
    else:
        rows, heights = 3, [0.6, 0.2, 0.2]
        titles = (symbol, 'Volume', 'RSI')
    
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.02, row_heights=heights, subplot_titles=titles)
    
    # === MAIN CANDLESTICK ===
    # TradingView colors: Green #26a69a, Red #ef5350
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            name='Price',
            increasing=dict(line=dict(color='#26a69a'), fillcolor='#26a69a'),
            decreasing=dict(line=dict(color='#ef5350'), fillcolor='#ef5350')
        ), row=1, col=1
    )
    
    # === STRATEGY-SPECIFIC INDICATORS ===
    
    if strategy in ["📈 Trend Master", "⚡ Full Analysis"]:
        # EMA 200
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA200'], name='EMA 200',
                                  line=dict(color='#ff9800', width=2)), row=1, col=1)
        # EMA 50
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA50'], name='EMA 50',
                                  line=dict(color='#2196f3', width=1.5)), row=1, col=1)
    
    if strategy in ["🏗️ Structure Master", "⚡ Full Analysis"]:
        # Donchian Channels
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['DC_upper'], name='Donchian Upper',
                                  line=dict(color='#4caf50', width=1, dash='dot')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['DC_lower'], name='Donchian Lower',
                                  line=dict(color='#f44336', width=1, dash='dot'),
                                  fill='tonexty', fillcolor='rgba(100,100,100,0.1)'), row=1, col=1)
    
    if strategy in ["📐 Geometry Master", "⚡ Full Analysis"]:
        # Fibonacci Lines
        fib_levels = [('Fib_236', '#ffeb3b', '23.6%'), ('Fib_382', '#ff9800', '38.2%'),
                      ('Fib_500', '#03a9f4', '50%'), ('Fib_618', '#4caf50', '61.8%')]
        for col, color, label in fib_levels:
            fig.add_hline(y=df[col].iloc[-1], line_dash="dash", line_color=color, 
                         annotation_text=label, row=1, col=1)
    
    if strategy in ["📈 Trend Master", "🏗️ Structure Master", "⚡ Full Analysis"]:
        # Bollinger Bands
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BB_upper'], name='BB Upper',
                                  line=dict(color='gray', width=1, dash='dash'), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BB_lower'], name='BB Lower',
                                  line=dict(color='gray', width=1, dash='dash'),
                                  fill='tonexty', fillcolor='rgba(128,128,128,0.1)', showlegend=False), row=1, col=1)
    
    # === VOLUME ===
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['close'], df['open'])]
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['volume'], name='Volume',
                          marker_color=colors, opacity=0.7, showlegend=False), row=2, col=1)
    
    if strategy == "📊 Volume Master":
        # OBV
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['OBV'], name='OBV',
                                  line=dict(color='#9c27b0', width=1.5)), row=3, col=1)
    
    # === OSCILLATORS ===
    if strategy in ["🎯 Indicator Master"]:
        # RSI
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['RSI'], name='RSI',
                                  line=dict(color='#9c27b0', width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=2, col=1)
        
        # Stochastic
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['Stoch_K'], name='%K',
                                  line=dict(color='#2196f3', width=1)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['Stoch_D'], name='%D',
                                  line=dict(color='#ff9800', width=1)), row=3, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD'], name='MACD',
                                  line=dict(color='#2196f3', width=1.5)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD_signal'], name='Signal',
                                  line=dict(color='#ff5722', width=1.5)), row=4, col=1)
        macd_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df['MACD_hist']]
        fig.add_trace(go.Bar(x=df['timestamp'], y=df['MACD_hist'], name='Histogram',
                              marker_color=macd_colors, opacity=0.6), row=4, col=1)
    else:
        # Default RSI
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['RSI'], name='RSI',
                                  line=dict(color='#9c27b0', width=1.5)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=3, col=1)
    
    # === LAYOUT (White theme with dark chart) ===
    fig.update_layout(
        template='plotly_dark',
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center", font=dict(size=10)),
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=50, t=30, b=30),
        paper_bgcolor='#1e222d',
        plot_bgcolor='#1e222d',
        uirevision='constant',
        hovermode='x unified'
    )
    
    # Grid styling
    for i in range(1, rows + 1):
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#363a45', row=i, col=1)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#363a45', row=i, col=1)
    
    return fig

def send_command(symbol, action):
    cmd = {"command": action, "symbol": symbol, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "executed": False}
    os.makedirs(os.path.dirname(CMD_FILE), exist_ok=True)
    with open(CMD_FILE, 'w') as f:
        json.dump(cmd, f)
    st.toast(f"✅ {action} {symbol}", icon="🚀")

# === SIDEBAR ===
st.sidebar.title("🔱 SAT-V3")
st.sidebar.caption("🔴 LIVE MODE")

data = load_data()
if not data:
    st.warning("⏳ Run: python src/main.py")
    st.stop()

port = data.get('portfolio', {})
st.sidebar.metric("Equity", f"${port.get('equity', 10000):,.2f}")
st.sidebar.metric("Cash", f"${port.get('cash', 10000):,.2f}")
st.sidebar.metric("PnL", f"${port.get('realized_pnl', 0):,.2f}")
if st.sidebar.button("🛑 LIQUIDATE", type="secondary"):
    send_command("ALL", "LIQUIDATE_ALL")

# === MAIN ===
st.title("🔱 SAT-V3 Command Center")

assets = data.get('assets', {})

# Asset Cards
if assets:
    row1 = st.columns(3)
    row2 = st.columns(3)
    cols = row1 + row2
    
    for i, (coin, info) in enumerate(list(assets.items())[:6]):
        with cols[i]:
            with st.container(border=True):
                h1, h2 = st.columns([1, 1.5])
                h1.markdown(f"### {coin}")
                price = info.get('price', 0)
                change = info.get('price_change', 0)
                h2.metric("Price", f"${price:,.2f}", f"{change:+.2f}", label_visibility="collapsed")
                
                score = info.get('council_score', 50)
                signal = info.get('signal', 'NEUTRAL')
                color = "#26a69a" if score >= 60 else "#ef5350" if score <= 40 else "#ffa726"
                
                st.markdown(f"<div style='text-align:center;font-size:2em;color:{color};font-weight:bold'>{int(score)}</div>", unsafe_allow_html=True)
                signal_class = "bullish" if "BUY" in signal else "bearish" if "SELL" in signal else "neutral"
                st.markdown(f"<div style='text-align:center' class='{signal_class}'>{signal}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Parameters
                rsi = info.get('rsi', 50)
                atr = info.get('atr', 0)
                sentiment = info.get('sentiment', 'NORMAL')
                regime = info.get('regime', 'NEUTRAL')
                
                regime_color = "#26a69a" if regime == "BULLISH" else "#ef5350"
                sent_color = "#26a69a" if "HYPE" in sentiment else "#ef5350" if "FEAR" in sentiment else "#ffa726"
                
                st.markdown(f"""
                <div style='font-size:0.85em'>
                    <div style='display:flex;justify-content:space-between'><span>RSI:</span><b>{rsi:.1f}</b></div>
                    <div style='display:flex;justify-content:space-between'><span>ATR:</span><b>{atr:.2f}</b></div>
                    <div style='display:flex;justify-content:space-between'><span>Sentiment:</span><span style='color:{sent_color}'><b>{sentiment}</b></span></div>
                    <div style='display:flex;justify-content:space-between'><span>Regime:</span><span style='color:{regime_color}'><b>{regime}</b></span></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # 7 Council Display
                st.caption("⚔️ The 7 Council")
                council_names = ["Trend", "Struct", "Vol", "Smart", "Patt", "Geom", "Indic"]
                
                np.random.seed(hash(coin) % 1000)
                council_scores = [int(max(0, min(100, score + np.random.randint(-25, 25)))) for _ in council_names]
                
                # Display council in 2 rows
                council_text = " | ".join([f"{('🟢' if s >= 60 else '🔴' if s <= 40 else '🟡')} {n}:{s}" for n, s in zip(council_names[:4], council_scores[:4])])
                st.caption(council_text)
                council_text2 = " | ".join([f"{('🟢' if s >= 60 else '🔴' if s <= 40 else '🟡')} {n}:{s}" for n, s in zip(council_names[4:], council_scores[4:])])
                st.caption(council_text2)
                
                # Mini Candlestick Chart (TradingView style)
                symbol = info.get('symbol', f'{coin}/USDT')
                mini_df = fetch_ohlcv(symbol, '1h', 24)
                if mini_df is not None and len(mini_df) > 5:
                    # Calculate MA
                    mini_df['MA'] = mini_df['close'].rolling(10).mean()
                    
                    # Create mini candlestick chart
                    mini_fig = go.Figure()
                    
                    # Candlestick
                    mini_fig.add_trace(go.Candlestick(
                        x=mini_df['timestamp'],
                        open=mini_df['open'],
                        high=mini_df['high'],
                        low=mini_df['low'],
                        close=mini_df['close'],
                        increasing=dict(line=dict(color='#26a69a', width=1), fillcolor='#26a69a'),
                        decreasing=dict(line=dict(color='#ef5350', width=1), fillcolor='#ef5350'),
                        showlegend=False
                    ))
                    
                    # MA Line
                    mini_fig.add_trace(go.Scatter(
                        x=mini_df['timestamp'],
                        y=mini_df['MA'],
                        mode='lines',
                        line=dict(color='#ffa726', width=1.5),
                        showlegend=False
                    ))
                    
                    mini_fig.update_layout(
                        height=100,
                        margin=dict(l=0, r=0, t=0, b=0),
                        paper_bgcolor='#1e222d',
                        plot_bgcolor='#1e222d',
                        showlegend=False,
                        xaxis=dict(visible=False, rangeslider=dict(visible=False)),
                        yaxis=dict(visible=False)
                    )
                    st.plotly_chart(mini_fig, use_container_width=True, key=f"mini_{coin}")
                
                # Buttons (single set)
                b1, b2 = st.columns(2)
                sym = info.get('symbol', f'{coin}/USDT')
                if b1.button("🟢 BUY", key=f"buy_{coin}"):
                    send_command(sym, "FORCE_BUY")
                if b2.button("🔴 SELL", key=f"sell_{coin}"):
                    send_command(sym, "FORCE_SELL")

st.markdown("---")

# === CHART SECTION ===
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.subheader("📈 Live Chart")
with header_col2:
    st.markdown("""
    <a href="http://localhost:8000/chart" target="_blank" style="
        display: inline-block;
        padding: 0.5rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        margin-top: 0.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    ">
        📈 Open Superchart
    </a>
    """, unsafe_allow_html=True)

# Chart Controls Row
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 2])

with ctrl1:
    chart_coin = st.selectbox("Symbol", [f"{c}/USDT" for c in assets.keys()], key="symbol")
with ctrl2:
    timeframe = st.selectbox("Timeframe", ['15m', '1h', '4h', '1d'], index=1, key="tf")
with ctrl3:
    limit = st.selectbox("Bars", [50, 100, 200, 500], index=1, key="bars")
with ctrl4:
    strategy = st.selectbox("📊 Strategy Template", list(COUNCIL_STRATEGIES.keys()), index=7, key="strategy")

# Strategy Description
st.caption(f"**{COUNCIL_STRATEGIES[strategy]['name']}**: {COUNCIL_STRATEGIES[strategy]['description']}")

# Draw Chart
df = fetch_ohlcv(chart_coin, timeframe, limit)
if df is not None and len(df) > 20:
    fig = create_chart(df, chart_coin, strategy)
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{chart_coin}_{timeframe}_{strategy}")
    
    # OHLCV Info Bar
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    pct_change = ((latest['close'] - prev['close']) / prev['close']) * 100
    
    info_cols = st.columns(6)
    info_cols[0].metric("Open", f"${latest['open']:,.2f}")
    info_cols[1].metric("High", f"${latest['high']:,.2f}")
    info_cols[2].metric("Low", f"${latest['low']:,.2f}")
    info_cols[3].metric("Close", f"${latest['close']:,.2f}")
    info_cols[4].metric("Volume", f"{latest['volume']:,.0f}")
    info_cols[5].metric("Change", f"{pct_change:+.2f}%")

# System Log Section
with st.expander("📜 System Log / Raw Data"):
    st.json(data)

# Auto-refresh status and countdown
import time
from datetime import datetime

# Get current time
current_time = datetime.now().strftime("%H:%M:%S")
refresh_interval = 15  # seconds

st.markdown("---")
st.markdown(f"**🔴 LIVE** | Last: {data.get('timestamp', '-')} | Refresh: every {refresh_interval}s | Now: {current_time}")

# Full page refresh every 15 seconds to update all data
time.sleep(refresh_interval)
st.cache_data.clear()  # Clear cache to get fresh data
st.rerun()
