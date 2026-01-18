// Core Types for SAT-V3 Advanced Charting Module
// Blueprint: langkah@14.txt - TradingView Clone

export interface CandleData {
    time: number;      // Unix timestamp (ms)
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

// Ocean Calm Theme
export interface ChartTheme {
    background: string;
    gridLines: string;
    bullishBody: string;
    bullishWick: string;
    bearishBody: string;
    bearishWick: string;
    textPrimary: string;
    textSecondary: string;
    crosshair: string;
    watermark: string;
    accent: string;
}

export const OCEAN_CALM_THEME: ChartTheme = {
    background: '#FFFFFF',
    gridLines: '#F0F3FA',
    // TradingView Official Colors
    bullishBody: '#26a69a',    // Teal green
    bullishWick: '#26a69a',    // Same as body
    bearishBody: '#ef5350',    // Coral red
    bearishWick: '#ef5350',    // Same as body
    textPrimary: '#131722',    // TV dark text
    textSecondary: '#787B86',
    crosshair: '#9598A1',      // TV crosshair gray
    watermark: 'rgba(19, 23, 34, 0.05)',
    accent: '#2962FF',         // TV blue accent
};

// Chart Configuration
export interface ChartConfig {
    symbol: string;
    timeframe: string;
    barSpacing: number;
    scrollOffset: number;
    scaleType: 'linear' | 'logarithmic';
    autoScale: boolean;
}

// Visible Range
export interface VisibleRange {
    minPrice: number;
    maxPrice: number;
    startIdx: number;
    endIdx: number;
    startTime: number;
    endTime: number;
}

// Drawing Objects (20+ types)
export type DrawingType =
    // Lines
    | 'none' | 'trendline' | 'ray' | 'extendedLine' | 'horizontalLine' | 'verticalLine' | 'parallelChannel'
    // Fibonacci
    | 'fibonacci' | 'fibExtension' | 'fibChannel'
    // Geometric
    | 'rectangle' | 'ellipse' | 'triangle' | 'path'
    // Annotation
    | 'text' | 'callout' | 'priceLabel' | 'arrow'
    // Position
    | 'position' | 'longPosition' | 'shortPosition'
    // Patterns
    | 'headShoulders' | 'xabcd';

export interface DrawingObject {
    id: string;
    type: DrawingType;
    points: { x: number; y: number; price?: number; time?: number }[];
    properties: Record<string, unknown>;
    visible: boolean;
}

// Chart Types (14 Total - 9 Time-based + 5 Price-based)
export type ChartType =
    // Time-based
    | 'candle'
    | 'bar'
    | 'hollow'
    | 'column'
    | 'line'
    | 'area'
    | 'baseline'
    | 'highLow'
    | 'heikinAshi'
    // Price-based (Exotic)
    | 'renko'
    | 'lineBreak'
    | 'kagi'
    | 'pointFigure'
    | 'rangeBars';

// Tick Volume Profile (for Advanced Volume - Footprint Charts)
export interface TickVolume {
    priceLevel: number;
    buyVolume: number;
    sellVolume: number;
}

// Extended CandleData with volume profile
export interface CandleDataAdvanced extends CandleData {
    tickVolumeProfile?: TickVolume[];
}

// Indicator Types
export interface IndicatorConfig {
    id: string;
    type: string;
    params: Record<string, number>;
    color: string;
    visible: boolean;
    pane: 'main' | 'separate';
}
