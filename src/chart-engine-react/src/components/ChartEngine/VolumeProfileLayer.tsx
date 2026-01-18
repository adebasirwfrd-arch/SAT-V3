import React, { useRef, useEffect, useCallback } from 'react';
import { ChartTheme, CandleData, VisibleRange } from '../../types';
import { calculateVisibleRange, priceToCoordinate } from '../../lib/math/coordinates';
import { calculateVolumeProfile, VolumeProfileLevel } from '../../lib/indicators';

interface VolumeProfileLayerProps {
    width: number;
    height: number;
    data: CandleData[];
    theme: ChartTheme;
    barSpacing: number;
    scrollOffset: number;
    visible: boolean;
}

/**
 * VolumeProfileLayer - Volume Profile (VPVR) Histogram
 * Renders horizontal volume bars on the right side of chart
 */
const VolumeProfileLayer: React.FC<VolumeProfileLayerProps> = ({
    width,
    height,
    data,
    theme,
    barSpacing,
    scrollOffset,
    visible,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext('2d');
        if (!canvas || !ctx || !visible || data.length === 0) return;

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

        // Calculate volume profile
        const profile = calculateVolumeProfile(data, startIdx, endIdx, 30);
        if (profile.length === 0) return;

        // Find max volume for scaling
        const maxVol = Math.max(...profile.map(p => p.volume));
        if (maxVol === 0) return;

        const profileWidth = 80; // Right margin area
        const barHeight = priceHeight / profile.length;

        // Find POC (Point of Control)
        let pocIndex = 0;
        for (let i = 1; i < profile.length; i++) {
            if (profile[i].volume > profile[pocIndex].volume) pocIndex = i;
        }

        // Draw profile bars
        for (let i = 0; i < profile.length; i++) {
            const level = profile[i];
            const y = priceToCoordinate(level.priceLevel, priceHeight, minPrice, maxPrice);
            const barWidth = (level.volume / maxVol) * profileWidth;

            const isPOC = i === pocIndex;

            // Buy volume (left side - teal)
            const buyWidth = (level.buyVolume / level.volume) * barWidth || 0;
            ctx.fillStyle = isPOC ? theme.bullishBody : `${theme.bullishBody}50`;
            ctx.fillRect(width - profileWidth, y - barHeight / 2, buyWidth, barHeight - 1);

            // Sell volume (right side - red)
            const sellWidth = barWidth - buyWidth;
            ctx.fillStyle = isPOC ? theme.bearishBody : `${theme.bearishBody}50`;
            ctx.fillRect(width - profileWidth + buyWidth, y - barHeight / 2, sellWidth, barHeight - 1);
        }

        // POC line
        const pocY = priceToCoordinate(profile[pocIndex].priceLevel, priceHeight, minPrice, maxPrice);
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(0, pocY);
        ctx.lineTo(width - profileWidth, pocY);
        ctx.stroke();
        ctx.setLineDash([]);

        // POC label
        ctx.fillStyle = theme.accent;
        ctx.font = 'bold 9px Inter, Arial';
        ctx.fillText('POC', 5, pocY - 3);

    }, [width, height, data, theme, barSpacing, scrollOffset, visible]);

    useEffect(() => {
        draw();
    }, [draw]);

    if (!visible) return null;

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

export default VolumeProfileLayer;
