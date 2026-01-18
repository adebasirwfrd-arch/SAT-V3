import React, { useRef, useEffect, useState } from 'react';
import { useChartStore } from '../../store/chartStore';
import { useChartInteraction } from '../../hooks/useChartInteraction';
import { DrawingType } from '../../types';
import CanvasLayer from './CanvasLayer';
import CandleSeries from './CandleSeries';
import IndicatorLayer from './IndicatorLayer';
import DrawingLayer from './DrawingLayer';
import CursorLayer from './CursorLayer';
import VolumeProfileLayer from './VolumeProfileLayer';
import CouncilLayer from './CouncilLayer';
import MethodologyLayer from './MethodologyLayer';

interface ChartContainerProps {
    height?: number;
    activeTool?: DrawingType;
}

/**
 * ChartContainer - Main Chart Component
 * Now with 6 layered canvases:
 * 
 * Layer 1: Background, Grid, Watermark
 * Layer 2: Candles, Volume
 * Layer 3: Indicators (SMA, EMA, BB)
 * Layer 3.5: Volume Profile
 * Layer 4: Council Analysis (The 7 Council strategies)
 * Layer 5: Drawings (Trendlines, Fibo, Position)
 * Layer 6: Cursor (Crosshair, Tooltips)
 */
const ChartContainer: React.FC<ChartContainerProps> = ({
    height = 500,
    activeTool = 'none',
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 800, height });

    const {
        data,
        theme,
        barSpacing,
        scrollOffset,
        crosshair,
        chartType,
        config,
        candleCloseCountdown,
        indicators,
        drawings,
        addDrawing,
        activeCouncil,
    } = useChartStore();

    const {
        handleMouseDown,
        handleMouseMove,
        handleMouseUp,
        handleMouseLeave,
        handleWheel,
    } = useChartInteraction({ containerRef, width: dimensions.width });

    // Handle resize
    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                const rect = containerRef.current.getBoundingClientRect();
                setDimensions({ width: rect.width, height });
            }
        };

        updateDimensions();
        window.addEventListener('resize', updateDimensions);
        return () => window.removeEventListener('resize', updateDimensions);
    }, [height]);

    return (
        <div
            ref={containerRef}
            style={{
                position: 'relative',
                width: '100%',
                height: `${height}px`,
                backgroundColor: theme.background,
                cursor: activeTool !== 'none' ? 'crosshair' : 'default',
                overflow: 'hidden',
                borderRadius: '8px',
                boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
            }}
            onMouseDown={activeTool === 'none' ? handleMouseDown : undefined}
            onMouseMove={activeTool === 'none' ? handleMouseMove : undefined}
            onMouseUp={activeTool === 'none' ? handleMouseUp : undefined}
            onMouseLeave={activeTool === 'none' ? handleMouseLeave : undefined}
            onWheel={handleWheel}
        >
            {/* Layer 1: Background (Static) */}
            <CanvasLayer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
                symbol={config.symbol}
            />

            {/* Layer 2: Candles (Dynamic) */}
            <CandleSeries
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
                chartType={chartType}
            />

            {/* Layer 3: Indicators */}
            <IndicatorLayer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
                indicators={indicators}
            />

            {/* Layer 3.5: Volume Profile */}
            <VolumeProfileLayer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
                visible={true}
            />

            {/* Layer 4: Council Analysis (The 7 Council) */}
            <CouncilLayer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
                activeCouncil={activeCouncil}
            />

            {/* Layer 4.5: Methodology Analysis */}
            <MethodologyLayer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
            />

            {/* Layer 5: Drawings */}
            <DrawingLayer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
                drawings={drawings}
                activeTool={activeTool}
                onDrawingComplete={addDrawing}
            />

            {/* Layer 6: Cursor (Volatile) */}
            <CursorLayer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                theme={theme}
                barSpacing={barSpacing}
                scrollOffset={scrollOffset}
                crosshair={crosshair}
                candleCloseCountdown={candleCloseCountdown}
            />
        </div>
    );
};

export default ChartContainer;
