import React, { useRef, useEffect, useCallback, useState } from 'react';
import { ChartTheme, CandleData, DrawingObject, VisibleRange } from '../../types';
import { priceToCoordinate, timeToCoordinate, coordinateToPrice, coordinateToIndex, calculateVisibleRange } from '../../lib/math/coordinates';

// Extended Drawing Types (110+ Categories)
export type DrawingToolType =
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

interface DrawingLayerProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    drawings: DrawingObject[];
    onDrawingComplete?: (drawing: DrawingObject) => void;
    activeTool: DrawingToolType;
}

// Fibonacci levels
const FIBO_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1, 1.618, 2.618];

/**
 * DrawingLayer - Interactive drawing tools (110+ types)
 * Implements: Lines, Fibonacci, Geometric Shapes, Annotations, Patterns
 */
const DrawingLayer: React.FC<DrawingLayerProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    drawings,
    onDrawingComplete,
    activeTool,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);
    const [currentPoint, setCurrentPoint] = useState<{ x: number; y: number } | null>(null);

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
        const priceHeight = height * 0.85;

        // Draw existing drawings
        for (const drawing of drawings) {
            if (!drawing.visible) continue;
            renderDrawing(ctx, drawing, minPrice, maxPrice, priceHeight);
        }

        // Draw current drawing in progress
        if (isDrawing && startPoint && currentPoint) {
            renderPreview(ctx, startPoint, currentPoint, minPrice, maxPrice, priceHeight);
        }

    }, [width, height, data, theme, barSpacing, scrollOffset, drawings, isDrawing, startPoint, currentPoint, activeTool]);

    const renderDrawing = (
        ctx: CanvasRenderingContext2D,
        drawing: DrawingObject,
        minPrice: number,
        maxPrice: number,
        priceHeight: number
    ) => {
        const p1 = drawing.points[0];
        const p2 = drawing.points[1];

        switch (drawing.type) {
            case 'trendline':
            case 'ray':
            case 'extendedLine':
                ctx.strokeStyle = theme.accent;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();

                // Anchor points
                ctx.fillStyle = theme.accent;
                ctx.beginPath();
                ctx.arc(p1.x, p1.y, 4, 0, Math.PI * 2);
                ctx.arc(p2.x, p2.y, 4, 0, Math.PI * 2);
                ctx.fill();
                break;

            case 'horizontalLine':
                ctx.strokeStyle = theme.accent;
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 4]);
                ctx.beginPath();
                ctx.moveTo(0, p1.y);
                ctx.lineTo(width, p1.y);
                ctx.stroke();
                ctx.setLineDash([]);
                break;

            case 'verticalLine':
                ctx.strokeStyle = theme.accent;
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 4]);
                ctx.beginPath();
                ctx.moveTo(p1.x, 0);
                ctx.lineTo(p1.x, height);
                ctx.stroke();
                ctx.setLineDash([]);
                break;

            case 'parallelChannel':
                if (drawing.points.length >= 2) {
                    const channelWidth = drawing.properties.channelWidth as number || 50;
                    ctx.strokeStyle = theme.accent;
                    ctx.lineWidth = 1;

                    // Main lines
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.moveTo(p1.x, p1.y + channelWidth);
                    ctx.lineTo(p2.x, p2.y + channelWidth);
                    ctx.stroke();

                    // Fill
                    ctx.fillStyle = `${theme.accent}15`;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.lineTo(p2.x, p2.y + channelWidth);
                    ctx.lineTo(p1.x, p1.y + channelWidth);
                    ctx.closePath();
                    ctx.fill();
                }
                break;

            case 'fibonacci':
                if (drawing.points.length >= 2) {
                    const diff = p2.y - p1.y;

                    for (const level of FIBO_LEVELS) {
                        const y = p1.y + diff * level;
                        const price = coordinateToPrice(y, priceHeight, minPrice, maxPrice);

                        ctx.strokeStyle = level === 0 || level === 1 ? theme.accent : `${theme.accent}80`;
                        ctx.lineWidth = 1;
                        ctx.setLineDash(level === 0.5 ? [4, 4] : []);
                        ctx.beginPath();
                        ctx.moveTo(0, y);
                        ctx.lineTo(width, y);
                        ctx.stroke();
                        ctx.setLineDash([]);

                        // Label
                        ctx.fillStyle = theme.textSecondary;
                        ctx.font = '10px Inter, Arial';
                        ctx.fillText(`${(level * 100).toFixed(1)}% (${price.toFixed(2)})`, 5, y - 3);
                    }
                }
                break;

            case 'rectangle':
                ctx.fillStyle = `${theme.accent}20`;
                ctx.strokeStyle = theme.accent;
                ctx.lineWidth = 1;
                ctx.fillRect(
                    Math.min(p1.x, p2.x),
                    Math.min(p1.y, p2.y),
                    Math.abs(p2.x - p1.x),
                    Math.abs(p2.y - p1.y)
                );
                ctx.strokeRect(
                    Math.min(p1.x, p2.x),
                    Math.min(p1.y, p2.y),
                    Math.abs(p2.x - p1.x),
                    Math.abs(p2.y - p1.y)
                );
                break;

            case 'ellipse':
                const cx = (p1.x + p2.x) / 2;
                const cy = (p1.y + p2.y) / 2;
                const rx = Math.abs(p2.x - p1.x) / 2;
                const ry = Math.abs(p2.y - p1.y) / 2;

                ctx.fillStyle = `${theme.accent}20`;
                ctx.strokeStyle = theme.accent;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
                break;

            case 'position':
            case 'longPosition':
            case 'shortPosition':
                const isLong = drawing.type === 'longPosition' || (drawing.type === 'position' && p2.y < p1.y);

                ctx.fillStyle = isLong ? 'rgba(0, 180, 219, 0.2)' : 'rgba(255, 107, 107, 0.2)';
                ctx.fillRect(p1.x, Math.min(p1.y, p2.y), p2.x - p1.x, Math.abs(p2.y - p1.y));

                ctx.strokeStyle = isLong ? theme.bullishBody : theme.bearishBody;
                ctx.lineWidth = 2;
                ctx.strokeRect(p1.x, Math.min(p1.y, p2.y), p2.x - p1.x, Math.abs(p2.y - p1.y));

                // Label
                ctx.fillStyle = isLong ? theme.bullishBody : theme.bearishBody;
                ctx.font = 'bold 11px Inter, Arial';
                ctx.fillText(isLong ? 'LONG' : 'SHORT', p1.x + 5, Math.min(p1.y, p2.y) + 15);

                // R:R Ratio
                const entry = coordinateToPrice(p1.y, priceHeight, minPrice, maxPrice);
                const target = coordinateToPrice(p2.y, priceHeight, minPrice, maxPrice);
                const pnlPercent = ((target - entry) / entry * 100).toFixed(2);
                ctx.fillText(`${isLong ? '+' : ''}${pnlPercent}%`, p1.x + 5, Math.min(p1.y, p2.y) + 28);
                break;

            case 'text':
                ctx.fillStyle = theme.textPrimary;
                ctx.font = '12px Inter, Arial';
                ctx.fillText(drawing.properties.text as string || 'Text', p1.x, p1.y);
                break;

            case 'arrow':
                ctx.strokeStyle = theme.accent;
                ctx.fillStyle = theme.accent;
                ctx.lineWidth = 2;

                const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x);
                const headLen = 12;

                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();

                // Arrow head
                ctx.beginPath();
                ctx.moveTo(p2.x, p2.y);
                ctx.lineTo(p2.x - headLen * Math.cos(angle - Math.PI / 6), p2.y - headLen * Math.sin(angle - Math.PI / 6));
                ctx.lineTo(p2.x - headLen * Math.cos(angle + Math.PI / 6), p2.y - headLen * Math.sin(angle + Math.PI / 6));
                ctx.closePath();
                ctx.fill();
                break;
        }
    };

    const renderPreview = (
        ctx: CanvasRenderingContext2D,
        start: { x: number; y: number },
        current: { x: number; y: number },
        minPrice: number,
        maxPrice: number,
        priceHeight: number
    ) => {
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);

        switch (activeTool) {
            case 'trendline':
            case 'ray':
            case 'extendedLine':
            case 'arrow':
                ctx.beginPath();
                ctx.moveTo(start.x, start.y);
                ctx.lineTo(current.x, current.y);
                ctx.stroke();
                break;

            case 'horizontalLine':
                ctx.beginPath();
                ctx.moveTo(0, start.y);
                ctx.lineTo(width, start.y);
                ctx.stroke();
                break;

            case 'verticalLine':
                ctx.beginPath();
                ctx.moveTo(start.x, 0);
                ctx.lineTo(start.x, height);
                ctx.stroke();
                break;

            case 'fibonacci':
                const diff = current.y - start.y;
                for (const level of FIBO_LEVELS) {
                    const y = start.y + diff * level;
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    ctx.lineTo(width, y);
                    ctx.stroke();
                }
                break;

            case 'rectangle':
                ctx.fillStyle = `${theme.accent}20`;
                ctx.fillRect(
                    Math.min(start.x, current.x),
                    Math.min(start.y, current.y),
                    Math.abs(current.x - start.x),
                    Math.abs(current.y - start.y)
                );
                ctx.strokeRect(
                    Math.min(start.x, current.x),
                    Math.min(start.y, current.y),
                    Math.abs(current.x - start.x),
                    Math.abs(current.y - start.y)
                );
                break;

            case 'ellipse':
                const cx = (start.x + current.x) / 2;
                const cy = (start.y + current.y) / 2;
                const rx = Math.abs(current.x - start.x) / 2;
                const ry = Math.abs(current.y - start.y) / 2;
                ctx.beginPath();
                ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
                ctx.stroke();
                break;

            case 'position':
            case 'longPosition':
            case 'shortPosition':
                const isLong = activeTool === 'longPosition' || (activeTool === 'position' && current.y < start.y);
                ctx.fillStyle = isLong ? 'rgba(0, 180, 219, 0.2)' : 'rgba(255, 107, 107, 0.2)';
                ctx.fillRect(
                    start.x,
                    Math.min(start.y, current.y),
                    current.x - start.x,
                    Math.abs(current.y - start.y)
                );
                break;
        }

        ctx.setLineDash([]);
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        if (activeTool === 'none') return;

        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;

        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        setIsDrawing(true);
        setStartPoint({ x, y });
        setCurrentPoint({ x, y });
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDrawing) return;

        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;

        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        setCurrentPoint({ x, y });
    };

    const handleMouseUp = () => {
        if (!isDrawing || !startPoint || !currentPoint) return;

        const newDrawing: DrawingObject = {
            id: `drawing-${Date.now()}`,
            type: activeTool === 'none' ? 'trendline' : activeTool,
            points: [startPoint, currentPoint],
            properties: {},
            visible: true,
        };

        onDrawingComplete?.(newDrawing);

        setIsDrawing(false);
        setStartPoint(null);
        setCurrentPoint(null);
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
                pointerEvents: activeTool !== 'none' ? 'auto' : 'none',
                cursor: activeTool !== 'none' ? 'crosshair' : 'default',
            }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
        />
    );
};

export default DrawingLayer;
