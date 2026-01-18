import { useEffect, useRef, useCallback } from 'react';
import { CandleData } from '../types';
import { useChartStore } from '../store/chartStore';

// Use local FastAPI server or fallback to Binance Testnet
const getBaseUrl = () => {
    // When running from FastAPI at /chart, use relative API path
    if (window.location.pathname.startsWith('/chart')) {
        return '';  // Use same origin
    }
    // When running standalone dev server
    return '';
};

const BINANCE_WS_URL = 'wss://stream.binance.com:9443/ws';

/**
 * Filter and fix outliers from candle data
 * Handles Binance Testnet data quality issues with extreme wicks
 * Strategy: Keep all candles but clamp extreme high/low wicks
 */
function filterOutliers(candles: CandleData[]): CandleData[] {
    if (candles.length < 10) return candles;

    // Calculate median close price for reference
    const closes = candles.map(c => c.close).sort((a, b) => a - b);
    const medianClose = closes[Math.floor(closes.length / 2)];

    // Maximum allowed wick extension: 5% beyond body (very conservative)
    // This means if body is 95000-95500, high can be max 100275 and low min 90250
    const maxWickExtension = 0.05;

    return candles.map(c => {
        const bodyHigh = Math.max(c.open, c.close);
        const bodyLow = Math.min(c.open, c.close);

        // Clamp high to reasonable wick
        const maxAllowedHigh = bodyHigh * (1 + maxWickExtension);
        const minAllowedLow = bodyLow * (1 - maxWickExtension);

        return {
            ...c,
            high: Math.min(c.high, maxAllowedHigh),
            low: Math.max(c.low, minAllowedLow),
        };
    });
}

/**
 * Get default number of visible candles based on timeframe
 * This ensures candles are properly sized and not "gepeng" (squashed)
 */
function getDefaultVisibleCandles(timeframe: string): number {
    switch (timeframe) {
        case '1m': return 120;   // 2 hours
        case '5m': return 48;    // 4 hours
        case '15m': return 32;   // 8 hours
        case '1h': return 48;    // 2 days
        case '4h': return 30;    // 5 days
        case '1d': return 60;    // 2 months
        case '1w': return 26;    // 6 months
        default: return 100;
    }
}

/**
 * Calculate optimal bar spacing to fit visible candles to width
 * Ensures candles are proportional and the chart is "fit to width"
 */
function calculateAutoBarSpacing(
    viewportWidth: number,
    visibleCandles: number,
    rightMargin: number = 80
): number {
    const effectiveWidth = viewportWidth - rightMargin;
    const spacing = effectiveWidth / visibleCandles;
    // Clamp to reasonable range: min 4px, max 50px
    return Math.max(4, Math.min(50, spacing));
}

interface UseDataStreamOptions {
    symbol: string;
    timeframe: string;
    onConnect?: () => void;
    onDisconnect?: () => void;
}

export function useDataStream({ symbol, timeframe, onConnect, onDisconnect }: UseDataStreamOptions) {
    const wsRef = useRef<WebSocket | null>(null);
    const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const { setData, updateLastCandle, appendCandle, setConnected, setCandleCloseCountdown, setBarSpacing, data } = useChartStore();

    // Fetch data from local FastAPI server
    const fetchHistoricalData = useCallback(async () => {
        try {
            const baseUrl = getBaseUrl();
            const symbolForApi = symbol.replace('/', '-');
            const url = `${baseUrl}/api/ohlcv/${symbolForApi}?timeframe=${timeframe}&limit=10000`;

            console.log('[Data] Fetching from:', url);
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const candles = await response.json();

            if (Array.isArray(candles) && candles.length > 0) {
                const formattedCandles: CandleData[] = candles.map((c: Record<string, unknown>) => ({
                    time: (c.time as number) * 1000, // Convert to ms if needed
                    open: c.open as number,
                    high: c.high as number,
                    low: c.low as number,
                    close: c.close as number,
                    volume: c.volume as number,
                }));

                // Filter out outliers from Binance Testnet data
                const cleanedCandles = filterOutliers(formattedCandles);
                console.log(`[Data] Filtered ${formattedCandles.length - cleanedCandles.length} outlier candles`);

                // Calculate auto bar spacing for fit-to-width
                const defaultVisible = getDefaultVisibleCandles(timeframe);
                const viewportWidth = window.innerWidth - 50; // Account for toolbar
                const autoSpacing = calculateAutoBarSpacing(viewportWidth, defaultVisible);
                setBarSpacing(autoSpacing);
                console.log(`[Data] Auto barSpacing: ${autoSpacing}px for ${defaultVisible} visible candles`);

                setData(cleanedCandles);
                setConnected(true);
                console.log(`[Data] Loaded ${cleanedCandles.length} candles from server`);
                return cleanedCandles;
            }

            return [];
        } catch (error) {
            console.error('[Data] Failed to fetch historical data:', error);
            setConnected(false);
            return [];
        }
    }, [symbol, timeframe, setData, setConnected, setBarSpacing]);

    // Poll for updates (fallback when WebSocket not available)
    const startPolling = useCallback(() => {
        if (pollIntervalRef.current) return;

        console.log('[Poll] Starting polling for updates...');

        pollIntervalRef.current = setInterval(async () => {
            try {
                const baseUrl = getBaseUrl();
                const symbolForApi = symbol.replace('/', '-');
                const url = `${baseUrl}/api/ohlcv/${symbolForApi}?timeframe=${timeframe}&limit=5`;

                const response = await fetch(url);
                const candles = await response.json();

                if (Array.isArray(candles) && candles.length > 0) {
                    const latest = candles[candles.length - 1];
                    const formattedCandle: CandleData = {
                        time: (latest.time as number) * 1000,
                        open: latest.open as number,
                        high: latest.high as number,
                        low: latest.low as number,
                        close: latest.close as number,
                        volume: latest.volume as number,
                    };

                    // Update or append
                    updateLastCandle(formattedCandle);

                    // Calculate countdown (estimate for 1m candle)
                    const now = Date.now();
                    const candleEndTime = formattedCandle.time + 60000; // 1 minute
                    const remaining = Math.max(0, Math.floor((candleEndTime - now) / 1000));
                    setCandleCloseCountdown(remaining);
                }
            } catch (error) {
                console.error('[Poll] Update error:', error);
            }
        }, 5000); // Poll every 5 seconds
    }, [symbol, timeframe, updateLastCandle, setCandleCloseCountdown]);

    // Try WebSocket (optional - may fail in some environments)
    const tryWebSocket = useCallback(() => {
        try {
            const streamName = `${symbol.toLowerCase().replace('/', '')}@kline_${timeframe}`;
            const ws = new WebSocket(`${BINANCE_WS_URL}/${streamName}`);

            ws.onopen = () => {
                console.log('[WS] Connected to Binance');
                setConnected(true);
                onConnect?.();

                // Stop polling if WS connected
                if (pollIntervalRef.current) {
                    clearInterval(pollIntervalRef.current);
                    pollIntervalRef.current = null;
                }
            };

            ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.e === 'kline') {
                        const k = msg.k;
                        const candle: CandleData = {
                            time: k.t,
                            open: parseFloat(k.o),
                            high: parseFloat(k.h),
                            low: parseFloat(k.l),
                            close: parseFloat(k.c),
                            volume: parseFloat(k.v),
                        };

                        const closeTime = k.T;
                        const now = Date.now();
                        const remaining = Math.max(0, Math.floor((closeTime - now) / 1000));
                        setCandleCloseCountdown(remaining);

                        if (k.x) {
                            appendCandle(candle);
                        } else {
                            updateLastCandle(candle);
                        }
                    }
                } catch (e) {
                    console.error('[WS] Parse error:', e);
                }
            };

            ws.onclose = () => {
                console.log('[WS] Closed - falling back to polling');
                setConnected(true); // Still connected via polling
                onDisconnect?.();
                startPolling();
            };

            ws.onerror = () => {
                console.log('[WS] Error - using polling instead');
                ws.close();
            };

            wsRef.current = ws;
        } catch (error) {
            console.log('[WS] Failed to connect, using polling');
            startPolling();
        }
    }, [symbol, timeframe, setConnected, updateLastCandle, appendCandle, setCandleCloseCountdown, onConnect, onDisconnect, startPolling]);

    // Disconnect
    const disconnect = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
        }
    }, []);

    // Initialize
    useEffect(() => {
        fetchHistoricalData().then((candles) => {
            if (candles.length > 0) {
                // Try WebSocket for real-time, fall back to polling
                tryWebSocket();
            }
        });

        return () => {
            disconnect();
        };
    }, [fetchHistoricalData, tryWebSocket, disconnect]);

    return { disconnect, fetchHistoricalData };
}
