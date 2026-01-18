import React, { useRef, useEffect, useCallback } from 'react';
import { ChartTheme, CandleData, VisibleRange } from '../../types';
import {
    priceToCoordinate,
    timeToCoordinate,
    calculateVisibleRange
} from '../../lib/math/coordinates';

interface CanvasLayerProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    symbol: string;
}

/**
 * CanvasLayer - Background Layer (Static)
 * Renders: Grid lines, Watermark, Session Breaks
 * Only re-renders on resize/pan
 */
const CanvasLayer: React.FC<CanvasLayerProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    symbol,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext('2d');
        if (!canvas || !ctx || data.length === 0) return;

        const pixelRatio = window.devicePixelRatio || 1;

        // Setup High-DPI
        canvas.width = width * pixelRatio;
        canvas.height = height * pixelRatio;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.scale(pixelRatio, pixelRatio);

        const range: VisibleRange = calculateVisibleRange(data, width, barSpacing, scrollOffset);
        const { minPrice, maxPrice } = range;

        // 1. Background
        ctx.fillStyle = theme.background;
        ctx.fillRect(0, 0, width, height);

        // 2. Watermark (Symbol)
        ctx.save();
        ctx.font = 'bold 48px Inter, Arial, sans-serif';
        ctx.fillStyle = theme.watermark;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(symbol, width / 2, height / 2);
        ctx.restore();

        // 3. Grid Lines (Horizontal - Price)
        ctx.strokeStyle = theme.gridLines;
        ctx.lineWidth = 1;
        ctx.beginPath();

        const priceRange = maxPrice - minPrice;
        const numLines = 8;
        const priceStep = priceRange / numLines;

        for (let i = 0; i <= numLines; i++) {
            const price = minPrice + i * priceStep;
            const y = Math.floor(priceToCoordinate(price, height, minPrice, maxPrice)) + 0.5;
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
        }

        // 4. Grid Lines (Vertical - Time)
        const pxPerLabel = 100;
        const barsPerLabel = Math.ceil(pxPerLabel / barSpacing);

        for (let i = data.length - 1; i >= 0; i -= barsPerLabel) {
            const x = Math.floor(timeToCoordinate(i, data.length, width, barSpacing, scrollOffset)) + 0.5;
            if (x < -50) break;
            if (x > width + 50) continue;
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
        }

        ctx.stroke();

        // 5. Price Labels (Right Axis)
        ctx.fillStyle = theme.textSecondary;
        ctx.font = '11px Inter, Arial, sans-serif';
        ctx.textAlign = 'right';

        for (let i = 0; i <= numLines; i++) {
            const price = minPrice + i * priceStep;
            const y = priceToCoordinate(price, height, minPrice, maxPrice);
            const label = price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            ctx.fillText(label, width - 5, y + 4);
        }

        // 6. Time Labels (Bottom Axis)
        ctx.textAlign = 'center';
        for (let i = data.length - 1; i >= 0; i -= barsPerLabel) {
            const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
            if (x < 50 || x > width - 100) continue;

            const candle = data[i];
            if (!candle) continue;

            const date = new Date(candle.time);
            const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            ctx.fillText(timeStr, x, height - 5);
        }

    }, [width, height, data, theme, barSpacing, scrollOffset, symbol]);

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

export default CanvasLayer;
