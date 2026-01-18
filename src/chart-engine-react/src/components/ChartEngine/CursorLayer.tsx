import React, { useRef, useEffect, useCallback } from 'react';
import { ChartTheme, CandleData, VisibleRange } from '../../types';
import {
    priceToCoordinate,
    timeToCoordinate,
    coordinateToPrice,
    coordinateToIndex,
    calculateVisibleRange
} from '../../lib/math/coordinates';

interface CursorLayerProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    crosshair: { x: number; y: number } | null;
    candleCloseCountdown: number;
}

/**
 * CursorLayer - Interaction Layer (Volatile)
 * Renders: Crosshair, Price label, Time label, Countdown
 * Re-renders at 60fps when cursor moves
 */
const CursorLayer: React.FC<CursorLayerProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    crosshair,
    candleCloseCountdown,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext('2d');
        if (!canvas || !ctx) return;

        const pixelRatio = window.devicePixelRatio || 1;

        // Setup High-DPI
        canvas.width = width * pixelRatio;
        canvas.height = height * pixelRatio;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.scale(pixelRatio, pixelRatio);

        // Clear
        ctx.clearRect(0, 0, width, height);

        if (data.length === 0) return;

        const range: VisibleRange = calculateVisibleRange(data, width, barSpacing, scrollOffset);
        const { minPrice, maxPrice } = range;
        const volumeHeight = height * 0.2;
        const priceAreaHeight = height - volumeHeight;

        // Draw Countdown to Close (always visible)
        if (candleCloseCountdown > 0 && data.length > 0) {
            const lastCandle = data[data.length - 1];
            const lastY = priceToCoordinate(lastCandle.close, priceAreaHeight, minPrice, maxPrice);

            const minutes = Math.floor(candleCloseCountdown / 60);
            const seconds = candleCloseCountdown % 60;
            const countdownText = `${minutes}:${seconds.toString().padStart(2, '0')}`;

            // Draw countdown label
            ctx.font = 'bold 10px Inter, Arial, sans-serif';
            const textWidth = ctx.measureText(countdownText).width + 8;

            ctx.fillStyle = theme.accent;
            ctx.fillRect(width - textWidth - 5, lastY - 8, textWidth, 16);

            ctx.fillStyle = '#FFFFFF';
            ctx.textAlign = 'right';
            ctx.fillText(countdownText, width - 9, lastY + 4);
        }

        // Draw Current Price Line
        if (data.length > 0) {
            const lastCandle = data[data.length - 1];
            const lastY = priceToCoordinate(lastCandle.close, priceAreaHeight, minPrice, maxPrice);

            ctx.strokeStyle = theme.accent;
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(0, lastY);
            ctx.lineTo(width - 80, lastY);
            ctx.stroke();
            ctx.setLineDash([]);

            // Price label
            const priceLabel = lastCandle.close.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            ctx.font = 'bold 11px Inter, Arial, sans-serif';
            const labelWidth = ctx.measureText(priceLabel).width + 10;

            ctx.fillStyle = theme.accent;
            ctx.fillRect(width - labelWidth - 5, lastY - 10, labelWidth + 5, 20);

            ctx.fillStyle = '#FFFFFF';
            ctx.textAlign = 'right';
            ctx.fillText(priceLabel, width - 8, lastY + 4);
        }

        // Draw Crosshair
        if (crosshair) {
            const { x, y } = crosshair;

            // Dashed lines
            ctx.strokeStyle = theme.crosshair;
            ctx.lineWidth = 1;
            ctx.setLineDash([6, 6]);

            ctx.beginPath();
            // Horizontal
            ctx.moveTo(0, y);
            ctx.lineTo(width - 80, y);
            // Vertical
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height - 30);
            ctx.stroke();
            ctx.setLineDash([]);

            // Price Label (Y-axis)
            const price = coordinateToPrice(y, priceAreaHeight, minPrice, maxPrice);
            const priceText = price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

            ctx.font = '11px Inter, Arial, sans-serif';
            const priceWidth = ctx.measureText(priceText).width + 10;

            ctx.fillStyle = theme.textPrimary;
            ctx.fillRect(width - priceWidth - 5, y - 10, priceWidth + 5, 20);

            ctx.fillStyle = '#FFFFFF';
            ctx.textAlign = 'right';
            ctx.fillText(priceText, width - 8, y + 4);

            // Time Label (X-axis)
            const index = coordinateToIndex(x, data.length, width, barSpacing, scrollOffset);
            const candle = data[index];
            if (candle) {
                const date = new Date(candle.time);
                const timeText = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

                ctx.fillStyle = theme.textPrimary;
                const timeWidth = ctx.measureText(timeText).width + 10;
                ctx.fillRect(x - timeWidth / 2, height - 20, timeWidth, 18);

                ctx.fillStyle = '#FFFFFF';
                ctx.textAlign = 'center';
                ctx.fillText(timeText, x, height - 6);
            }
        }

    }, [width, height, data, theme, barSpacing, scrollOffset, crosshair, candleCloseCountdown]);

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

export default CursorLayer;
