import { create } from 'zustand';
import { CandleData, ChartConfig, ChartType, DrawingObject, IndicatorConfig, OCEAN_CALM_THEME, ChartTheme } from '../types';

export type CouncilStrategy = 'fullAnalysis' | 'trend' | 'struct' | 'volume' | 'smart' | 'pattern' | 'geom' | 'indic';

// Methodology types for trading pattern detection
export type MethodologyType =
    | 'none'
    | 'accumulation'   // Crypto Accumulation Candle Finder
    | 'haBB'           // Nooner's HA/BB Candles  
    | 'dailyCandle'    // Daily Candle overlay
    | 'cfr'            // Candle Formation Ratio
    | 'renko'          // Renko Bands
    | 'inside'         // Mushir's Inside Candle
    | 'vsc'            // Volume Spread Candle
    | 'htf'            // HTF Candles
    | 'pattern321'     // 321 Pattern (RSI All In)
    | 'ivd'            // Intrabar Volume Delta
    | 'big_candle'     // Big Candle Up/Down Alert
    | 'crt_po3'        // CRT + PO3 Range Theory
    | 'internal_strength' // Internal Candle Strength (LuxAlgo)
    | 'smart_bar_counter' // Smart Bar Counter with Alerts
    | 'lrc'            // Linear Regression Candle
    | 'breakout_oscillator' // Candle Breakout Oscillator (LuxAlgo)
    | 'vwap_rating'    // VWAP + Candle-Rating SELL
    | 'ma_candles'     // Moving Average Candles
    // Methodology 6
    | 'crt_trend_filter' // CRT with Trend Filter
    | 'big_candles_filter' // Big Candles Filter (Not Range)
    | 'bbr1_volatility' // BBr1 Candle Range Volatility Gap
    | 'ebp_marker'      // EBP Candle Marker
    | 'momentum_exhaustion' // Candle Momentum Exhaustion
    | 'color_by_time'   // Color candle by time
    | 'bulldozz_ma'     // BullDozz MA-Candlesticks
    | 'bull_vs_bear'    // Bull vs Bear Candles
    | 'last_candle_alert' // Last Candle Close Alert
    | 'truly_bull_bear' // Truly Bullish & Bearish Candle
    | 'volume_delta_htf'; // Volume Delta Candles HTF

interface ChartState {
    // Data
    data: CandleData[];
    setData: (data: CandleData[]) => void;
    updateLastCandle: (candle: CandleData) => void;
    appendCandle: (candle: CandleData) => void;

    // Config
    config: ChartConfig;
    setConfig: (config: Partial<ChartConfig>) => void;

    // Theme
    theme: ChartTheme;
    setTheme: (theme: ChartTheme) => void;

    // Chart Type
    chartType: ChartType;
    setChartType: (type: ChartType) => void;

    // Council Strategy
    activeCouncil: CouncilStrategy;
    setActiveCouncil: (strategy: CouncilStrategy) => void;

    // Methodology (Trading Pattern Detection)
    activeMethodology: MethodologyType;
    setActiveMethodology: (methodology: MethodologyType) => void;

    // Viewport
    scrollOffset: number;
    barSpacing: number;
    setScrollOffset: (offset: number) => void;
    setBarSpacing: (spacing: number) => void;

    // Crosshair
    crosshair: { x: number; y: number } | null;
    setCrosshair: (pos: { x: number; y: number } | null) => void;

    // Drawings
    drawings: DrawingObject[];
    addDrawing: (drawing: DrawingObject) => void;
    removeDrawing: (id: string) => void;
    updateDrawing: (id: string, updates: Partial<DrawingObject>) => void;

    // Indicators
    indicators: IndicatorConfig[];
    addIndicator: (indicator: IndicatorConfig) => void;
    removeIndicator: (id: string) => void;

    // Connection
    isConnected: boolean;
    setConnected: (connected: boolean) => void;

    // Countdown
    candleCloseCountdown: number;
    setCandleCloseCountdown: (seconds: number) => void;
}

export const useChartStore = create<ChartState>((set) => ({
    // Data
    data: [],
    setData: (data) => set({ data }),
    updateLastCandle: (candle) => set((state) => {
        if (state.data.length === 0) return { data: [candle] };
        const newData = [...state.data];
        newData[newData.length - 1] = candle;
        return { data: newData };
    }),
    appendCandle: (candle) => set((state) => ({
        data: [...state.data, candle]
    })),

    // Config
    config: {
        symbol: 'BTCUSDT',
        timeframe: '1m',
        barSpacing: 12,
        scrollOffset: 0,
        scaleType: 'linear',
        autoScale: true,
    },
    setConfig: (config) => set((state) => ({
        config: { ...state.config, ...config }
    })),

    // Theme
    theme: OCEAN_CALM_THEME,
    setTheme: (theme) => set({ theme }),

    // Chart Type
    chartType: 'candle',
    setChartType: (chartType) => set({ chartType }),

    // Council Strategy
    activeCouncil: 'fullAnalysis',
    setActiveCouncil: (activeCouncil) => set({ activeCouncil }),

    // Methodology
    activeMethodology: 'none',
    setActiveMethodology: (activeMethodology) => set({ activeMethodology }),

    // Viewport
    scrollOffset: 0,
    barSpacing: 12,
    setScrollOffset: (scrollOffset) => set({ scrollOffset }),
    setBarSpacing: (barSpacing) => set({ barSpacing: Math.max(4, Math.min(50, barSpacing)) }),

    // Crosshair
    crosshair: null,
    setCrosshair: (crosshair) => set({ crosshair }),

    // Drawings
    drawings: [],
    addDrawing: (drawing) => set((state) => ({
        drawings: [...state.drawings, drawing]
    })),
    removeDrawing: (id) => set((state) => ({
        drawings: state.drawings.filter(d => d.id !== id)
    })),
    updateDrawing: (id, updates) => set((state) => ({
        drawings: state.drawings.map(d => d.id === id ? { ...d, ...updates } : d)
    })),

    // Indicators
    indicators: [],
    addIndicator: (indicator) => set((state) => ({
        indicators: [...state.indicators, indicator]
    })),
    removeIndicator: (id) => set((state) => ({
        indicators: state.indicators.filter(i => i.id !== id)
    })),

    // Connection
    isConnected: false,
    setConnected: (isConnected) => set({ isConnected }),

    // Countdown
    candleCloseCountdown: 0,
    setCandleCloseCountdown: (candleCloseCountdown) => set({ candleCloseCountdown }),
}));
