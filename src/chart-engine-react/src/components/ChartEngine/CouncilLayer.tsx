import React, { useRef, useEffect, useCallback, useMemo } from 'react';
import { ChartTheme, CandleData, VisibleRange } from '../../types';
import { CouncilStrategy } from '../../store/chartStore';
import { calculateVisibleRange, priceToCoordinate, timeToCoordinate } from '../../lib/math/coordinates';

interface CouncilLayerProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    activeCouncil: CouncilStrategy;
}

// Colors for each council strategy
const COUNCIL_COLORS: Record<CouncilStrategy, string> = {
    fullAnalysis: '#FFD700',
    trend: '#00B4DB',
    struct: '#FF6B6B',
    volume: '#26a69a',
    smart: '#9C27B0',
    pattern: '#FF9800',
    geom: '#2196F3',
    indic: '#4CAF50',
};

// Simple SMA calculation
function calculateSimpleSMA(closes: number[], period: number): (number | null)[] {
    const result: (number | null)[] = [];
    for (let i = 0; i < closes.length; i++) {
        if (i < period - 1) {
            result.push(null);
        } else {
            const sum = closes.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            result.push(sum / period);
        }
    }
    return result;
}

// Simple Bollinger Bands calculation
function calculateSimpleBB(closes: number[], period: number, stdDev: number) {
    const sma = calculateSimpleSMA(closes, period);
    const upper: (number | null)[] = [];
    const lower: (number | null)[] = [];

    for (let i = 0; i < closes.length; i++) {
        if (i < period - 1 || sma[i] === null) {
            upper.push(null);
            lower.push(null);
        } else {
            const slice = closes.slice(i - period + 1, i + 1);
            const mean = sma[i]!;
            const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period;
            const std = Math.sqrt(variance);
            upper.push(mean + stdDev * std);
            lower.push(mean - stdDev * std);
        }
    }

    return { upper, middle: sma, lower };
}

/**
 * CouncilLayer - Renders analysis overlays based on selected council strategy
 */
const CouncilLayer: React.FC<CouncilLayerProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    activeCouncil,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    // Calculate support/resistance levels
    const structureLevels = useMemo(() => {
        if (data.length < 20) return [];
        const levels: { price: number; type: 'support' | 'resistance'; strength: number }[] = [];

        // Find local highs and lows
        for (let i = 10; i < data.length - 10; i++) {
            const isLocalHigh = data.slice(i - 5, i).every(c => c.high < data[i].high) &&
                data.slice(i + 1, i + 6).every(c => c.high < data[i].high);
            const isLocalLow = data.slice(i - 5, i).every(c => c.low > data[i].low) &&
                data.slice(i + 1, i + 6).every(c => c.low > data[i].low);

            if (isLocalHigh) {
                levels.push({ price: data[i].high, type: 'resistance', strength: 1 });
            }
            if (isLocalLow) {
                levels.push({ price: data[i].low, type: 'support', strength: 1 });
            }
        }

        // Cluster nearby levels
        const clustered: typeof levels = [];
        const threshold = (Math.max(...data.map(d => d.high)) - Math.min(...data.map(d => d.low))) * 0.01;

        for (const level of levels) {
            const existing = clustered.find(c => Math.abs(c.price - level.price) < threshold && c.type === level.type);
            if (existing) {
                existing.strength++;
                existing.price = (existing.price + level.price) / 2;
            } else {
                clustered.push({ ...level });
            }
        }

        return clustered.filter(l => l.strength >= 2).slice(0, 6);
    }, [data]);

    // Calculate order blocks (Smart Money)
    const orderBlocks = useMemo(() => {
        if (data.length < 30) return [];
        const blocks: { startIdx: number; endIdx: number; high: number; low: number; type: 'bullish' | 'bearish' }[] = [];

        for (let i = 5; i < data.length - 5; i++) {
            const candle = data[i];
            const nextCandles = data.slice(i + 1, i + 4);

            // Bullish order block
            const isBearish = candle.close < candle.open;
            const strongMove = nextCandles.length >= 2 && nextCandles.every(c => c.close > c.open);

            if (isBearish && strongMove && blocks.length < 3) {
                blocks.push({
                    startIdx: i,
                    endIdx: i + 1,
                    high: candle.high,
                    low: candle.low,
                    type: 'bullish',
                });
            }

            // Bearish order block
            const isBullish = candle.close > candle.open;
            const strongDownMove = nextCandles.length >= 2 && nextCandles.every(c => c.close < c.open);

            if (isBullish && strongDownMove && blocks.length < 5) {
                blocks.push({
                    startIdx: i,
                    endIdx: i + 1,
                    high: candle.high,
                    low: candle.low,
                    type: 'bearish',
                });
            }
        }

        return blocks.slice(-5);
    }, [data]);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext('2d');
        if (!canvas || !ctx || data.length === 0) return;

        const pixelRatio = window.devicePixelRatio || 1;
        canvas.width = width * pixelRatio;
        canvas.height = height * pixelRatio;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.scale(pixelRatio, pixelRatio);
        ctx.clearRect(0, 0, width, height);

        const range: VisibleRange = calculateVisibleRange(data, width, barSpacing, scrollOffset);
        const { minPrice, maxPrice, startIdx, endIdx } = range;
        const priceHeight = height * 0.85;

        const color = COUNCIL_COLORS[activeCouncil];
        const closes = data.map(d => d.close);

        // Draw based on active council strategy
        if (activeCouncil === 'trend' || activeCouncil === 'fullAnalysis') {
            drawTrendAnalysis(ctx, closes, data, startIdx, endIdx, minPrice, maxPrice, priceHeight, barSpacing, scrollOffset, width);
        }

        if (activeCouncil === 'struct' || activeCouncil === 'fullAnalysis') {
            drawStructureAnalysis(ctx, structureLevels, minPrice, maxPrice, priceHeight, width);
        }

        if (activeCouncil === 'smart' || activeCouncil === 'fullAnalysis') {
            drawSmartMoneyAnalysis(ctx, orderBlocks, data, minPrice, maxPrice, priceHeight, barSpacing, scrollOffset, width);
        }

        if (activeCouncil === 'geom' || activeCouncil === 'fullAnalysis') {
            drawGeometryAnalysis(ctx, data, startIdx, endIdx, minPrice, maxPrice, priceHeight, width);
        }

        if (activeCouncil === 'indic' || activeCouncil === 'fullAnalysis') {
            drawIndicatorAnalysis(ctx, closes, data, startIdx, endIdx, minPrice, maxPrice, priceHeight, barSpacing, scrollOffset, width);
        }

        // Draw council label
        ctx.fillStyle = color;
        ctx.font = 'bold 10px Inter, Arial';
        ctx.textAlign = 'right';
        const councilLabels: Record<CouncilStrategy, string> = {
            fullAnalysis: 'FULL ANALYSIS',
            trend: 'TREND',
            struct: 'STRUCTURE',
            volume: 'VOLUME',
            smart: 'SMART MONEY',
            pattern: 'PATTERN',
            geom: 'GEOMETRY',
            indic: 'INDICATORS',
        };
        ctx.fillText(`⚔️ ${councilLabels[activeCouncil]}`, width - 90, 15);

    }, [width, height, data, barSpacing, scrollOffset, activeCouncil, structureLevels, orderBlocks]);

    // Trend Analysis: SMA lines
    function drawTrendAnalysis(
        ctx: CanvasRenderingContext2D,
        closes: number[],
        data: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        barSpacing: number,
        scrollOffset: number,
        canvasWidth: number
    ) {
        const sma20 = calculateSimpleSMA(closes, 20);
        const sma50 = calculateSimpleSMA(closes, 50);
        const sma200 = calculateSimpleSMA(closes, 200);

        const drawLine = (values: (number | null)[], color: string) => {
            ctx.strokeStyle = color;
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            let started = false;

            for (let i = startIdx; i <= endIdx && i < data.length; i++) {
                const val = values[i];
                if (val === null) continue;

                const x = timeToCoordinate(i, data.length, canvasWidth, barSpacing, scrollOffset);
                const y = priceToCoordinate(val, priceHeight, minPrice, maxPrice);

                if (!started) {
                    ctx.moveTo(x, y);
                    started = true;
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
        };

        drawLine(sma20, '#FFB800');
        drawLine(sma50, '#00BCD4');
        if (data.length > 200) {
            drawLine(sma200, '#FF5722');
        }
    }

    // Structure Analysis: Support/Resistance
    function drawStructureAnalysis(
        ctx: CanvasRenderingContext2D,
        levels: typeof structureLevels,
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        canvasWidth: number
    ) {
        for (const level of levels) {
            const y = priceToCoordinate(level.price, priceHeight, minPrice, maxPrice);
            const color = level.type === 'resistance' ? '#FF6B6B' : '#26a69a';

            ctx.strokeStyle = color;
            ctx.lineWidth = level.strength;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvasWidth, y);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = color;
            ctx.font = '9px Inter';
            ctx.textAlign = 'left';
            ctx.fillText(`${level.type === 'resistance' ? 'R' : 'S'}: ${level.price.toFixed(2)}`, 5, y - 3);
        }
    }

    // Smart Money Analysis: Order Blocks
    function drawSmartMoneyAnalysis(
        ctx: CanvasRenderingContext2D,
        blocks: typeof orderBlocks,
        data: CandleData[],
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        barSpacing: number,
        scrollOffset: number,
        canvasWidth: number
    ) {
        for (const block of blocks) {
            const x1 = timeToCoordinate(block.startIdx, data.length, canvasWidth, barSpacing, scrollOffset);
            const y1 = priceToCoordinate(block.high, priceHeight, minPrice, maxPrice);
            const y2 = priceToCoordinate(block.low, priceHeight, minPrice, maxPrice);

            const color = block.type === 'bullish' ? 'rgba(38, 166, 154, 0.3)' : 'rgba(239, 83, 80, 0.3)';
            const borderColor = block.type === 'bullish' ? '#26a69a' : '#ef5350';

            ctx.fillStyle = color;
            ctx.fillRect(x1, y1, canvasWidth - x1, y2 - y1);

            ctx.strokeStyle = borderColor;
            ctx.lineWidth = 1;
            ctx.strokeRect(x1, y1, canvasWidth - x1, y2 - y1);

            ctx.fillStyle = borderColor;
            ctx.font = 'bold 9px Inter';
            ctx.fillText(block.type === 'bullish' ? 'OB+' : 'OB-', x1 + 3, y1 + 12);
        }
    }

    // Geometry Analysis: Fibonacci
    function drawGeometryAnalysis(
        ctx: CanvasRenderingContext2D,
        data: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        canvasWidth: number
    ) {
        const visibleData = data.slice(startIdx, endIdx + 1);
        if (visibleData.length < 2) return;

        const highPrice = Math.max(...visibleData.map(d => d.high));
        const lowPrice = Math.min(...visibleData.map(d => d.low));
        const diff = highPrice - lowPrice;

        const fibLevels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];

        for (const level of fibLevels) {
            const price = lowPrice + diff * (1 - level);
            const y = priceToCoordinate(price, priceHeight, minPrice, maxPrice);

            ctx.strokeStyle = level === 0.5 ? '#FFD700' : '#2196F380';
            ctx.lineWidth = level === 0.5 || level === 0.618 ? 1.5 : 1;
            ctx.setLineDash(level === 0.5 ? [] : [3, 3]);
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvasWidth, y);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = '#2196F3';
            ctx.font = '9px Inter';
            ctx.fillText(`${(level * 100).toFixed(1)}%`, canvasWidth - 80, y - 2);
        }
    }

    // Indicator Analysis: Bollinger Bands
    function drawIndicatorAnalysis(
        ctx: CanvasRenderingContext2D,
        closes: number[],
        data: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        barSpacing: number,
        scrollOffset: number,
        canvasWidth: number
    ) {
        const bb = calculateSimpleBB(closes, 20, 2);

        const drawBBLine = (values: (number | null)[], color: string, lineWidth: number) => {
            ctx.strokeStyle = color;
            ctx.lineWidth = lineWidth;
            ctx.beginPath();
            let started = false;

            for (let i = startIdx; i <= endIdx && i < data.length; i++) {
                const val = values[i];
                if (val === null) continue;

                const x = timeToCoordinate(i, data.length, canvasWidth, barSpacing, scrollOffset);
                const y = priceToCoordinate(val, priceHeight, minPrice, maxPrice);

                if (!started) {
                    ctx.moveTo(x, y);
                    started = true;
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
        };

        drawBBLine(bb.upper, '#4CAF5080', 1);
        drawBBLine(bb.middle, '#4CAF50', 1.5);
        drawBBLine(bb.lower, '#4CAF5080', 1);
    }

    useEffect(() => {
        draw();
    }, [draw]);

    return (
        <canvas
            ref={canvasRef}
            style={{
                position: 'absolute',
                top: 0,
                left: 0,
                pointerEvents: 'none',
            }}
        />
    );
};

export default CouncilLayer;
