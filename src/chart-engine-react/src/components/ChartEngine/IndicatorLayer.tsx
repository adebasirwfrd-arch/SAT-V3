import React, { useRef, useEffect, useCallback } from 'react';
import { ChartTheme, CandleData, IndicatorConfig, VisibleRange } from '../../types';
import { priceToCoordinate, timeToCoordinate, calculateVisibleRange } from '../../lib/math/coordinates';
import { calculateSMA, calculateEMA, calculateBollingerBands } from '../../lib/indicators';

interface IndicatorLayerProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    indicators: IndicatorConfig[];
}

/**
 * IndicatorLayer - Overlay indicators on main chart
 * Renders: SMA, EMA, Bollinger Bands as smooth curves
 */
const IndicatorLayer: React.FC<IndicatorLayerProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    indicators,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const drawBezierCurve = useCallback((
        ctx: CanvasRenderingContext2D,
        values: (number | null)[],
        color: string,
        minPrice: number,
        maxPrice: number,
        priceHeight: number
    ) => {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();

        let started = false;
        let prevX = 0;
        let prevY = 0;

        for (let i = 0; i < values.length; i++) {
            if (values[i] === null) {
                started = false;
                continue;
            }

            const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
            const y = priceToCoordinate(values[i]!, priceHeight, minPrice, maxPrice);

            if (x < -50 || x > width + 50) continue;

            if (!started) {
                ctx.moveTo(x, y);
                started = true;
            } else {
                // Bezier curve for smoothness
                const cpX = (prevX + x) / 2;
                ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y);
            }

            prevX = x;
            prevY = y;
        }

        ctx.stroke();
    }, [data.length, width, barSpacing, scrollOffset]);

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
        const { minPrice, maxPrice } = range;
        const priceHeight = height * 0.8; // Same as CandleSeries

        for (const indicator of indicators) {
            if (!indicator.visible || indicator.pane !== 'main') continue;

            let values: (number | null)[] = [];

            switch (indicator.type) {
                case 'SMA':
                    values = calculateSMA(data, indicator.params.period || 20);
                    drawBezierCurve(ctx, values, indicator.color, minPrice, maxPrice, priceHeight);
                    break;

                case 'EMA':
                    values = calculateEMA(data, indicator.params.period || 20);
                    drawBezierCurve(ctx, values, indicator.color, minPrice, maxPrice, priceHeight);
                    break;

                case 'BB':
                    const bb = calculateBollingerBands(data, indicator.params.period || 20, indicator.params.stdDev || 2);
                    // Draw bands with fill
                    ctx.fillStyle = `${indicator.color}20`;
                    ctx.beginPath();

                    // Upper band forward
                    let started = false;
                    for (let i = 0; i < bb.upper.length; i++) {
                        if (bb.upper[i] === null) continue;
                        const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
                        const y = priceToCoordinate(bb.upper[i]!, priceHeight, minPrice, maxPrice);
                        if (!started) {
                            ctx.moveTo(x, y);
                            started = true;
                        } else {
                            ctx.lineTo(x, y);
                        }
                    }

                    // Lower band backward
                    for (let i = bb.lower.length - 1; i >= 0; i--) {
                        if (bb.lower[i] === null) continue;
                        const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
                        const y = priceToCoordinate(bb.lower[i]!, priceHeight, minPrice, maxPrice);
                        ctx.lineTo(x, y);
                    }

                    ctx.closePath();
                    ctx.fill();

                    // Draw lines
                    drawBezierCurve(ctx, bb.upper, indicator.color, minPrice, maxPrice, priceHeight);
                    drawBezierCurve(ctx, bb.middle, indicator.color, minPrice, maxPrice, priceHeight);
                    drawBezierCurve(ctx, bb.lower, indicator.color, minPrice, maxPrice, priceHeight);
                    break;
            }
        }
    }, [width, height, data, barSpacing, scrollOffset, indicators, drawBezierCurve]);

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

export default IndicatorLayer;
