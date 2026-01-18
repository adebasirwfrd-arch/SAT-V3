import React, { useRef, useEffect, useCallback } from 'react';
import { ChartTheme, CandleData, VisibleRange } from '../../types';
import {
    priceToCoordinate,
    timeToCoordinate,
    calculateVisibleRange
} from '../../lib/math/coordinates';
import {
    transformToHeikinAshi,
    transformToRenko,
    transformToLineBreak,
    transformToRangeBars,
    isHollowCandle,
    ChartType,
} from '../../lib/chartTransformers';

interface CandleSeriesProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    chartType: ChartType;
}

/**
 * CandleSeries - Universal Chart Renderer
 * Supports 14 chart types with Factory Pattern
 */
const CandleSeries: React.FC<CandleSeriesProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    chartType,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    // Transform data based on chart type
    const getDisplayData = useCallback((): CandleData[] => {
        switch (chartType) {
            case 'heikinAshi':
                return transformToHeikinAshi(data);
            case 'renko':
                // Auto brick size based on price volatility
                const avgPrice = data.length > 0 ? data[data.length - 1].close : 100;
                const brickSize = avgPrice * 0.002; // 0.2% of price
                return transformToRenko(data, brickSize);
            case 'lineBreak':
                return transformToLineBreak(data, 3);
            case 'rangeBars':
                const rangeSize = data.length > 0 ? data[data.length - 1].close * 0.001 : 10;
                return transformToRangeBars(data, rangeSize);
            default:
                return data;
        }
    }, [data, chartType]);

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

        const displayData = getDisplayData();
        if (displayData.length === 0) return;

        const range: VisibleRange = calculateVisibleRange(displayData, width, barSpacing, scrollOffset);
        const { minPrice, maxPrice, startIdx, endIdx } = range;

        const volumeHeight = height * 0.15;
        const priceAreaHeight = height - volumeHeight;

        // Calculate max volume for scaling
        let maxVolume = 0;
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (candle && candle.volume > maxVolume) maxVolume = candle.volume;
        }

        const bodyWidth = Math.max(1, barSpacing * 0.8);
        const halfBody = bodyWidth / 2;

        // Render based on chart type
        switch (chartType) {
            case 'line':
                drawLine(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceAreaHeight);
                break;
            case 'area':
                drawArea(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceAreaHeight);
                break;
            case 'baseline':
                drawBaseline(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceAreaHeight);
                break;
            case 'highLow':
                drawHighLow(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceAreaHeight);
                break;
            case 'bar':
                drawBars(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceAreaHeight, bodyWidth);
                break;
            case 'column':
                drawColumn(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceAreaHeight, bodyWidth);
                break;
            default:
                // Candle-based types (candle, hollow, heikinAshi, renko, lineBreak, rangeBars)
                drawCandles(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceAreaHeight, bodyWidth, halfBody);
        }

        // Draw Volume (all types except column)
        if (chartType !== 'column' && maxVolume > 0) {
            drawVolume(ctx, displayData, startIdx, endIdx, volumeHeight, bodyWidth, halfBody, maxVolume);
        }

    }, [width, height, data, theme, barSpacing, scrollOffset, chartType, getDisplayData]);

    // ==================== RENDER FUNCTIONS ====================

    const drawCandles = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        bodyWidth: number,
        halfBody: number
    ) => {
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;

            // TradingView-style: Pixel-perfect positioning
            // Use Math.floor + 0.5 for crisp 1px lines
            const rawX = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const x = Math.floor(rawX);

            if (x < -bodyWidth || x > width + bodyWidth) continue;

            const isUp = candle.close >= candle.open;
            const prevCandle = i > 0 ? displayData[i - 1] : null;
            const isHollow = chartType === 'hollow' ? isHollowCandle(candle, prevCandle) : false;

            // TradingView official colors
            const bodyColor = isUp ? theme.bullishBody : theme.bearishBody;
            const wickColor = isUp ? theme.bullishWick : theme.bearishWick;

            // Calculate Y coordinates with pixel snapping
            const openY = Math.floor(priceToCoordinate(candle.open, priceHeight, minPrice, maxPrice));
            const closeY = Math.floor(priceToCoordinate(candle.close, priceHeight, minPrice, maxPrice));
            const highY = Math.floor(priceToCoordinate(candle.high, priceHeight, minPrice, maxPrice));
            const lowY = Math.floor(priceToCoordinate(candle.low, priceHeight, minPrice, maxPrice));

            // CRITICAL: Minimum body height of 1px (TradingView rule for Doji visibility)
            let bodyHeight = Math.abs(closeY - openY);
            if (bodyHeight < 1) bodyHeight = 1;

            const bodyTop = Math.min(openY, closeY);
            const bodyLeft = Math.floor(x - halfBody);
            const floorBodyWidth = Math.floor(bodyWidth);

            // 1. Draw Wick (crisp 1px line, perfectly centered)
            // Add 0.5 to align with pixel grid for sharp rendering
            const wickX = Math.floor(x) + 0.5;
            ctx.strokeStyle = wickColor;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(wickX, highY);
            ctx.lineTo(wickX, lowY);
            ctx.stroke();

            // 2. Draw Body
            if (chartType === 'hollow' && isHollow) {
                // Hollow candle: stroke only
                ctx.strokeStyle = bodyColor;
                ctx.lineWidth = 1;
                ctx.strokeRect(bodyLeft + 0.5, bodyTop + 0.5, floorBodyWidth - 1, bodyHeight);
            } else {
                // Filled candle body
                ctx.fillStyle = bodyColor;
                ctx.fillRect(bodyLeft, bodyTop, floorBodyWidth, bodyHeight);
            }
        }
    };

    const drawBars = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        bodyWidth: number
    ) => {
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;

            const x = Math.floor(timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset)) + 0.5;
            if (x < -bodyWidth || x > width + bodyWidth) continue;

            const isUp = candle.close >= candle.open;
            const color = isUp ? theme.bullishBody : theme.bearishBody;

            const openY = Math.floor(priceToCoordinate(candle.open, priceHeight, minPrice, maxPrice));
            const closeY = Math.floor(priceToCoordinate(candle.close, priceHeight, minPrice, maxPrice));
            const highY = Math.floor(priceToCoordinate(candle.high, priceHeight, minPrice, maxPrice)) + 0.5;
            const lowY = Math.floor(priceToCoordinate(candle.low, priceHeight, minPrice, maxPrice)) + 0.5;

            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.beginPath();

            // Vertical line (H-L)
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);

            // Open tick (left)
            ctx.moveTo(x - bodyWidth / 2, openY);
            ctx.lineTo(x, openY);

            // Close tick (right)
            ctx.moveTo(x, closeY);
            ctx.lineTo(x + bodyWidth / 2, closeY);

            ctx.stroke();
        }
    };

    const drawLine = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number
    ) => {
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 2;
        ctx.beginPath();

        let started = false;
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;

            const x = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const y = priceToCoordinate(candle.close, priceHeight, minPrice, maxPrice);

            if (!started) {
                ctx.moveTo(x, y);
                started = true;
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
    };

    const drawArea = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number
    ) => {
        // Create gradient fill
        const gradient = ctx.createLinearGradient(0, 0, 0, priceHeight);
        gradient.addColorStop(0, `${theme.bullishBody}60`);
        gradient.addColorStop(1, `${theme.bullishBody}05`);

        ctx.beginPath();

        let firstX = 0;
        let started = false;

        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;

            const x = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const y = priceToCoordinate(candle.close, priceHeight, minPrice, maxPrice);

            if (!started) {
                firstX = x;
                ctx.moveTo(x, y);
                started = true;
            } else {
                ctx.lineTo(x, y);
            }
        }

        // Close the path to bottom
        const lastX = timeToCoordinate(endIdx, displayData.length, width, barSpacing, scrollOffset);
        ctx.lineTo(lastX, priceHeight);
        ctx.lineTo(firstX, priceHeight);
        ctx.closePath();

        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw line on top
        drawLine(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceHeight);
    };

    const drawBaseline = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number
    ) => {
        // Calculate baseline (median price)
        const baseline = (minPrice + maxPrice) / 2;
        const baselineY = priceToCoordinate(baseline, priceHeight, minPrice, maxPrice);

        // Draw baseline
        ctx.strokeStyle = theme.textSecondary;
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(0, baselineY);
        ctx.lineTo(width, baselineY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Fill above (green) and below (red)
        for (let i = startIdx; i < endIdx; i++) {
            const candle = displayData[i];
            const nextCandle = displayData[i + 1];
            if (!candle || !nextCandle) continue;

            const x1 = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const x2 = timeToCoordinate(i + 1, displayData.length, width, barSpacing, scrollOffset);
            const y1 = priceToCoordinate(candle.close, priceHeight, minPrice, maxPrice);
            const y2 = priceToCoordinate(nextCandle.close, priceHeight, minPrice, maxPrice);

            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.lineTo(x2, baselineY);
            ctx.lineTo(x1, baselineY);
            ctx.closePath();

            const avgY = (y1 + y2) / 2;
            ctx.fillStyle = avgY < baselineY ? `${theme.bullishBody}40` : `${theme.bearishBody}40`;
            ctx.fill();
        }

        // Draw line
        drawLine(ctx, displayData, startIdx, endIdx, minPrice, maxPrice, priceHeight);
    };

    const drawHighLow = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number
    ) => {
        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, priceHeight);
        gradient.addColorStop(0, `${theme.bullishBody}30`);
        gradient.addColorStop(1, `${theme.bearishBody}30`);

        ctx.beginPath();

        // Draw high line
        let started = false;
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;
            const x = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const y = priceToCoordinate(candle.high, priceHeight, minPrice, maxPrice);
            if (!started) { ctx.moveTo(x, y); started = true; }
            else { ctx.lineTo(x, y); }
        }

        // Draw low line backward
        for (let i = endIdx; i >= startIdx; i--) {
            const candle = displayData[i];
            if (!candle) continue;
            const x = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const y = priceToCoordinate(candle.low, priceHeight, minPrice, maxPrice);
            ctx.lineTo(x, y);
        }

        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw high/low lines
        ctx.strokeStyle = theme.bullishBody;
        ctx.lineWidth = 1;
        ctx.beginPath();
        started = false;
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;
            const x = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const y = priceToCoordinate(candle.high, priceHeight, minPrice, maxPrice);
            if (!started) { ctx.moveTo(x, y); started = true; }
            else { ctx.lineTo(x, y); }
        }
        ctx.stroke();

        ctx.strokeStyle = theme.bearishBody;
        ctx.beginPath();
        started = false;
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;
            const x = timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset);
            const y = priceToCoordinate(candle.low, priceHeight, minPrice, maxPrice);
            if (!started) { ctx.moveTo(x, y); started = true; }
            else { ctx.lineTo(x, y); }
        }
        ctx.stroke();
    };

    const drawColumn = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        minPrice: number,
        maxPrice: number,
        priceHeight: number,
        bodyWidth: number
    ) => {
        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;

            const x = Math.floor(timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset));
            if (x < -bodyWidth || x > width + bodyWidth) continue;

            const isUp = candle.close >= candle.open;
            const color = isUp ? theme.bullishBody : theme.bearishBody;

            const closeY = priceToCoordinate(candle.close, priceHeight, minPrice, maxPrice);

            ctx.fillStyle = `${color}80`;
            ctx.fillRect(x - bodyWidth / 2, closeY, bodyWidth, priceHeight - closeY);
        }
    };

    const drawVolume = (
        ctx: CanvasRenderingContext2D,
        displayData: CandleData[],
        startIdx: number,
        endIdx: number,
        volumeHeight: number,
        bodyWidth: number,
        halfBody: number,
        maxVolume: number
    ) => {
        const volumeTop = height - volumeHeight;

        for (let i = startIdx; i <= endIdx; i++) {
            const candle = displayData[i];
            if (!candle) continue;

            const x = Math.floor(timeToCoordinate(i, displayData.length, width, barSpacing, scrollOffset));
            if (x < -bodyWidth || x > width + bodyWidth) continue;

            const isUp = candle.close >= candle.open;
            const volHeight = (candle.volume / maxVolume) * volumeHeight;
            const volY = height - volHeight;

            ctx.fillStyle = isUp
                ? `${theme.bullishBody}30`
                : `${theme.bearishBody}30`;
            ctx.fillRect(x - halfBody, volY, bodyWidth, volHeight);
        }
    };

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

export default CandleSeries;
