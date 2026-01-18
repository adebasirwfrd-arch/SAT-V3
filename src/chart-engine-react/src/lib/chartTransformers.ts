import { CandleData } from '../types';

/**
 * Chart Data Transformers
 * Converts raw OHLC data to various chart type formats
 * Supports 21 TradingView chart types
 */

// ==================== TIME-BASED TRANSFORMERS ====================

/**
 * Heikin Ashi Transformer
 * Smooths price action for trend identification
 */
export function transformToHeikinAshi(data: CandleData[]): CandleData[] {
    if (data.length === 0) return [];

    const result: CandleData[] = [];

    for (let i = 0; i < data.length; i++) {
        const current = data[i];
        const prev = result[i - 1];

        // HA Close = (Open + High + Low + Close) / 4
        const haClose = (current.open + current.high + current.low + current.close) / 4;

        // HA Open = (Previous HA Open + Previous HA Close) / 2
        const haOpen = prev
            ? (prev.open + prev.close) / 2
            : (current.open + current.close) / 2;

        // HA High = Max(High, HA Open, HA Close)
        const haHigh = Math.max(current.high, haOpen, haClose);

        // HA Low = Min(Low, HA Open, HA Close)
        const haLow = Math.min(current.low, haOpen, haClose);

        result.push({
            time: current.time,
            open: haOpen,
            high: haHigh,
            low: haLow,
            close: haClose,
            volume: current.volume,
        });
    }

    return result;
}

/**
 * Check if candle should be rendered as hollow
 * Hollow when Close > Previous Close (uptrend)
 */
export function isHollowCandle(current: CandleData, previous: CandleData | null): boolean {
    if (!previous) return current.close >= current.open;
    return current.close > previous.close;
}

// ==================== PRICE-BASED (EXOTIC) TRANSFORMERS ====================

/**
 * Renko Transformer
 * Creates bricks of fixed price size, ignoring time
 */
export function transformToRenko(data: CandleData[], brickSize: number): CandleData[] {
    if (data.length === 0 || brickSize <= 0) return [];

    const bricks: CandleData[] = [];
    let lastBrickClose = data[0].close;
    let brickTime = data[0].time;
    let virtualIndex = 0;

    for (const candle of data) {
        const priceDiff = candle.close - lastBrickClose;
        const numBricks = Math.floor(Math.abs(priceDiff) / brickSize);

        if (numBricks >= 1) {
            const direction = priceDiff > 0 ? 1 : -1;

            for (let i = 0; i < numBricks; i++) {
                const newClose = lastBrickClose + direction * brickSize;
                bricks.push({
                    time: brickTime + virtualIndex, // Virtual time index
                    open: lastBrickClose,
                    high: direction > 0 ? newClose : lastBrickClose,
                    low: direction > 0 ? lastBrickClose : newClose,
                    close: newClose,
                    volume: candle.volume / numBricks,
                });
                lastBrickClose = newClose;
                brickTime = candle.time;
                virtualIndex++;
            }
        }
    }

    return bricks;
}

/**
 * Line Break Transformer
 * New line only when price exceeds high/low of previous N lines
 */
export function transformToLineBreak(data: CandleData[], lineCount: number = 3): CandleData[] {
    if (data.length === 0) return [];

    const lines: CandleData[] = [];

    // Start with first candle
    lines.push({
        ...data[0],
        open: data[0].open,
        close: data[0].close,
        high: Math.max(data[0].open, data[0].close),
        low: Math.min(data[0].open, data[0].close),
    });

    for (let i = 1; i < data.length; i++) {
        const candle = data[i];
        const lastLine = lines[lines.length - 1];
        const isLastUp = lastLine.close > lastLine.open;

        // Get the high/low of the last N lines
        const lookback = Math.min(lineCount, lines.length);
        let highestHigh = -Infinity;
        let lowestLow = Infinity;

        for (let j = lines.length - lookback; j < lines.length; j++) {
            highestHigh = Math.max(highestHigh, lines[j].high);
            lowestLow = Math.min(lowestLow, lines[j].low);
        }

        // Check for new line condition
        if (isLastUp) {
            // Continuation up
            if (candle.close > highestHigh) {
                lines.push({
                    time: candle.time,
                    open: lastLine.close,
                    close: candle.close,
                    high: candle.close,
                    low: lastLine.close,
                    volume: candle.volume,
                });
            }
            // Reversal down - must break ALL previous N lines
            else if (candle.close < lowestLow) {
                lines.push({
                    time: candle.time,
                    open: lastLine.close,
                    close: candle.close,
                    high: lastLine.close,
                    low: candle.close,
                    volume: candle.volume,
                });
            }
        } else {
            // Continuation down
            if (candle.close < lowestLow) {
                lines.push({
                    time: candle.time,
                    open: lastLine.close,
                    close: candle.close,
                    high: lastLine.close,
                    low: candle.close,
                    volume: candle.volume,
                });
            }
            // Reversal up
            else if (candle.close > highestHigh) {
                lines.push({
                    time: candle.time,
                    open: lastLine.close,
                    close: candle.close,
                    high: candle.close,
                    low: lastLine.close,
                    volume: candle.volume,
                });
            }
        }
    }

    return lines;
}

/**
 * Kagi Transformer
 * Yang (thick) lines when breaks high, Yin (thin) when breaks low
 */
export interface KagiLine {
    time: number;
    price: number;
    isYang: boolean; // true = thick (bullish), false = thin (bearish)
    direction: 'up' | 'down';
}

export function transformToKagi(data: CandleData[], reversalAmount: number): KagiLine[] {
    if (data.length === 0) return [];

    const lines: KagiLine[] = [];
    let currentPrice = data[0].close;
    let direction: 'up' | 'down' = 'up';
    let previousHigh = data[0].close;
    let previousLow = data[0].close;
    let isYang = true;

    lines.push({
        time: data[0].time,
        price: currentPrice,
        isYang,
        direction,
    });

    for (let i = 1; i < data.length; i++) {
        const candle = data[i];
        const price = candle.close;

        if (direction === 'up') {
            if (price > currentPrice) {
                // Continue up
                currentPrice = price;
                if (price > previousHigh) {
                    isYang = true; // Becomes Yang when breaks previous high
                    previousHigh = price;
                }
                lines[lines.length - 1] = { time: candle.time, price, isYang, direction };
            } else if (currentPrice - price >= reversalAmount) {
                // Reversal down
                direction = 'down';
                lines.push({ time: candle.time, price, isYang, direction });
                currentPrice = price;
            }
        } else {
            if (price < currentPrice) {
                // Continue down
                currentPrice = price;
                if (price < previousLow) {
                    isYang = false; // Becomes Yin when breaks previous low
                    previousLow = price;
                }
                lines[lines.length - 1] = { time: candle.time, price, isYang, direction };
            } else if (price - currentPrice >= reversalAmount) {
                // Reversal up
                direction = 'up';
                lines.push({ time: candle.time, price, isYang, direction });
                currentPrice = price;
            }
        }
    }

    return lines;
}

/**
 * Point & Figure (PnF) Transformer
 * Columns of X (up) and O (down)
 */
export interface PnFColumn {
    x: number; // Column index
    boxes: { price: number; type: 'X' | 'O' }[];
    direction: 'up' | 'down';
}

export function transformToPnF(data: CandleData[], boxSize: number, reversalBoxes: number = 3): PnFColumn[] {
    if (data.length === 0 || boxSize <= 0) return [];

    const columns: PnFColumn[] = [];
    let currentColumn: PnFColumn = { x: 0, boxes: [], direction: 'up' };
    let lastBoxPrice = Math.floor(data[0].close / boxSize) * boxSize;

    // Initialize with first X
    currentColumn.boxes.push({ price: lastBoxPrice, type: 'X' });

    for (const candle of data) {
        const high = Math.floor(candle.high / boxSize) * boxSize;
        const low = Math.floor(candle.low / boxSize) * boxSize;

        if (currentColumn.direction === 'up') {
            // Check for continuation up
            if (high > lastBoxPrice) {
                for (let p = lastBoxPrice + boxSize; p <= high; p += boxSize) {
                    currentColumn.boxes.push({ price: p, type: 'X' });
                    lastBoxPrice = p;
                }
            }
            // Check for reversal
            else if (lastBoxPrice - low >= reversalBoxes * boxSize) {
                columns.push({ ...currentColumn });
                currentColumn = { x: columns.length, boxes: [], direction: 'down' };
                for (let p = lastBoxPrice - boxSize; p >= low; p -= boxSize) {
                    currentColumn.boxes.push({ price: p, type: 'O' });
                    lastBoxPrice = p;
                }
            }
        } else {
            // Check for continuation down
            if (low < lastBoxPrice) {
                for (let p = lastBoxPrice - boxSize; p >= low; p -= boxSize) {
                    currentColumn.boxes.push({ price: p, type: 'O' });
                    lastBoxPrice = p;
                }
            }
            // Check for reversal
            else if (high - lastBoxPrice >= reversalBoxes * boxSize) {
                columns.push({ ...currentColumn });
                currentColumn = { x: columns.length, boxes: [], direction: 'up' };
                for (let p = lastBoxPrice + boxSize; p <= high; p += boxSize) {
                    currentColumn.boxes.push({ price: p, type: 'X' });
                    lastBoxPrice = p;
                }
            }
        }
    }

    if (currentColumn.boxes.length > 0) {
        columns.push(currentColumn);
    }

    return columns;
}

/**
 * Range Bars Transformer
 * Each bar has exactly the same price range (High - Low = Constant)
 */
export function transformToRangeBars(data: CandleData[], rangeSize: number): CandleData[] {
    if (data.length === 0 || rangeSize <= 0) return [];

    const bars: CandleData[] = [];
    let currentBar: CandleData | null = null;

    for (const candle of data) {
        // Process each tick (using close as proxy)
        const price = candle.close;

        if (!currentBar) {
            currentBar = {
                time: candle.time,
                open: price,
                high: price,
                low: price,
                close: price,
                volume: candle.volume,
            };
        }

        // Update current bar
        currentBar.high = Math.max(currentBar.high, price);
        currentBar.low = Math.min(currentBar.low, price);
        currentBar.close = price;
        currentBar.volume += candle.volume;

        // Check if range is complete
        while (currentBar.high - currentBar.low >= rangeSize) {
            // Close the bar at the range boundary
            const isUp = currentBar.close >= currentBar.open;

            if (isUp) {
                currentBar.high = currentBar.low + rangeSize;
                currentBar.close = currentBar.high;
            } else {
                currentBar.low = currentBar.high - rangeSize;
                currentBar.close = currentBar.low;
            }

            bars.push({ ...currentBar });

            // Start new bar
            currentBar = {
                time: candle.time,
                open: currentBar.close,
                high: price,
                low: price,
                close: price,
                volume: 0,
            };
            currentBar.high = Math.max(currentBar.high, price);
            currentBar.low = Math.min(currentBar.low, price);
        }
    }

    return bars;
}

// ==================== TYPE EXPORTS ====================

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

export const CHART_TYPE_INFO: Record<ChartType, { label: string; category: 'time' | 'price'; icon: string }> = {
    candle: { label: 'Candles', category: 'time', icon: '🕯️' },
    bar: { label: 'Bars', category: 'time', icon: '📊' },
    hollow: { label: 'Hollow', category: 'time', icon: '⬜' },
    column: { label: 'Column', category: 'time', icon: '📶' },
    line: { label: 'Line', category: 'time', icon: '📈' },
    area: { label: 'Area', category: 'time', icon: '🏔️' },
    baseline: { label: 'Baseline', category: 'time', icon: '↔️' },
    highLow: { label: 'High-Low', category: 'time', icon: '↕️' },
    heikinAshi: { label: 'Heikin Ashi', category: 'time', icon: '🎌' },
    renko: { label: 'Renko', category: 'price', icon: '🧱' },
    lineBreak: { label: 'Line Break', category: 'price', icon: '📐' },
    kagi: { label: 'Kagi', category: 'price', icon: '⚡' },
    pointFigure: { label: 'Point & Figure', category: 'price', icon: '❌' },
    rangeBars: { label: 'Range Bars', category: 'price', icon: '📏' },
};
