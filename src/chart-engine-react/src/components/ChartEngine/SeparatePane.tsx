import React, { useRef, useEffect, useCallback } from 'react';
import { ChartTheme, CandleData } from '../../types';
import { timeToCoordinate, calculateVisibleRange } from '../../lib/math/coordinates';
import { calculateRSI, calculateMACD } from '../../lib/indicators';

interface SeparatePaneProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    indicatorType: 'RSI' | 'MACD';
    period?: number;
}

/**
 * SeparatePane - Indicator pane below main chart
 * Renders: RSI or MACD with histogram
 */
const SeparatePane: React.FC<SeparatePaneProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    indicatorType,
    period = 14,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

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

        // Background
        ctx.fillStyle = theme.background;
        ctx.fillRect(0, 0, width, height);

        const range = calculateVisibleRange(data, width, barSpacing, scrollOffset);
        const { startIdx, endIdx } = range;

        if (indicatorType === 'RSI') {
            drawRSI(ctx, startIdx, endIdx);
        } else if (indicatorType === 'MACD') {
            drawMACD(ctx, startIdx, endIdx);
        }

        // Border
        ctx.strokeStyle = theme.gridLines;
        ctx.lineWidth = 1;
        ctx.strokeRect(0, 0, width, height);

    }, [width, height, data, theme, barSpacing, scrollOffset, indicatorType, period]);

    const drawRSI = useCallback((ctx: CanvasRenderingContext2D, startIdx: number, endIdx: number) => {
        const rsiValues = calculateRSI(data, period);

        // RSI Range: 0-100
        const minVal = 0;
        const maxVal = 100;

        // Draw zones
        // Overbought zone (70-100)
        ctx.fillStyle = 'rgba(255, 107, 107, 0.1)';
        const overboughtY = valueToY(70, minVal, maxVal);
        ctx.fillRect(0, 0, width, overboughtY);

        // Oversold zone (0-30)
        ctx.fillStyle = 'rgba(0, 180, 219, 0.1)';
        const oversoldY = valueToY(30, minVal, maxVal);
        ctx.fillRect(0, oversoldY, width, height - oversoldY);

        // Draw level lines
        ctx.strokeStyle = theme.gridLines;
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);

        [30, 50, 70].forEach(level => {
            const y = valueToY(level, minVal, maxVal);
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();

            // Label
            ctx.fillStyle = theme.textSecondary;
            ctx.font = '10px Inter, Arial';
            ctx.fillText(level.toString(), width - 25, y + 3);
        });
        ctx.setLineDash([]);

        // Draw RSI line
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 1.5;
        ctx.beginPath();

        let started = false;
        for (let i = startIdx; i <= endIdx; i++) {
            if (rsiValues[i] === null) continue;

            const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
            const y = valueToY(rsiValues[i]!, minVal, maxVal);

            if (!started) {
                ctx.moveTo(x, y);
                started = true;
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();

        // Label
        ctx.fillStyle = theme.textPrimary;
        ctx.font = 'bold 11px Inter, Arial';
        ctx.fillText(`RSI(${period})`, 8, 15);

        // Current value
        const lastRSI = rsiValues[data.length - 1];
        if (lastRSI !== null) {
            const color = lastRSI > 70 ? theme.bearishBody : lastRSI < 30 ? theme.bullishBody : theme.textPrimary;
            ctx.fillStyle = color;
            ctx.fillText(lastRSI.toFixed(2), 70, 15);
        }

    }, [data, period, width, height, barSpacing, scrollOffset, theme]);

    const drawMACD = useCallback((ctx: CanvasRenderingContext2D, startIdx: number, endIdx: number) => {
        const macd = calculateMACD(data);

        // Find min/max for scaling
        let minVal = Infinity;
        let maxVal = -Infinity;

        for (let i = startIdx; i <= endIdx; i++) {
            if (macd.macd[i] !== null) {
                minVal = Math.min(minVal, macd.macd[i]!, macd.signal[i] || Infinity);
                maxVal = Math.max(maxVal, macd.macd[i]!, macd.signal[i] || -Infinity);
            }
            if (macd.histogram[i] !== null) {
                minVal = Math.min(minVal, macd.histogram[i]!);
                maxVal = Math.max(maxVal, macd.histogram[i]!);
            }
        }

        if (minVal === Infinity) { minVal = -1; maxVal = 1; }
        const padding = (maxVal - minVal) * 0.1;
        minVal -= padding;
        maxVal += padding;

        // Draw zero line
        const zeroY = valueToY(0, minVal, maxVal);
        ctx.strokeStyle = theme.gridLines;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, zeroY);
        ctx.lineTo(width, zeroY);
        ctx.stroke();

        // Draw histogram
        const barWidth = Math.max(1, barSpacing * 0.6);
        for (let i = startIdx; i <= endIdx; i++) {
            if (macd.histogram[i] === null) continue;

            const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
            const y = valueToY(macd.histogram[i]!, minVal, maxVal);
            const barHeight = Math.abs(y - zeroY);

            ctx.fillStyle = macd.histogram[i]! >= 0
                ? 'rgba(0, 180, 219, 0.6)'
                : 'rgba(255, 107, 107, 0.6)';

            if (macd.histogram[i]! >= 0) {
                ctx.fillRect(x - barWidth / 2, y, barWidth, barHeight);
            } else {
                ctx.fillRect(x - barWidth / 2, zeroY, barWidth, barHeight);
            }
        }

        // Draw MACD line
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        let started = false;
        for (let i = startIdx; i <= endIdx; i++) {
            if (macd.macd[i] === null) continue;
            const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
            const y = valueToY(macd.macd[i]!, minVal, maxVal);
            if (!started) { ctx.moveTo(x, y); started = true; }
            else { ctx.lineTo(x, y); }
        }
        ctx.stroke();

        // Draw Signal line
        ctx.strokeStyle = '#FF6B00';
        ctx.lineWidth = 1;
        ctx.beginPath();
        started = false;
        for (let i = startIdx; i <= endIdx; i++) {
            if (macd.signal[i] === null) continue;
            const x = timeToCoordinate(i, data.length, width, barSpacing, scrollOffset);
            const y = valueToY(macd.signal[i]!, minVal, maxVal);
            if (!started) { ctx.moveTo(x, y); started = true; }
            else { ctx.lineTo(x, y); }
        }
        ctx.stroke();

        // Label
        ctx.fillStyle = theme.textPrimary;
        ctx.font = 'bold 11px Inter, Arial';
        ctx.fillText('MACD(12,26,9)', 8, 15);

    }, [data, width, height, barSpacing, scrollOffset, theme]);

    const valueToY = (value: number, min: number, max: number): number => {
        const range = max - min;
        if (range === 0) return height / 2;
        const normalized = (value - min) / range;
        return height - normalized * height;
    };

    useEffect(() => {
        draw();
    }, [draw]);

    return (
        <canvas
            ref={canvasRef}
            style={{ display: 'block', borderRadius: '4px' }}
        />
    );
};

export default SeparatePane;
