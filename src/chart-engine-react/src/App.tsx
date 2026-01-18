import React, { useState } from 'react';
import ChartContainer from './components/ChartEngine/ChartContainer';
import SeparatePane from './components/ChartEngine/SeparatePane';
import TopBar from './components/UI/TopBar';
import Toolbar from './components/UI/Toolbar';
import { useDataStream } from './hooks/useDataStream';
import { useChartStore } from './store/chartStore';
import { DrawingType } from './types';

/**
 * SAT-V3 Advanced Charting Module
 * TradingView Clone with Ocean Calm Theme
 */
function App() {
    const { config, theme, data, isConnected, barSpacing, scrollOffset } = useChartStore();
    const [activeTool, setActiveTool] = useState<DrawingType>('none');
    const [activePane, setActivePane] = useState<'none' | 'RSI' | 'MACD'>('none');

    // Connect to Binance Testnet
    useDataStream({
        symbol: config.symbol,
        timeframe: config.timeframe,
    });

    // Get last candle for OHLCV display
    const lastCandle = data[data.length - 1];
    const prevCandle = data[data.length - 2];
    const change = lastCandle && prevCandle
        ? ((lastCandle.close - prevCandle.close) / prevCandle.close * 100)
        : 0;

    return (
        <div style={{
            width: '100vw',
            height: '100vh',
            background: '#F5F7FA',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
        }}>
            {/* Header */}
            <header style={{
                padding: '10px 20px',
                background: theme.background,
                borderBottom: `1px solid ${theme.gridLines}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexShrink: 0,
            }}>
                <h1 style={{
                    margin: 0,
                    fontSize: '16px',
                    color: theme.textPrimary,
                    fontWeight: 600,
                }}>
                    📈 SAT-V3 Supercharts
                </h1>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    fontSize: '12px',
                }}>
                    <span style={{
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background: isConnected ? '#089981' : '#FF6B6B',
                        color: '#FFF',
                        fontSize: '10px',
                        fontWeight: 600,
                    }}>
                        {isConnected ? '🔴 LIVE' : 'OFFLINE'}
                    </span>
                    <span style={{ color: theme.textSecondary }}>
                        {data.length} candles
                    </span>
                </div>
            </header>

            {/* Main Content */}
            <main style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                {/* Left Toolbar */}
                <Toolbar
                    activeTool={activeTool}
                    onToolChange={setActiveTool}
                    activePane={activePane}
                    onPaneChange={setActivePane}
                />

                {/* Chart Area */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                    {/* Top Bar */}
                    <TopBar />

                    {/* OHLCV Bar */}
                    {lastCandle && (
                        <div style={{
                            display: 'flex',
                            gap: '16px',
                            padding: '6px 12px',
                            background: theme.background,
                            borderBottom: `1px solid ${theme.gridLines}`,
                            fontSize: '12px',
                            flexShrink: 0,
                        }}>
                            <span><b style={{ color: theme.textSecondary }}>O</b> {lastCandle.open.toLocaleString()}</span>
                            <span><b style={{ color: theme.textSecondary }}>H</b> <span style={{ color: theme.bullishBody }}>{lastCandle.high.toLocaleString()}</span></span>
                            <span><b style={{ color: theme.textSecondary }}>L</b> <span style={{ color: theme.bearishBody }}>{lastCandle.low.toLocaleString()}</span></span>
                            <span><b style={{ color: theme.textSecondary }}>C</b> {lastCandle.close.toLocaleString()}</span>
                            <span><b style={{ color: theme.textSecondary }}>V</b> {lastCandle.volume.toFixed(2)}</span>
                            <span style={{ color: change >= 0 ? theme.bullishBody : theme.bearishBody, fontWeight: 600 }}>
                                {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                            </span>
                        </div>
                    )}

                    {/* Chart */}
                    <div style={{ flex: 1, minHeight: 0, padding: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div style={{ flex: activePane !== 'none' ? '0 0 70%' : 1 }}>
                            <ChartContainer
                                height={activePane !== 'none' ? 350 : 500}
                                activeTool={activeTool}
                            />
                        </div>

                        {/* Separate Pane (RSI/MACD) */}
                        {activePane !== 'none' && (
                            <div style={{
                                flex: '0 0 120px',
                                background: theme.background,
                                borderRadius: '8px',
                                padding: '4px',
                                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                            }}>
                                <SeparatePane
                                    width={800}
                                    height={110}
                                    data={data}
                                    theme={theme}
                                    barSpacing={barSpacing}
                                    scrollOffset={scrollOffset}
                                    indicatorType={activePane}
                                />
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
