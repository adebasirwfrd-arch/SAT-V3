import { CandleData, VisibleRange } from '../../types';

/**
 * TradingView-Style Coordinate System
 * Implements Dynamic Auto-Scaling with Smart Padding
 */

/**
 * Convert price to Y pixel coordinate
 * Uses TradingView formula: pixelY = canvasHeight - ((price - renderMin) / (renderMax - renderMin)) * canvasHeight
 */
export function priceToCoordinate(
    price: number,
    height: number,
    minPrice: number,
    maxPrice: number,
    scaleType: 'linear' | 'logarithmic' = 'linear'
): number {
    const range = maxPrice - minPrice;
    if (range === 0) return height / 2;

    if (scaleType === 'logarithmic' && minPrice > 0 && price > 0) {
        const logMin = Math.log(minPrice);
        const logMax = Math.log(maxPrice);
        const logPrice = Math.log(price);
        const normalized = (logPrice - logMin) / (logMax - logMin);
        return height - normalized * height;
    }

    // TradingView formula: inverted Y axis
    const normalized = (price - minPrice) / range;
    return height - normalized * height;
}

/**
 * Convert Y pixel coordinate to price
 */
export function coordinateToPrice(
    y: number,
    height: number,
    minPrice: number,
    maxPrice: number,
    scaleType: 'linear' | 'logarithmic' = 'linear'
): number {
    const normalized = (height - y) / height;

    if (scaleType === 'logarithmic' && minPrice > 0) {
        const logMin = Math.log(minPrice);
        const logMax = Math.log(maxPrice);
        return Math.exp(logMin + normalized * (logMax - logMin));
    }

    return minPrice + normalized * (maxPrice - minPrice);
}

/**
 * Convert data index to X pixel coordinate
 * Right-aligned with right margin for price scale
 */
export function timeToCoordinate(
    index: number,
    dataLength: number,
    width: number,
    barSpacing: number,
    scrollOffset: number,
    rightMargin: number = 80
): number {
    const rightEdge = width - rightMargin;
    const offsetFromRight = (dataLength - 1 - index) * barSpacing;
    return rightEdge - offsetFromRight - scrollOffset * barSpacing;
}

/**
 * Convert X pixel coordinate to data index
 */
export function coordinateToIndex(
    x: number,
    dataLength: number,
    width: number,
    barSpacing: number,
    scrollOffset: number,
    rightMargin: number = 80
): number {
    const rightEdge = width - rightMargin;
    const offsetFromRight = rightEdge - x + scrollOffset * barSpacing;
    const index = dataLength - 1 - Math.round(offsetFromRight / barSpacing);
    return Math.max(0, Math.min(dataLength - 1, index));
}

/**
 * Calculate visible range with TradingView-style Dynamic Auto-Scaling
 * CRITICAL: Only use visible candles for Min/Max, not entire dataset
 */
export function calculateVisibleRange(
    data: CandleData[],
    width: number,
    barSpacing: number,
    scrollOffset: number
): VisibleRange {
    if (data.length === 0) {
        return {
            minPrice: 0,
            maxPrice: 100,
            startIdx: 0,
            endIdx: 0,
            startTime: 0,
            endTime: 0,
        };
    }

    // Step 1: Calculate visible bar indices
    const rightMargin = 80;
    const effectiveWidth = width - rightMargin;
    const numVisibleBars = Math.ceil(effectiveWidth / barSpacing) + 2; // +2 buffer

    // endIdx is the rightmost visible candle (accounting for scroll)
    const endIdx = Math.min(
        data.length - 1,
        data.length - 1 - Math.floor(scrollOffset)
    );

    // startIdx is the leftmost visible candle
    const startIdx = Math.max(0, endIdx - numVisibleBars);

    // Step 2: Get LOCAL Min/Max from VISIBLE candles ONLY (TradingView's key insight)
    let localLow = Infinity;
    let localHigh = -Infinity;

    for (let i = startIdx; i <= endIdx && i < data.length; i++) {
        const candle = data[i];
        if (!candle) continue;

        if (candle.low < localLow) localLow = candle.low;
        if (candle.high > localHigh) localHigh = candle.high;
    }

    // Handle edge case of no valid data
    if (localLow === Infinity || localHigh === -Infinity) {
        const lastCandle = data[data.length - 1];
        localLow = lastCandle?.low || 0;
        localHigh = lastCandle?.high || 100;
    }

    // Step 3: Apply Smart Padding (10% top and bottom - TradingView Style)
    const priceRange = localHigh - localLow;

    // Handle zero range (flat price)
    const safeRange = priceRange === 0 ? localHigh * 0.01 : priceRange;

    const paddingTop = safeRange * 0.10;    // 10% padding top
    const paddingBottom = safeRange * 0.10; // 10% padding bottom

    const renderMax = localHigh + paddingTop;
    const renderMin = localLow - paddingBottom;

    return {
        minPrice: renderMin,
        maxPrice: renderMax,
        startIdx,
        endIdx,
        startTime: data[startIdx]?.time || 0,
        endTime: data[endIdx]?.time || 0,
    };
}

/**
 * Snap to nearest OHLC (Magnet Mode for drawing tools)
 */
export function snapToOHLC(
    price: number,
    candle: CandleData,
    magnetThreshold: number = 5
): number {
    const values = [candle.open, candle.high, candle.low, candle.close];
    let closest = price;
    let minDist = Infinity;

    for (const v of values) {
        const dist = Math.abs(v - price);
        if (dist < minDist && dist < magnetThreshold) {
            minDist = dist;
            closest = v;
        }
    }

    return closest;
}

/**
 * Calculate optimal bar spacing based on canvas width and data length
 */
export function calculateOptimalBarSpacing(
    width: number,
    dataLength: number,
    minSpacing: number = 4,
    maxSpacing: number = 50
): number {
    const rightMargin = 80;
    const effectiveWidth = width - rightMargin;
    const optimalSpacing = effectiveWidth / Math.min(dataLength, 100);
    return Math.max(minSpacing, Math.min(maxSpacing, optimalSpacing));
}
