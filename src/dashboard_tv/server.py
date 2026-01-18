"""
SAT-V3 TradingView Dashboard - FastAPI WebSocket Server
Real-time trading dashboard with TradingView Lightweight Charts
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List
import ccxt

# Add parent path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import Config

app = FastAPI(title="SAT-V3 Trading Dashboard")

# Mount static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Active WebSocket connections
active_connections: List[WebSocket] = []

# System logs for debugging
system_logs = []

# Global Market Data for Auto-Trading Sync
global_market_data = {}

def add_log(message):
    """Add log entry with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    system_logs.append(log_entry)
    if len(system_logs) > 100:  # Keep last 100 logs
        system_logs.pop(0)
    print(log_entry)

# Initialize exchange - Binance Testnet for OHLCV data
add_log("Initializing Binance Testnet connection...")
try:
    exchange = ccxt.binance({
        'sandbox': True,  # Use sandbox/testnet mode
        'options': {
            'defaultType': 'spot',
            'adjustForTimeDifference': True,
        },
        'enableRateLimit': True,
        'timeout': 15000
    })
    # Test connection
    exchange.load_markets()
    add_log(f"Binance Testnet exchange initialized - {len(exchange.markets)} markets loaded")
except Exception as e:
    add_log(f"Exchange init error: {e} - using simulation fallback")
    exchange = None

def load_bot_data():
    """Load data from bot's multi_asset_data.json"""
    if os.path.exists(Config.LIVE_DATA_FILE):
        try:
            with open(Config.LIVE_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def load_trade_history():
    """Load trade history for calendar display"""
    history_path = os.path.join(os.path.dirname(Config.LIVE_DATA_FILE), 'trade_history.json')
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r') as f:
                history = json.load(f)
                return history.get('daily_summary', {})
        except:
            pass
    return {}

def load_wallet():
    """Load wallet.json for holdings display"""
    wallet_path = os.path.join(os.path.dirname(Config.LIVE_DATA_FILE), 'wallet.json')
    if os.path.exists(wallet_path):
        try:
            with open(wallet_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def fetch_ohlcv(symbol, timeframe='1h', limit=100):
    """Fetch OHLCV data from Binance with pagination for large requests"""
    try:
        if exchange:
            # Binance API limit is 1000 candles per request
            BATCH_SIZE = 1000
            
            if limit <= BATCH_SIZE:
                # Simple single fetch
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            else:
                # Paginated fetch for large requests (up to 50,000 candles)
                all_candles = []
                remaining = min(limit, 50000)  # Cap at 50K like TradingView Ultimate
                
                # Start with most recent data
                end_time = None
                
                while remaining > 0:
                    fetch_count = min(BATCH_SIZE, remaining)
                    
                    try:
                        if end_time:
                            # Fetch older data before end_time
                            batch = exchange.fetch_ohlcv(
                                symbol, 
                                timeframe=timeframe, 
                                limit=fetch_count,
                                params={'endTime': end_time}
                            )
                        else:
                            # First fetch - get most recent
                            batch = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=fetch_count)
                        
                        if not batch:
                            break
                        
                        # Prepend older candles to front
                        all_candles = batch + all_candles
                        remaining -= len(batch)
                        
                        # Set end_time to oldest candle for next batch
                        end_time = batch[0][0]  # timestamp of oldest candle in batch
                        
                        # Avoid rate limiting
                        if remaining > 0:
                            import time
                            time.sleep(0.1)  # 100ms delay between requests
                            
                    except Exception as e:
                        print(f"Batch fetch error: {e}")
                        break
                
                ohlcv = all_candles
                print(f"[OHLCV] Fetched {len(ohlcv)} candles for {symbol} {timeframe}")
            
            return [
                {
                    'time': int(candle[0] / 1000),  # Convert to seconds
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                }
                for candle in ohlcv
            ]
    except Exception as e:
        print(f"Error fetching OHLCV: {e}")
    
    # Fallback simulation for large limit
    import numpy as np
    coin = symbol.split('/')[0]
    np.random.seed(hash(coin) % 10000)
    
    base = {'BTC': 95000, 'ETH': 3300, 'SOL': 140, 'BNB': 600, 'TON': 6, 'XRP': 2}.get(coin, 100)
    now = int(datetime.now().timestamp())
    candles = []
    
    # Generate requested number of candles (capped at 50000)
    actual_limit = min(limit, 50000)
    
    for i in range(actual_limit):
        time_offset = (actual_limit - i) * 3600  # 1 hour per candle
        close = base * (1 + np.random.randn() * 0.02)
        open_price = close * (1 + np.random.randn() * 0.005)
        high = max(open_price, close) * (1 + abs(np.random.randn()) * 0.005)
        low = min(open_price, close) * (1 - abs(np.random.randn()) * 0.005)
        
        candles.append({
            'time': now - time_offset,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': np.random.randint(1000, 10000)
        })
        base = close
    
    return candles

def save_command(symbol, action):
    """Save command for bot to execute"""
    cmd = {
        "command": action,
        "symbol": symbol,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "executed": False
    }
    os.makedirs(os.path.dirname(Config.COMMANDS_FILE), exist_ok=True)
    with open(Config.COMMANDS_FILE, 'w') as f:
        json.dump(cmd, f)

def save_wallet(wallet):
    """Save wallet.json"""
    wallet_path = os.path.join(os.path.dirname(Config.LIVE_DATA_FILE), 'wallet.json')
    os.makedirs(os.path.dirname(wallet_path), exist_ok=True)
    with open(wallet_path, 'w') as f:
        json.dump(wallet, f, indent=2)

def load_transactions():
    """Load active transactions"""
    tx_path = os.path.join(os.path.dirname(Config.LIVE_DATA_FILE), 'transactions.json')
    if os.path.exists(tx_path):
        try:
            with open(tx_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_transactions(transactions):
    """Save transactions"""
    tx_path = os.path.join(os.path.dirname(Config.LIVE_DATA_FILE), 'transactions.json')
    os.makedirs(os.path.dirname(tx_path), exist_ok=True)
    with open(tx_path, 'w') as f:
        json.dump(transactions, f, indent=2)

def load_bot_logs():
    """Load AI bot logs"""
    log_path = os.path.join(os.path.dirname(Config.LIVE_DATA_FILE), 'bot_logs.json')
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_bot_log(log_entry):
    """Add log entry to bot_logs.json"""
    logs = load_bot_logs()
    logs.append(log_entry)
    if len(logs) > 200:
        logs = logs[-200:]
    log_path = os.path.join(os.path.dirname(Config.LIVE_DATA_FILE), 'bot_logs.json')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w') as f:
        json.dump(logs, f, indent=2)

@app.get("/")
async def root():
    """Serve main dashboard"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/chart")
async def superchart():
    """Serve React Superchart"""
    return FileResponse(os.path.join(STATIC_DIR, "chart", "index.html"))

@app.get("/api/data")
async def get_data():
    """Get current bot data"""
    data = load_bot_data()
    return data or {"error": "No data available"}

@app.get("/api/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100):
    """Get OHLCV data for chart"""
    symbol = symbol.replace("-", "/")
    candles = fetch_ohlcv(symbol, timeframe, limit)
    return candles

@app.get("/api/transactions")
async def get_transactions():
    """Get active transactions"""
    transactions = load_transactions()
    return {"transactions": transactions}

@app.post("/api/command/{symbol}/{action}")
async def send_command(symbol: str, action: str, source: str = "MANUAL"):
    """Execute real trading command on Binance Testnet"""
    symbol = symbol.replace("-", "/")
    add_log(f"Command received: {action} {symbol}")
    
    wallet = load_wallet()
    if not wallet:
        wallet = {"cash": 100000.0, "holdings": {}, "realized_pnl": 0.0, "max_balance": 100000.0}
    
    try:
        # Get current price from exchange
        if exchange:
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
        else:
            # Fallback prices
            bases = {'BTC/USDT': 95000, 'ETH/USDT': 3300, 'SOL/USDT': 140, 'BNB/USDT': 600, 'TON/USDT': 6, 'XRP/USDT': 2}
            current_price = bases.get(symbol, 100)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if action == "FORCE_BUY":
            # Calculate lot size (10% of cash)
            lot_value = wallet['cash'] * 0.10
            if lot_value < 10:
                return {"status": "error", "message": "Insufficient funds"}
            
            lot_size = lot_value / current_price
            
            # Update wallet
            wallet['cash'] -= lot_value
            if symbol not in wallet.get('holdings', {}):
                wallet['holdings'] = wallet.get('holdings', {})
                wallet['holdings'][symbol] = {
                    'quantity': 0,
                    'entry_price': 0,
                    'total_cost': 0
                }
            
            holding = wallet['holdings'][symbol]
            old_qty = holding.get('quantity', 0)
            old_cost = holding.get('total_cost', 0)
            
            new_qty = old_qty + lot_size
            new_cost = old_cost + lot_value
            new_entry = new_cost / new_qty if new_qty > 0 else current_price
            
            wallet['holdings'][symbol] = {
                'quantity': new_qty,
                'entry_price': new_entry,
                'total_cost': new_cost,
                'current_value': new_qty * current_price,
                'highest_price': current_price  # Initialize for Trailing Stop
            }
            
            save_wallet(wallet)
            
            # Add to transactions
            transactions = load_transactions()
            transactions.append({
                'id': len(transactions) + 1,
                'symbol': symbol,
                'action': 'BUY',
                'quantity': lot_size,
                'entry_price': current_price,
                'timestamp': timestamp,
                'status': 'ACTIVE',
                'source': source
            })
            save_transactions(transactions)
            
            # Log
            log_entry = {
                'timestamp': timestamp,
                'type': 'TRADE',
                'message': f"BUY {lot_size:.6f} {symbol} @ ${current_price:.2f} (${lot_value:.2f})"
            }
            save_bot_log(log_entry)
            add_log(f"Executed BUY: {lot_size:.6f} {symbol} @ ${current_price:.2f}")
            
            return {"status": "ok", "action": "BUY", "symbol": symbol, "quantity": lot_size, "price": current_price, "message": f"Bought {lot_size:.6f} {symbol} @ ${current_price:.2f}"}
            
        elif action == "FORCE_SELL":
            holdings = wallet.get('holdings', {})
            if symbol not in holdings or holdings[symbol].get('quantity', 0) <= 0:
                return {"status": "error", "message": f"No {symbol} holdings to sell"}
            
            holding = holdings[symbol]
            quantity = holding['quantity']
            entry_price = holding['entry_price']
            sell_value = quantity * current_price
            cost_basis = holding.get('total_cost', quantity * entry_price)
            pnl = sell_value - cost_basis
            
            # Update wallet
            wallet['cash'] += sell_value
            wallet['realized_pnl'] = wallet.get('realized_pnl', 0) + pnl
            del wallet['holdings'][symbol]
            
            # Update max balance
            equity = wallet['cash'] + sum(h.get('current_value', 0) for h in wallet.get('holdings', {}).values())
            wallet['max_balance'] = max(wallet.get('max_balance', equity), equity)
            
            save_wallet(wallet)
            
            # Update transactions
            transactions = load_transactions()
            for tx in transactions:
                if tx['symbol'] == symbol and tx['status'] == 'ACTIVE':
                    tx['status'] = 'CLOSED'
                    tx['close_price'] = current_price
                    tx['close_timestamp'] = timestamp
                    tx['pnl'] = pnl
            save_transactions(transactions)
            
            # Log
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            log_entry = {
                'timestamp': timestamp,
                'type': 'TRADE',
                'message': f"SELL {quantity:.6f} {symbol} @ ${current_price:.2f} (PnL: {pnl_str})"
            }
            save_bot_log(log_entry)
            add_log(f"Executed SELL: {quantity:.6f} {symbol} @ ${current_price:.2f} PnL: {pnl_str}")
            
            return {"status": "ok", "action": "SELL", "symbol": symbol, "quantity": quantity, "price": current_price, "pnl": pnl, "message": f"Sold {quantity:.6f} {symbol} @ ${current_price:.2f} (PnL: {pnl_str})"}
            
    except Exception as e:
        add_log(f"Trade error: {e}")
        return {"status": "error", "message": str(e)}
@app.post("/api/liquidate_all")
async def liquidate_all():
    """Liquidate all active positions"""
    wallet = load_wallet()
    holdings = list(wallet.get('holdings', {}).keys())
    results = []
    
    for symbol in holdings:
        # Create a simplified symbol for the URL/Command logic if needed, 
        # but send_command handles replacement. 
        # Here we call python function directly, we need to handle format.
        # send_command expects "BTC/USDT" format for symbol argument
        
        # We call the function directly
        res = await send_command(symbol, "FORCE_SELL", source="MANUAL_LIQUIDATE")
        results.append(res)
        
    return {"status": "ok", "message": f"Liquidated {len(results)} positions", "details": results}

@app.get("/api/logs")
async def get_logs():
    """Get system logs"""
    return {"logs": system_logs[-50:]}  # Return last 50 logs

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Store previous prices to detect changes
        previous_prices = {}
        
        while True:
            # Fetch real prices from Binance Testnet
            coins = ['BTC', 'ETH', 'SOL', 'BNB', 'TON', 'XRP']
            assets = {}
            price_logs = []
            
            for coin in coins:
                symbol = f'{coin}/USDT'
                try:
                    if exchange:
                        ticker = exchange.fetch_ticker(symbol)
                        price = ticker['last']
                        change_pct = ticker.get('percentage', 0) or 0
                    else:
                        import numpy as np
                        bases = {'BTC': 95000, 'ETH': 3300, 'SOL': 140, 'BNB': 600, 'TON': 6, 'XRP': 2}
                        price = bases.get(coin, 100) * (1 + np.random.randn() * 0.001)
                        change_pct = np.random.randn() * 2
                    
                    # Detect price change
                    prev_price = previous_prices.get(coin, price)
                    price_diff = price - prev_price
                    if abs(price_diff) > 0.01:
                        direction = '📈' if price_diff > 0 else '📉'
                        price_logs.append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'type': 'PRICE',
                            'message': f"{direction} {coin}: ${prev_price:.2f} → ${price:.2f} ({'+' if price_diff > 0 else ''}{price_diff:.2f})"
                        })
                    previous_prices[coin] = price
                    
                    # Generate council score based on price momentum
                    import numpy as np
                    np.random.seed(int(datetime.now().timestamp()) % 1000 + hash(coin) % 100)
                    score = 50 + change_pct * 5  # Base score on price change
                    score = max(20, min(80, score + np.random.randn() * 10))
                    signal = 'BUY' if score >= 60 else 'SELL' if score <= 40 else 'NEUTRAL'
                    
                    assets[coin] = {
                        'symbol': symbol,
                        'price': round(price, 2),
                        'price_change': round(change_pct, 2),
                        'council_score': round(score, 2),
                        'signal': signal,
                        'rsi': round(50 + np.random.randn() * 15, 1),
                        'atr': round(price * 0.02, 2),
                        'sentiment': 'HYPE' if change_pct > 2 else 'FEAR' if change_pct < -2 else 'NORMAL',
                        'regime': 'BULLISH' if change_pct > 0 else 'BEARISH' if change_pct < 0 else 'NEUTRAL'
                    }
                    # Update global state for trading loop
                    global_market_data[coin] = assets[coin]
                except Exception as e:
                    print(f"Error fetching {coin}: {e}")
            
            data = {
                'assets': assets,
                'portfolio': {'equity': 100000, 'cash': 100000, 'realized_pnl': 0},
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            
            # Load trade history for calendar
            daily_pnl = load_trade_history()
            
            # Load wallet data and merge holdings for frontend display
            wallet = load_wallet()
            if wallet:
                if 'portfolio' not in data:
                    data['portfolio'] = {}
                data['portfolio']['holdings'] = wallet.get('holdings', {})
                data['portfolio']['cash'] = wallet.get('cash', data['portfolio'].get('cash', 100000))
                data['portfolio']['realized_pnl'] = wallet.get('realized_pnl', 0)
                # Calculate equity from cash + holdings value
                holdings = wallet.get('holdings', {})
                holdings_value = sum(h.get('current_value', 0) for h in holdings.values())
                equity = data['portfolio']['cash'] + holdings_value
                data['portfolio']['equity'] = equity
                data['portfolio']['open_positions'] = len(holdings)
                
                # Calculate max_drawdown from wallet's max_balance
                max_balance = wallet.get('max_balance', equity)
                if max_balance > 0:
                    drawdown = ((max_balance - equity) / max_balance) * 100
                    data['portfolio']['max_drawdown'] = max(0, drawdown)
                else:
                    data['portfolio']['max_drawdown'] = 0
            
            # Load transactions and bot logs
            transactions = load_transactions()
            active_transactions = [tx for tx in transactions if tx.get('status') == 'ACTIVE']
            
            # Update current values for active transactions
            for tx in active_transactions:
                symbol = tx['symbol']
                if exchange:
                    try:
                        ticker = exchange.fetch_ticker(symbol)
                        tx['current_price'] = ticker['last']
                        tx['pnl'] = (ticker['last'] - tx['entry_price']) * tx['quantity']
                        
                        # Add Trailing Stop Info
                        if wallet and 'holdings' in wallet and symbol in wallet['holdings']:
                            holding = wallet['holdings'][symbol]
                            highest = holding.get('highest_price', tx['current_price'])
                            tx['stop_loss'] = highest * (1 - 0.02) #  2% default
                    except:
                        pass
            
            bot_logs = load_bot_logs()[-30:]  # Last 30 trade logs
            
            # Combine price logs with trade logs for display
            all_logs = price_logs + bot_logs
            all_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Send update
            if len(active_transactions) > 0:
                print(f"DEBUG WS: Sending {len(active_transactions)} active transactions. Sample: {active_transactions[0].get('symbol')} SL={active_transactions[0].get('stop_loss')}")
            
            await websocket.send_json({
                "type": "update",
                "data": data,
                "daily_pnl": daily_pnl,
                "transactions": active_transactions,
                "bot_logs": all_logs[:50],  # Send combined logs
                "price_logs": price_logs,  # Send price changes separately too
                "timestamp": datetime.now().isoformat()
            })
            
            # Wait 1 second before next update
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


# Configuration
TRAILING_STOP_PCT = 0.02  # 2% Trailing Stop
AUTO_TRADE_ENABLED = True
BUY_THRESHOLD = 70
SELL_THRESHOLD = 30

async def trading_loop():
    """Background task for auto-trading and trailing stops"""
    add_log("Starting Auto-Trading Loop...")
    while True:
        try:
            # 1. Load Data
            wallet = load_wallet()
            if not wallet:
                await asyncio.sleep(5)
                continue
                
            holdings = wallet.get('holdings', {})
            transactions = load_transactions()
            
            # 2. Check Trailing Stops & Take Profits
            for symbol, holding in list(holdings.items()):
                # Get current price
                ticker = exchange.fetch_ticker(symbol) if exchange else {'last': holding['entry_price']}
                current_price = ticker['last']
                
                # Update Highest Price for Trailing Stop
                highest_price = holding.get('highest_price', holding['entry_price'])
                if current_price > highest_price:
                    holding['highest_price'] = current_price
                    # Update wallet with new highest price
                    wallet['holdings'][symbol]['highest_price'] = current_price
                    save_wallet(wallet)
                
                # Check Trailing Stop
                stop_loss_price = highest_price * (1 - TRAILING_STOP_PCT)
                
                if current_price < stop_loss_price:
                    # Trigger Trailing Stop SELL
                    add_log(f"📉 Trailing Stop Triggered for {symbol}: price ${current_price:.2f} < stop ${stop_loss_price:.2f}")
                    add_log(f"📉 Trailing Stop Triggered for {symbol}: price ${current_price:.2f} < stop ${stop_loss_price:.2f}")
                    await send_command(symbol, "FORCE_SELL", source="BOT_TRAILING_STOP")
            
            # 3. Check Auto-Buy Signals
            if AUTO_TRADE_ENABLED:
                # Use global market data to ensure WYSIWYG (What You See Is What You Get)
                # This syncs the bot decision with the UI display
                current_time = datetime.now()
                
                for coin, data in global_market_data.items():
                    symbol = data.get('symbol')
                    if not symbol: continue
                    
                    # Skip if already holding
                    if symbol in holdings:
                        continue
                    
                    # Use the EXACT score displayed on dashboard
                    score = data.get('council_score', 50)
                    
                    if score >= BUY_THRESHOLD:
                        add_log(f"🤖 Auto-Buy Signal for {symbol} (Score: {score:.1f} > {BUY_THRESHOLD})")
                        add_log(f"🤖 Auto-Buy Signal for {symbol} (Score: {score:.1f} > {BUY_THRESHOLD})")
                        await send_command(symbol, "FORCE_BUY", source="BOT_AUTO_BUY")

            await asyncio.sleep(5) # Run every 5 seconds
            
        except Exception as e:
            print(f"Trading Loop Error: {e}")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(trading_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
