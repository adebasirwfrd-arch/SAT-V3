import React, { useState } from 'react';
import { useChartStore, CouncilStrategy, MethodologyType } from '../../store/chartStore';
import { ChartType } from '../../types';
import { CHART_TYPE_INFO } from '../../lib/chartTransformers';

const TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d', '1w'];

// Group chart types by category
const TIME_BASED_TYPES: ChartType[] = ['candle', 'bar', 'hollow', 'column', 'line', 'area', 'baseline', 'highLow', 'heikinAshi'];
const PRICE_BASED_TYPES: ChartType[] = ['renko', 'lineBreak', 'kagi', 'pointFigure', 'rangeBars'];

// The 7 Council Strategies
const COUNCIL_STRATEGIES = [
    { id: 'fullAnalysis' as CouncilStrategy, icon: '⚔️', label: 'Full Analysis', color: '#FFD700' },
    { id: 'trend' as CouncilStrategy, icon: '📈', label: 'Trend', color: '#00B4DB' },
    { id: 'struct' as CouncilStrategy, icon: '🏗️', label: 'Structure', color: '#FF6B6B' },
    { id: 'volume' as CouncilStrategy, icon: '📊', label: 'Volume', color: '#26a69a' },
    { id: 'smart' as CouncilStrategy, icon: '🧠', label: 'Smart Money', color: '#9C27B0' },
    { id: 'pattern' as CouncilStrategy, icon: '🔷', label: 'Pattern', color: '#FF9800' },
    { id: 'geom' as CouncilStrategy, icon: '📐', label: 'Geometry', color: '#2196F3' },
    { id: 'indic' as CouncilStrategy, icon: '📉', label: 'Indicators', color: '#4CAF50' },
];

// Methodology Options with hints
const METHODOLOGY_OPTIONS = [
    { id: 'none' as MethodologyType, icon: '📊', label: 'None', hint: 'No methodology overlay active.' },
    { id: 'accumulation' as MethodologyType, icon: '🔍', label: 'Accumulation', hint: 'Detects MM entry time with high volume + long wick candles. Best on 5min timeframe.' },
    { id: 'haBB' as MethodologyType, icon: '🎯', label: 'HA/BB Candles', hint: 'Green/Red when Heikin-Ashi and Bull-Bear agree. Yellow when they disagree.' },
    { id: 'dailyCandle' as MethodologyType, icon: '📅', label: 'Daily Candle', hint: 'Shows daily OHLC candle overlay on lower timeframes.' },
    { id: 'cfr' as MethodologyType, icon: '📐', label: 'CFR Formation', hint: 'Detects small-body candles, dojis, and accumulation formations.' },
    { id: 'renko' as MethodologyType, icon: '📈', label: 'Renko Bands', hint: 'Renko trend line with upper/lower bands showing brick thresholds.' },
    { id: 'inside' as MethodologyType, icon: '🕯️', label: 'Inside Candle', hint: 'Highlights candles fully engulfed by the previous candle range.' },
    { id: 'vsc' as MethodologyType, icon: '📊', label: 'Volume Spread', hint: 'Color-coded volume candles based on spread and volume analysis.' },
    { id: 'htf' as MethodologyType, icon: '🕰️', label: 'HTF Candles', hint: 'Visualizes higher timeframe candles (15m, 1h, 4h) on current chart.' },
    { id: 'pattern321' as MethodologyType, icon: '🔢', label: '321 Pattern', hint: 'Detects 3 consecutive candles with increasing body size suitable for reversal alerts.' },
    { id: 'ivd' as MethodologyType, icon: '📉', label: 'Intrabar Delta', hint: 'Shows estimated Up/Down volume and Delta stats per candle.' },
    { id: 'big_candle' as MethodologyType, icon: '🕯️', label: 'Big Candle', hint: 'Detects anomalously large candles (liquidity zones).' },
    { id: 'crt_po3' as MethodologyType, icon: '📦', label: 'CRT + PO3', hint: 'Accumulation, Manipulation, Distribution phases.' },
    { id: 'internal_strength' as MethodologyType, icon: '💪', label: 'Internal Strength', hint: 'Divides bars into rows to show bullish/bearish strength.' },
    { id: 'smart_bar_counter' as MethodologyType, icon: '🔢', label: 'Bar Counter', hint: 'Counts bars from a specific time or event.' },
    { id: 'lrc' as MethodologyType, icon: '📏', label: 'Linear Reg Candle', hint: 'Smoothed candles based on Linear Regression.' },
    { id: 'breakout_oscillator' as MethodologyType, icon: '🌊', label: 'Breakout Osc', hint: 'Oscillator showing market state (Bull/Bear/Chop).' },
    { id: 'vwap_rating' as MethodologyType, icon: '⭐', label: 'VWAP Rating', hint: 'Strong bearish candles below VWAP setup.' },
    { id: 'ma_candles' as MethodologyType, icon: '〰️', label: 'MA Candles', hint: 'Smoothed candles based on Moving Averages.' },
    // Methodology 6
    { id: 'crt_trend_filter' as MethodologyType, icon: '📉', label: 'CRT Trend', hint: 'Filters CRT signals with 50 EMA trend.' },
    { id: 'big_candles_filter' as MethodologyType, icon: '🕯️', label: 'Big Candles Filter', hint: 'Highlights candles with large bodies.' },
    { id: 'bbr1_volatility' as MethodologyType, icon: '📊', label: 'BBr1 Volatility', hint: 'Candle Range Volatility Gap Indicator.' },
    { id: 'ebp_marker' as MethodologyType, icon: '🚩', label: 'EBP Marker', hint: 'Highlights liquidity sweep candles.' },
    { id: 'momentum_exhaustion' as MethodologyType, icon: '🛑', label: 'Mom Exhaustion', hint: 'Detects trend exhaustion candles.' },
    { id: 'color_by_time' as MethodologyType, icon: '🕒', label: 'Time Color', hint: 'Colors candles within a specific time range.' },
    { id: 'bulldozz_ma' as MethodologyType, icon: '🏗️', label: 'BullDozz MA', hint: 'Candles based on various MA types.' },
    { id: 'bull_vs_bear' as MethodologyType, icon: '🆚', label: 'Bull vs Bear', hint: 'Counts bull/bear candles vs total.' },
    { id: 'last_candle_alert' as MethodologyType, icon: '🔔', label: 'Last Candle', hint: 'Highlights if last candle closes above/below previous.' },
    { id: 'truly_bull_bear' as MethodologyType, icon: '🐂', label: 'Truly Bull/Bear', hint: 'Strong open/close differential candles.' },
    { id: 'volume_delta_htf' as MethodologyType, icon: '📶', label: 'Vol Delta HTF', hint: 'Volume Delta Candles with HTF data.' },
];

/**
 * TopBar - Chart controls
 * Symbol selector, Timeframe, Chart Type (14 types), Council Strategy, Scale
 */
const TopBar: React.FC = () => {
    const { config, setConfig, chartType, setChartType, isConnected, theme, activeCouncil, setActiveCouncil, activeMethodology, setActiveMethodology } = useChartStore();
    const [showHints, setShowHints] = useState(false);

    const buttonStyle: React.CSSProperties = {
        padding: '5px 10px',
        border: `1px solid ${theme.gridLines}`,
        borderRadius: '4px',
        background: theme.background,
        color: theme.textPrimary,
        fontSize: '12px',
        cursor: 'pointer',
        transition: 'all 0.2s',
    };

    const activeButtonStyle: React.CSSProperties = {
        ...buttonStyle,
        background: theme.accent,
        color: '#FFFFFF',
        borderColor: theme.accent,
    };

    const selectedCouncil = COUNCIL_STRATEGIES.find(c => c.id === activeCouncil);

    return (
        <div
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '8px 12px',
                background: theme.background,
                borderBottom: `1px solid ${theme.gridLines}`,
                flexWrap: 'wrap',
            }}
        >
            {/* Symbol */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{
                    fontWeight: 'bold',
                    fontSize: '14px',
                    color: theme.textPrimary,
                }}>
                    {config.symbol}
                </span>
                <span style={{
                    padding: '2px 5px',
                    borderRadius: '4px',
                    fontSize: '9px',
                    background: isConnected ? '#089981' : '#FF6B6B',
                    color: '#FFFFFF',
                }}>
                    {isConnected ? 'LIVE' : 'OFF'}
                </span>
            </div>

            <div style={{ width: '1px', height: '20px', background: theme.gridLines }} />

            {/* Timeframe */}
            <div style={{ display: 'flex', gap: '3px' }}>
                {TIMEFRAMES.map(tf => (
                    <button
                        key={tf}
                        style={config.timeframe === tf ? activeButtonStyle : buttonStyle}
                        onClick={() => setConfig({ timeframe: tf })}
                    >
                        {tf}
                    </button>
                ))}
            </div>

            <div style={{ width: '1px', height: '20px', background: theme.gridLines }} />

            {/* Chart Type Dropdown */}
            <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value as ChartType)}
                style={{
                    ...buttonStyle,
                    minWidth: '130px',
                    padding: '5px 8px',
                }}
            >
                <optgroup label="📊 Time-Based">
                    {TIME_BASED_TYPES.map(ct => (
                        <option key={ct} value={ct}>
                            {CHART_TYPE_INFO[ct]?.icon || ''} {CHART_TYPE_INFO[ct]?.label || ct}
                        </option>
                    ))}
                </optgroup>
                <optgroup label="💎 Price-Based">
                    {PRICE_BASED_TYPES.map(ct => (
                        <option key={ct} value={ct}>
                            {CHART_TYPE_INFO[ct]?.icon || ''} {CHART_TYPE_INFO[ct]?.label || ct}
                        </option>
                    ))}
                </optgroup>
            </select>

            <div style={{ width: '1px', height: '20px', background: theme.gridLines }} />

            {/* The 7 Council Dropdown */}
            <select
                value={activeCouncil}
                onChange={(e) => setActiveCouncil(e.target.value as CouncilStrategy)}
                style={{
                    ...buttonStyle,
                    minWidth: '150px',
                    padding: '5px 8px',
                    borderColor: selectedCouncil?.color || theme.gridLines,
                    color: selectedCouncil?.color || theme.textPrimary,
                    fontWeight: 600,
                }}
            >
                <optgroup label="⚔️ The 7 Council">
                    {COUNCIL_STRATEGIES.map(strategy => (
                        <option
                            key={strategy.id}
                            value={strategy.id}
                            style={{ color: strategy.color }}
                        >
                            {strategy.icon} {strategy.label}
                        </option>
                    ))}
                </optgroup>
            </select>

            {/* Methodology Dropdown */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <select
                    value={activeMethodology}
                    onChange={(e) => setActiveMethodology(e.target.value as MethodologyType)}
                    style={{
                        ...buttonStyle,
                        minWidth: '140px',
                        padding: '5px 8px',
                        borderColor: activeMethodology !== 'none' ? '#9C27B0' : theme.gridLines,
                        color: activeMethodology !== 'none' ? '#9C27B0' : theme.textPrimary,
                        fontWeight: 600,
                    }}
                >
                    <optgroup label="📊 Methodology">
                        {METHODOLOGY_OPTIONS.map(m => (
                            <option key={m.id} value={m.id}>
                                {m.icon} {m.label}
                            </option>
                        ))}
                    </optgroup>
                </select>

                {/* Hints Button */}
                <button
                    style={{
                        ...buttonStyle,
                        padding: '5px 8px',
                        background: showHints ? '#9C27B0' : theme.background,
                        color: showHints ? '#FFF' : theme.textSecondary,
                        fontWeight: 600,
                    }}
                    onClick={() => setShowHints(!showHints)}
                    title="Show methodology hints"
                >
                    ?
                </button>
            </div>

            {/* Hints Popup */}
            {showHints && (
                <div style={{
                    position: 'absolute',
                    top: '100%',
                    right: '20px',
                    background: theme.background,
                    border: `1px solid ${theme.gridLines}`,
                    borderRadius: '8px',
                    padding: '12px',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
                    zIndex: 1000,
                    maxWidth: '300px',
                    fontSize: '11px',
                }}>
                    <div style={{ fontWeight: 600, marginBottom: '8px', color: '#9C27B0' }}>
                        📊 Methodology Hints
                    </div>
                    {METHODOLOGY_OPTIONS.filter(m => m.id !== 'none').map(m => (
                        <div key={m.id} style={{
                            padding: '6px 0',
                            borderBottom: `1px solid ${theme.gridLines}`,
                        }}>
                            <span style={{ fontWeight: 600 }}>{m.icon} {m.label}</span>
                            <p style={{ margin: '4px 0 0', color: theme.textSecondary }}>{m.hint}</p>
                        </div>
                    ))}
                </div>
            )}

            <div style={{ width: '1px', height: '20px', background: theme.gridLines }} />

            {/* Scale Toggle */}
            <button
                style={buttonStyle}
                onClick={() => setConfig({
                    scaleType: config.scaleType === 'linear' ? 'logarithmic' : 'linear'
                })}
            >
                {config.scaleType === 'linear' ? '📏 Lin' : '📐 Log'}
            </button>

            {/* Auto Scale Toggle */}
            <button
                style={config.autoScale ? activeButtonStyle : buttonStyle}
                onClick={() => setConfig({ autoScale: !config.autoScale })}
            >
                🔍 Auto
            </button>
        </div>
    );
};

export default TopBar;
