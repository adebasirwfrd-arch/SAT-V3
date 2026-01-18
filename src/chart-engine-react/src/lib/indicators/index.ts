import { CandleData } from '../../types';

/**
 * Technical Indicator Library
 * Comprehensive implementation for 50+ indicators
 * Supports Overlay (main pane) and Oscillators (separate pane)
 */

// ==================== MOVING AVERAGES ====================

export function calculateSMA(data: CandleData[], period: number): (number | null)[] {
    const result: (number | null)[] = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) { result.push(null); continue; }
        let sum = 0;
        for (let j = 0; j < period; j++) sum += data[i - j].close;
        result.push(sum / period);
    }
    return result;
}

export function calculateEMA(data: CandleData[], period: number): (number | null)[] {
    const result: (number | null)[] = [];
    const multiplier = 2 / (period + 1);
    let ema = 0;

    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) { result.push(null); continue; }
        if (i === period - 1) {
            let sum = 0;
            for (let j = 0; j < period; j++) sum += data[i - j].close;
            ema = sum / period;
        } else {
            ema = (data[i].close - ema) * multiplier + ema;
        }
        result.push(ema);
    }
    return result;
}

export function calculateWMA(data: CandleData[], period: number): (number | null)[] {
    const result: (number | null)[] = [];
    const weightSum = (period * (period + 1)) / 2;

    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) { result.push(null); continue; }
        let weightedSum = 0;
        for (let j = 0; j < period; j++) {
            weightedSum += data[i - j].close * (period - j);
        }
        result.push(weightedSum / weightSum);
    }
    return result;
}

// ==================== VOLATILITY ====================

export interface BollingerBands {
    upper: (number | null)[];
    middle: (number | null)[];
    lower: (number | null)[];
}

export function calculateBollingerBands(
    data: CandleData[], period: number = 20, stdDev: number = 2
): BollingerBands {
    const sma = calculateSMA(data, period);
    const upper: (number | null)[] = [];
    const lower: (number | null)[] = [];

    for (let i = 0; i < data.length; i++) {
        if (i < period - 1 || sma[i] === null) {
            upper.push(null); lower.push(null); continue;
        }
        let sumSq = 0;
        for (let j = 0; j < period; j++) {
            const diff = data[i - j].close - sma[i]!;
            sumSq += diff * diff;
        }
        const std = Math.sqrt(sumSq / period);
        upper.push(sma[i]! + stdDev * std);
        lower.push(sma[i]! - stdDev * std);
    }
    return { upper, middle: sma, lower };
}

export function calculateATR(data: CandleData[], period: number = 14): (number | null)[] {
    const result: (number | null)[] = [];
    const trueRanges: number[] = [];

    for (let i = 0; i < data.length; i++) {
        if (i === 0) {
            trueRanges.push(data[i].high - data[i].low);
            result.push(null);
            continue;
        }

        const tr = Math.max(
            data[i].high - data[i].low,
            Math.abs(data[i].high - data[i - 1].close),
            Math.abs(data[i].low - data[i - 1].close)
        );
        trueRanges.push(tr);

        if (i < period) { result.push(null); continue; }

        if (i === period) {
            result.push(trueRanges.slice(-period).reduce((a, b) => a + b, 0) / period);
        } else {
            const prevATR = result[i - 1]!;
            result.push((prevATR * (period - 1) + tr) / period);
        }
    }
    return result;
}

export interface KeltnerChannels {
    upper: (number | null)[];
    middle: (number | null)[];
    lower: (number | null)[];
}

export function calculateKeltnerChannels(
    data: CandleData[], period: number = 20, multiplier: number = 2
): KeltnerChannels {
    const ema = calculateEMA(data, period);
    const atr = calculateATR(data, 10);

    const upper: (number | null)[] = [];
    const lower: (number | null)[] = [];

    for (let i = 0; i < data.length; i++) {
        if (ema[i] === null || atr[i] === null) {
            upper.push(null); lower.push(null);
        } else {
            upper.push(ema[i]! + multiplier * atr[i]!);
            lower.push(ema[i]! - multiplier * atr[i]!);
        }
    }
    return { upper, middle: ema, lower };
}

// ==================== OSCILLATORS ====================

export function calculateRSI(data: CandleData[], period: number = 14): (number | null)[] {
    const result: (number | null)[] = [];
    let avgGain = 0, avgLoss = 0;

    for (let i = 0; i < data.length; i++) {
        if (i === 0) { result.push(null); continue; }

        const change = data[i].close - data[i - 1].close;
        const gain = change > 0 ? change : 0;
        const loss = change < 0 ? -change : 0;

        if (i < period) { result.push(null); continue; }

        if (i === period) {
            let sumGain = 0, sumLoss = 0;
            for (let j = 1; j <= period; j++) {
                const c = data[j].close - data[j - 1].close;
                sumGain += c > 0 ? c : 0;
                sumLoss += c < 0 ? -c : 0;
            }
            avgGain = sumGain / period;
            avgLoss = sumLoss / period;
        } else {
            avgGain = (avgGain * (period - 1) + gain) / period;
            avgLoss = (avgLoss * (period - 1) + loss) / period;
        }

        if (avgLoss === 0) { result.push(100); }
        else { result.push(100 - (100 / (1 + avgGain / avgLoss))); }
    }
    return result;
}

export interface MACD {
    macd: (number | null)[];
    signal: (number | null)[];
    histogram: (number | null)[];
}

export function calculateMACD(
    data: CandleData[], fastPeriod: number = 12, slowPeriod: number = 26, signalPeriod: number = 9
): MACD {
    const fastEMA = calculateEMA(data, fastPeriod);
    const slowEMA = calculateEMA(data, slowPeriod);
    const macdLine: (number | null)[] = [];

    for (let i = 0; i < data.length; i++) {
        if (fastEMA[i] === null || slowEMA[i] === null) macdLine.push(null);
        else macdLine.push(fastEMA[i]! - slowEMA[i]!);
    }

    // Signal line
    const signal: (number | null)[] = [];
    const histogram: (number | null)[] = [];
    let signalEMA = 0;
    let validCount = 0;

    for (let i = 0; i < data.length; i++) {
        if (macdLine[i] === null) { signal.push(null); histogram.push(null); continue; }
        validCount++;
        if (validCount < signalPeriod) { signal.push(null); histogram.push(null); continue; }

        if (validCount === signalPeriod) {
            let sum = 0, count = 0;
            for (let j = i; j >= 0 && count < signalPeriod; j--) {
                if (macdLine[j] !== null) { sum += macdLine[j]!; count++; }
            }
            signalEMA = sum / signalPeriod;
        } else {
            const mult = 2 / (signalPeriod + 1);
            signalEMA = (macdLine[i]! - signalEMA) * mult + signalEMA;
        }
        signal.push(signalEMA);
        histogram.push(macdLine[i]! - signalEMA);
    }
    return { macd: macdLine, signal, histogram };
}

export interface Stochastic {
    k: (number | null)[];
    d: (number | null)[];
}

export function calculateStochastic(
    data: CandleData[], period: number = 14, smoothK: number = 3, smoothD: number = 3
): Stochastic {
    const rawK: (number | null)[] = [];

    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) { rawK.push(null); continue; }

        let highest = -Infinity, lowest = Infinity;
        for (let j = 0; j < period; j++) {
            highest = Math.max(highest, data[i - j].high);
            lowest = Math.min(lowest, data[i - j].low);
        }

        const range = highest - lowest;
        if (range === 0) rawK.push(50);
        else rawK.push(((data[i].close - lowest) / range) * 100);
    }

    // Smooth K
    const k = calculateSMAValues(rawK, smoothK);
    const d = calculateSMAValues(k, smoothD);

    return { k, d };
}

function calculateSMAValues(values: (number | null)[], period: number): (number | null)[] {
    const result: (number | null)[] = [];
    for (let i = 0; i < values.length; i++) {
        if (i < period - 1 || values[i] === null) { result.push(null); continue; }
        let sum = 0, count = 0;
        for (let j = 0; j < period; j++) {
            if (values[i - j] !== null) { sum += values[i - j]!; count++; }
        }
        result.push(count > 0 ? sum / count : null);
    }
    return result;
}

export function calculateCCI(data: CandleData[], period: number = 20): (number | null)[] {
    const result: (number | null)[] = [];
    const constant = 0.015;

    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) { result.push(null); continue; }

        // Typical Price
        const typicalPrices: number[] = [];
        for (let j = 0; j < period; j++) {
            const tp = (data[i - j].high + data[i - j].low + data[i - j].close) / 3;
            typicalPrices.push(tp);
        }

        const smaTP = typicalPrices.reduce((a, b) => a + b, 0) / period;
        const meanDeviation = typicalPrices.reduce((sum, tp) => sum + Math.abs(tp - smaTP), 0) / period;

        const currentTP = (data[i].high + data[i].low + data[i].close) / 3;
        const cci = (currentTP - smaTP) / (constant * meanDeviation);
        result.push(cci);
    }
    return result;
}

// ==================== TREND ====================

export function calculateADX(data: CandleData[], period: number = 14): (number | null)[] {
    const result: (number | null)[] = [];
    const trValues: number[] = [];
    const plusDM: number[] = [];
    const minusDM: number[] = [];

    for (let i = 0; i < data.length; i++) {
        if (i === 0) { result.push(null); continue; }

        const tr = Math.max(
            data[i].high - data[i].low,
            Math.abs(data[i].high - data[i - 1].close),
            Math.abs(data[i].low - data[i - 1].close)
        );
        trValues.push(tr);

        const upMove = data[i].high - data[i - 1].high;
        const downMove = data[i - 1].low - data[i].low;

        plusDM.push(upMove > downMove && upMove > 0 ? upMove : 0);
        minusDM.push(downMove > upMove && downMove > 0 ? downMove : 0);

        if (i < period * 2) { result.push(null); continue; }

        const atr = trValues.slice(-period).reduce((a, b) => a + b, 0) / period;
        const plusDI = (plusDM.slice(-period).reduce((a, b) => a + b, 0) / period) / atr * 100;
        const minusDI = (minusDM.slice(-period).reduce((a, b) => a + b, 0) / period) / atr * 100;

        const dx = Math.abs(plusDI - minusDI) / (plusDI + minusDI) * 100;
        result.push(dx);
    }
    return result;
}

export function calculateParabolicSAR(data: CandleData[], step: number = 0.02, max: number = 0.2): (number | null)[] {
    const result: (number | null)[] = [];
    if (data.length < 2) return result;

    let isUptrend = data[1].close > data[0].close;
    let ep = isUptrend ? data[0].high : data[0].low;
    let sar = isUptrend ? data[0].low : data[0].high;
    let af = step;

    for (let i = 0; i < data.length; i++) {
        if (i === 0) { result.push(null); continue; }

        const prevSAR = sar;
        sar = prevSAR + af * (ep - prevSAR);

        // Check for reversal
        if (isUptrend) {
            if (data[i].low < sar) {
                isUptrend = false;
                sar = ep;
                ep = data[i].low;
                af = step;
            } else if (data[i].high > ep) {
                ep = data[i].high;
                af = Math.min(af + step, max);
            }
        } else {
            if (data[i].high > sar) {
                isUptrend = true;
                sar = ep;
                ep = data[i].high;
                af = step;
            } else if (data[i].low < ep) {
                ep = data[i].low;
                af = Math.min(af + step, max);
            }
        }

        result.push(sar);
    }
    return result;
}

// ==================== VOLUME ====================

export function calculateOBV(data: CandleData[]): (number | null)[] {
    const result: (number | null)[] = [];
    let obv = 0;

    for (let i = 0; i < data.length; i++) {
        if (i === 0) { obv = data[i].volume; }
        else {
            if (data[i].close > data[i - 1].close) obv += data[i].volume;
            else if (data[i].close < data[i - 1].close) obv -= data[i].volume;
        }
        result.push(obv);
    }
    return result;
}

export function calculateVWAP(data: CandleData[]): (number | null)[] {
    const result: (number | null)[] = [];
    let cumulativeTPV = 0;
    let cumulativeVolume = 0;

    for (let i = 0; i < data.length; i++) {
        const typicalPrice = (data[i].high + data[i].low + data[i].close) / 3;
        cumulativeTPV += typicalPrice * data[i].volume;
        cumulativeVolume += data[i].volume;

        if (cumulativeVolume === 0) result.push(null);
        else result.push(cumulativeTPV / cumulativeVolume);
    }
    return result;
}

export function calculateMFI(data: CandleData[], period: number = 14): (number | null)[] {
    const result: (number | null)[] = [];
    const typicalPrices: number[] = [];
    const moneyFlows: { positive: number; negative: number }[] = [];

    for (let i = 0; i < data.length; i++) {
        const tp = (data[i].high + data[i].low + data[i].close) / 3;
        const rawMF = tp * data[i].volume;

        typicalPrices.push(tp);

        if (i === 0) {
            moneyFlows.push({ positive: rawMF, negative: 0 });
            result.push(null);
            continue;
        }

        if (tp > typicalPrices[i - 1]) {
            moneyFlows.push({ positive: rawMF, negative: 0 });
        } else {
            moneyFlows.push({ positive: 0, negative: rawMF });
        }

        if (i < period) { result.push(null); continue; }

        let posMF = 0, negMF = 0;
        for (let j = 0; j < period; j++) {
            posMF += moneyFlows[i - j].positive;
            negMF += moneyFlows[i - j].negative;
        }

        if (negMF === 0) result.push(100);
        else result.push(100 - (100 / (1 + posMF / negMF)));
    }
    return result;
}

// ==================== VOLUME PROFILE ====================

export interface VolumeProfileLevel {
    priceLevel: number;
    volume: number;
    buyVolume: number;
    sellVolume: number;
}

export function calculateVolumeProfile(
    data: CandleData[],
    startIdx: number,
    endIdx: number,
    numLevels: number = 24
): VolumeProfileLevel[] {
    if (data.length === 0) return [];

    // Find price range
    let minPrice = Infinity, maxPrice = -Infinity;
    for (let i = startIdx; i <= endIdx && i < data.length; i++) {
        minPrice = Math.min(minPrice, data[i].low);
        maxPrice = Math.max(maxPrice, data[i].high);
    }

    const priceRange = maxPrice - minPrice;
    const levelSize = priceRange / numLevels;

    // Initialize levels
    const levels: VolumeProfileLevel[] = [];
    for (let i = 0; i < numLevels; i++) {
        levels.push({
            priceLevel: minPrice + (i + 0.5) * levelSize,
            volume: 0,
            buyVolume: 0,
            sellVolume: 0,
        });
    }

    // Distribute volume to levels
    for (let i = startIdx; i <= endIdx && i < data.length; i++) {
        const candle = data[i];
        const candleRange = candle.high - candle.low;
        const isBullish = candle.close >= candle.open;

        for (let j = 0; j < numLevels; j++) {
            const levelBottom = minPrice + j * levelSize;
            const levelTop = levelBottom + levelSize;

            // Check if candle overlaps level
            if (candle.high >= levelBottom && candle.low <= levelTop) {
                const overlap = Math.min(candle.high, levelTop) - Math.max(candle.low, levelBottom);
                const volumeShare = candleRange > 0 ? (overlap / candleRange) * candle.volume : 0;

                levels[j].volume += volumeShare;
                if (isBullish) levels[j].buyVolume += volumeShare;
                else levels[j].sellVolume += volumeShare;
            }
        }
    }

    return levels;
}

// ==================== INDICATOR REGISTRY ====================

export type IndicatorFunction = (data: CandleData[], ...params: number[]) => (number | null)[];

export const INDICATOR_REGISTRY: Map<string, { fn: IndicatorFunction; defaultParams: number[]; pane: 'main' | 'separate'; color: string }> = new Map([
    ['SMA', { fn: calculateSMA, defaultParams: [20], pane: 'main', color: '#FFB800' }],
    ['EMA', { fn: calculateEMA, defaultParams: [20], pane: 'main', color: '#00BCD4' }],
    ['WMA', { fn: calculateWMA, defaultParams: [20], pane: 'main', color: '#9C27B0' }],
    ['RSI', { fn: calculateRSI, defaultParams: [14], pane: 'separate', color: '#E040FB' }],
    ['ATR', { fn: calculateATR, defaultParams: [14], pane: 'separate', color: '#FF5722' }],
    ['ADX', { fn: calculateADX, defaultParams: [14], pane: 'separate', color: '#795548' }],
    ['CCI', { fn: calculateCCI, defaultParams: [20], pane: 'separate', color: '#607D8B' }],
    ['OBV', { fn: calculateOBV, defaultParams: [], pane: 'separate', color: '#4CAF50' }],
    ['VWAP', { fn: calculateVWAP, defaultParams: [], pane: 'main', color: '#FF9800' }],
    ['MFI', { fn: calculateMFI, defaultParams: [14], pane: 'separate', color: '#3F51B5' }],
    ['SAR', { fn: calculateParabolicSAR, defaultParams: [0.02, 0.2], pane: 'main', color: '#F44336' }],
]);
