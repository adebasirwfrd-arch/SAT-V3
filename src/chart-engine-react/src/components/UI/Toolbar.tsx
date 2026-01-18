import React, { useState } from 'react';
import { useChartStore } from '../../store/chartStore';
import { DrawingType } from '../../types';

interface ToolbarProps {
    activeTool: DrawingType;
    onToolChange: (tool: DrawingType) => void;
    activePane: 'none' | 'RSI' | 'MACD';
    onPaneChange: (pane: 'none' | 'RSI' | 'MACD') => void;
}

// Tool Categories
const TOOL_CATEGORIES = [
    {
        name: 'Selection',
        tools: [{ id: 'none', icon: '🖱️', label: 'Select' }],
    },
    {
        name: 'Lines',
        tools: [
            { id: 'trendline', icon: '📏', label: 'Trendline' },
            { id: 'ray', icon: '➡️', label: 'Ray' },
            { id: 'horizontalLine', icon: '➖', label: 'Horizontal' },
            { id: 'verticalLine', icon: '|', label: 'Vertical' },
            { id: 'parallelChannel', icon: '≡', label: 'Channel' },
        ],
    },
    {
        name: 'Fibonacci',
        tools: [
            { id: 'fibonacci', icon: '🔢', label: 'Fib Retracement' },
        ],
    },
    {
        name: 'Shapes',
        tools: [
            { id: 'rectangle', icon: '⬜', label: 'Rectangle' },
            { id: 'ellipse', icon: '⭕', label: 'Ellipse' },
        ],
    },
    {
        name: 'Position',
        tools: [
            { id: 'longPosition', icon: '📈', label: 'Long' },
            { id: 'shortPosition', icon: '📉', label: 'Short' },
        ],
    },
    {
        name: 'Annotation',
        tools: [
            { id: 'arrow', icon: '➤', label: 'Arrow' },
            { id: 'text', icon: 'T', label: 'Text' },
        ],
    },
] as const;

const OVERLAY_INDICATORS = [
    { type: 'SMA', label: 'SMA', period: 20, color: '#FFB800' },
    { type: 'EMA', label: 'EMA', period: 20, color: '#00BCD4' },
    { type: 'BB', label: 'BB', period: 20, stdDev: 2, color: '#2196F3' },
    { type: 'VWAP', label: 'VWAP', period: 0, color: '#FF9800' },
    { type: 'SAR', label: 'SAR', period: 0, color: '#F44336' },
];

const PANE_INDICATORS = [
    { id: 'RSI', label: 'RSI' },
    { id: 'MACD', label: 'MACD' },
] as const;

/**
 * Toolbar - Left sidebar with 6 categories of tools
 */
const Toolbar: React.FC<ToolbarProps> = ({
    activeTool,
    onToolChange,
    activePane,
    onPaneChange,
}) => {
    const { theme, indicators, addIndicator, removeIndicator } = useChartStore();
    const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

    const buttonStyle: React.CSSProperties = {
        width: '32px',
        height: '32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: `1px solid ${theme.gridLines}`,
        borderRadius: '6px',
        background: theme.background,
        cursor: 'pointer',
        fontSize: '14px',
        transition: 'all 0.2s',
    };

    const activeStyle: React.CSSProperties = {
        ...buttonStyle,
        background: theme.accent,
        borderColor: theme.accent,
    };

    const toggleIndicator = (ind: typeof OVERLAY_INDICATORS[0]) => {
        const existing = indicators.find(
            i => i.type === ind.type && i.params.period === ind.period
        );

        if (existing) {
            removeIndicator(existing.id);
        } else {
            addIndicator({
                id: `${ind.type}-${ind.period}-${Date.now()}`,
                type: ind.type,
                params: { period: ind.period, stdDev: ind.stdDev || 0 },
                color: ind.color,
                visible: true,
                pane: 'main',
            });
        }
    };

    const isIndicatorActive = (ind: typeof OVERLAY_INDICATORS[0]) => {
        return indicators.some(
            i => i.type === ind.type && i.params.period === ind.period && i.visible
        );
    };

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '4px',
            padding: '8px',
            background: theme.background,
            borderRight: `1px solid ${theme.gridLines}`,
            width: '50px',
            overflow: 'auto',
        }}>
            {/* Drawing Tools */}
            {TOOL_CATEGORIES.map(category => (
                <div key={category.name}>
                    {category.tools.map(tool => (
                        <button
                            key={tool.id}
                            style={activeTool === tool.id ? activeStyle : buttonStyle}
                            onClick={() => onToolChange(tool.id as DrawingType)}
                            title={tool.label}
                        >
                            {tool.icon}
                        </button>
                    ))}
                </div>
            ))}

            <div style={{ height: '1px', background: theme.gridLines, margin: '4px 0' }} />

            {/* Overlay Indicators */}
            <div style={{ fontSize: '8px', color: theme.textSecondary, textAlign: 'center', marginBottom: '2px' }}>
                IND
            </div>
            {OVERLAY_INDICATORS.map((ind, idx) => (
                <button
                    key={idx}
                    style={{
                        ...buttonStyle,
                        fontSize: '8px',
                        fontWeight: isIndicatorActive(ind) ? 'bold' : 'normal',
                        background: isIndicatorActive(ind) ? `${ind.color}30` : theme.background,
                        borderColor: isIndicatorActive(ind) ? ind.color : theme.gridLines,
                        color: isIndicatorActive(ind) ? ind.color : theme.textSecondary,
                    }}
                    onClick={() => toggleIndicator(ind)}
                    title={ind.label}
                >
                    {ind.label}
                </button>
            ))}

            <div style={{ height: '1px', background: theme.gridLines, margin: '4px 0' }} />

            {/* Pane Indicators */}
            {PANE_INDICATORS.map(pane => (
                <button
                    key={pane.id}
                    style={{
                        ...buttonStyle,
                        fontSize: '9px',
                        fontWeight: activePane === pane.id ? 'bold' : 'normal',
                        background: activePane === pane.id ? `${theme.accent}30` : theme.background,
                        borderColor: activePane === pane.id ? theme.accent : theme.gridLines,
                        color: activePane === pane.id ? theme.accent : theme.textSecondary,
                    }}
                    onClick={() => onPaneChange(activePane === pane.id ? 'none' : pane.id)}
                    title={pane.label}
                >
                    {pane.label}
                </button>
            ))}
        </div>
    );
};

export default Toolbar;
