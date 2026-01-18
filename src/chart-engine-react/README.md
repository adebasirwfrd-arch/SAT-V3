# 📈 SAT-V3 Advanced Charting Module

TradingView Clone with pixel-perfect precision, built with React, TypeScript, and raw HTML5 Canvas API.

## 🎨 Theme: Ocean Calm

| Element | Color |
|---------|-------|
| Background | #FFFFFF |
| Grid Lines | #F0F3FA |
| Bullish Candle | #00B4DB → #0083B0 (Teal) |
| Bearish Candle | #FF6B6B (Soft Red) |
| UI Accents | #0083B0 |

## 🏗️ Architecture

### 5-Layer Canvas System
```
Layer 5: CursorLayer    (Volatile)  - Crosshair, Tooltips
Layer 4: DrawingLayer   (Dynamic)   - Trendlines, Fibonacci
Layer 3: IndicatorLayer (Dynamic)   - SMA, EMA, Bollinger Bands
Layer 2: CandleSeries   (Dynamic)   - Candlesticks, Volume
Layer 1: CanvasLayer    (Static)    - Grid, Watermark, Labels
```

### Directory Structure
```
src/
├── App.tsx                     # Main application
├── types.ts                    # TypeScript interfaces
├── components/
│   ├── ChartEngine/
│   │   ├── ChartContainer.tsx  # Main container (5 layers)
│   │   ├── CanvasLayer.tsx     # Background & grid
│   │   ├── CandleSeries.tsx    # OHLC rendering
│   │   ├── IndicatorLayer.tsx  # Overlay indicators
│   │   ├── DrawingLayer.tsx    # Drawing tools
│   │   ├── CursorLayer.tsx     # Crosshair & labels
│   │   └── SeparatePane.tsx    # RSI/MACD pane
│   └── UI/
│       ├── TopBar.tsx          # Symbol, timeframe, chart type
│       └── Toolbar.tsx         # Drawing tools & indicators
├── hooks/
│   ├── useDataStream.ts        # Binance WebSocket
│   └── useChartInteraction.ts  # Pan, Zoom, Inertia
├── lib/
│   ├── math/
│   │   └── coordinates.ts      # Price ↔ Pixel conversion
│   ├── indicators/
│   │   └── index.ts            # SMA, EMA, BB, RSI, MACD
│   └── chartTransformers.ts    # Heikin Ashi, Renko
└── store/
    └── chartStore.ts           # Zustand global state
```

## ✨ Features

### Chart Types
- ✅ Candlestick
- ✅ Heikin Ashi
- ✅ Renko
- ✅ Hollow Candles
- ⬜ Bar
- ⬜ Line
- ⬜ Area

### Drawing Tools
- ✅ Trendline
- ✅ Fibonacci Retracement
- ✅ Position (Long/Short)
- ⬜ Horizontal Line
- ⬜ Vertical Line
- ⬜ Gann Fan
- ⬜ Elliott Wave

### Indicators (Overlay)
- ✅ SMA (20, 50, 200)
- ✅ EMA (20)
- ✅ Bollinger Bands

### Indicators (Separate Pane)
- ✅ RSI (14)
- ✅ MACD (12, 26, 9)

### Interactions
- ✅ Pan (Drag)
- ✅ Zoom (Mouse Wheel)
- ✅ Inertia Scrolling (Physics-based)
- ✅ Crosshair with Labels
- ✅ Auto-Scaling Y-Axis
- ✅ Countdown to Candle Close
- ✅ Symbol Watermark

### Data
- ✅ Binance Testnet WebSocket
- ✅ Historical Backfill (REST API)
- ✅ Real-time Updates

## 🚀 Quick Start

```bash
cd src/chart-engine-react
npm install
npm run dev
```

Open http://localhost:3001

## 📡 Data Source

- **WebSocket**: `wss://testnet.binance.vision/ws`
- **REST API**: `https://testnet.binance.vision/api/v3`
- **Default Symbol**: BTCUSDT
- **Default Timeframe**: 1m

## 🛠️ Tech Stack

- **Framework**: React 18
- **Language**: TypeScript
- **Build**: Vite 5
- **State**: Zustand
- **Rendering**: HTML5 Canvas (Raw)
- **Data**: Native WebSocket

## 📝 License

MIT
