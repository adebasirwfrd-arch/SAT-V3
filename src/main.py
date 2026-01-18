import time
import pandas as pd
import numpy as np
from datetime import datetime
import ccxt
import os
import sys
import json

# Setup Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.council.chairman import TheChairman
from src.utils.risk_manager import RiskManager
from src.utils.state_manager import StateManager
from config.settings import Config

class SATV3_MultiEngine:
    def __init__(self):
        print(f"🚀 INITIALIZING SAT-V3 MULTI-CRYPTO ENGINE...")
        print(f"📊 Trading {len(Config.TRADING_PAIRS)} pairs: {', '.join([p.split('/')[0] for p in Config.TRADING_PAIRS])}")
        
        self.brain = StateManager()
        self.chairman = TheChairman()
        self.risk_manager = RiskManager()
        
        # Asset data for dashboard
        self.assets_data = {'timestamp': '', 'assets': {}, 'portfolio': {}}
        
        # Connect to Binance
        try:
            self.exchange = ccxt.binance({
                'apiKey': Config.API_KEY or 'test',
                'secret': Config.SECRET_KEY or 'test',
                'options': {'defaultType': 'spot', 'adjustForTimeDifference': True},
                'urls': {
                    'api': {
                        'public': 'https://testnet.binance.vision/api/v3',
                        'private': 'https://testnet.binance.vision/api/v3',
                    }
                },
                'timeout': 10000,
                'enableRateLimit': True
            })
            if Config.SANDBOX:
                self.exchange.set_sandbox_mode(True)
                print("⚠️ BINANCE TESTNET MODE")
            
            self.exchange.load_markets()
            print("✅ Connected to Binance Network")
        except Exception as e:
            print(f"❌ Binance Connection Failed: {e}")
            self.exchange = None

    def get_market_data(self, symbol):
        """Fetch OHLCV data for a symbol"""
        try:
            if self.exchange:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=Config.TIMEFRAME, limit=300)
                if ohlcv and len(ohlcv) >= 200:
                    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                    df['time'] = pd.to_datetime(df['time'], unit='ms')
                    return df
        except Exception as e:
            print(f"⚠️ {symbol} Data Error: {e}")
        
        # Fallback: Simulation data
        dates = pd.date_range(end=datetime.now(), periods=300, freq='1h')
        df = pd.DataFrame({'time': dates})
        base = {'BTC/USDT': 50000, 'ETH/USDT': 3200, 'SOL/USDT': 180, 
                'BNB/USDT': 600, 'TON/USDT': 6.5, 'XRP/USDT': 0.55}.get(symbol, 100)
        noise = np.random.normal(0, base*0.01, 300).cumsum()
        df['close'] = base + noise
        df['open'] = df['close'].shift(1).fillna(base)
        df['high'] = df[['open', 'close']].max(axis=1) * 1.005
        df['low'] = df[['open', 'close']].min(axis=1) * 0.995
        df['volume'] = np.random.randint(100, 1000, 300)
        return df

    def execute_order(self, symbol, side, quantity, price):
        """Execute order (Testnet or simulated)"""
        try:
            if self.exchange and not Config.SANDBOX:
                if side == 'buy':
                    order = self.exchange.create_market_buy_order(symbol, quantity)
                else:
                    order = self.exchange.create_market_sell_order(symbol, quantity)
                return order
        except Exception as e:
            print(f"❌ Order Error: {e}")
        
        # Simulated order
        return {
            'id': f"SIM-{int(time.time())}",
            'side': side,
            'amount': quantity,
            'price': price,
            'average': price
        }

    def check_commands(self):
        """Check for manual commands from dashboard"""
        if not os.path.exists(Config.COMMANDS_FILE):
            return
        try:
            with open(Config.COMMANDS_FILE, 'r') as f:
                cmd = json.load(f)
            
            if cmd.get('executed'):
                return
            
            action = cmd.get('command')
            symbol = cmd.get('symbol', 'BTC/USDT')
            
            if action == 'FORCE_BUY' and symbol:
                print(f"🚀 FORCE BUY: {symbol}")
                # Get current price
                coin = symbol.split('/')[0]
                price = self.assets_data['assets'].get(coin, {}).get('price', 0)
                
                if price > 0:
                    # Calculate quantity (Max Invest or fixed)
                    cash = self.brain.get_cash()
                    max_invest = cash * Config.MAX_POSITION_SIZE
                    
                    if max_invest > 10:
                        qty = max_invest / price
                        
                        # Execute
                        order = self.execute_order(symbol, 'buy', qty, price)
                        
                        # Calculate mockup stops if not provided
                        atr = self.assets_data['assets'].get(coin, {}).get('atr', price * 0.02)
                        stop_loss = price - (2 * atr)
                        take_profit = price + (4 * atr)
                        
                        self.brain.update_position(symbol, {
                            'quantity': qty,
                            'entry_price': price,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'order_id': order.get('id', 'MANUAL')
                        })
                        print(f"✅ MANUAL BUY EXECUTED: {qty:.4f} {coin} @ ${price}")
                    else:
                        print(f"❌ INSUFFICIENT CASH: ${cash}")
                
            elif action == 'FORCE_SELL' and symbol:
                print(f"🔴 FORCE SELL: {symbol}")
                if symbol in self.brain.state.get('holdings', {}):
                    price = self.assets_data['assets'].get(symbol.split('/')[0], {}).get('price', 0)
                    self.brain.close_position(symbol, price)
            
            elif action == 'LIQUIDATE_ALL':
                print("🛑 LIQUIDATE ALL POSITIONS!")
                for sym in list(self.brain.state.get('holdings', {}).keys()):
                    coin = sym.split('/')[0]
                    price = self.assets_data['assets'].get(coin, {}).get('price', 0)
                    if price > 0:
                        self.brain.close_position(sym, price)
            
            # Mark as executed
            cmd['executed'] = True
            with open(Config.COMMANDS_FILE, 'w') as f:
                json.dump(cmd, f)
                
        except Exception as e:
            pass

    def analyze_asset(self, symbol):
        """Analyze a single asset with The Council"""
        coin = symbol.split('/')[0]
        df = self.get_market_data(symbol)
        
        if df is None or len(df) < 200:
            return None
        
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        price_change = current_price - prev_price
        
        # Run Council Voting (7 Generals + Sentiment)
        verdict = self.chairman.solicit_votes(df)
        
        # Calculate indicators for display
        atr = self.risk_manager.calculate_atr(df)
        
        # Simple RSI calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_value = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
        
        return {
            'symbol': symbol,
            'coin': coin,
            'price': float(current_price),
            'price_change': float(price_change),
            'rsi': rsi_value,
            'atr': float(atr),
            'council_score': float(verdict['final_score']),
            'signal': verdict['final_signal'],
            'sentiment': verdict.get('sentiment', {}).get('mode', 'NORMAL'),
            'regime': 'BULLISH' if verdict['final_score'] >= 50 else 'BEARISH'
        }

    def manage_positions(self, asset_data):
        """Manage existing positions with trailing stop"""
        symbol = asset_data['symbol']
        current_price = asset_data['price']
        atr = asset_data['atr']
        
        holdings = self.brain.state.get('holdings', {})
        if symbol not in holdings:
            return
        
        pos = holdings[symbol]
        entry_price = pos['entry_price']
        current_sl = pos.get('stop_loss', entry_price * 0.95)
        phase = pos.get('trailing_phase', 1)
        
        # Trailing Stop Logic
        if phase == 1 and current_price > (entry_price + 1.5 * atr):
            pos['stop_loss'] = entry_price * 1.001
            pos['trailing_phase'] = 2
            print(f"🛡️ {symbol}: Phase 2 (Break Even)")
        elif phase >= 2:
            proposed_sl = current_price - (3 * atr)
            if proposed_sl > current_sl:
                pos['stop_loss'] = proposed_sl
                pos['trailing_phase'] = 3
        
        # Check exit conditions
        if current_price <= pos.get('stop_loss', 0):
            print(f"🛑 {symbol}: STOP LOSS HIT!")
            self.brain.close_position(symbol, current_price)
        elif current_price >= pos.get('take_profit', float('inf')):
            print(f"💰 {symbol}: TAKE PROFIT HIT!")
            self.brain.close_position(symbol, current_price)

    def run_cycle(self):
        print(f"\n{'='*60}")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | SCANNING {len(Config.TRADING_PAIRS)} ASSETS...")
        
        self.assets_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'assets': {},
            'portfolio': {}
        }
        
        prices = {}
        
        for symbol in Config.TRADING_PAIRS:
            data = self.analyze_asset(symbol)
            if not data:
                continue
            
            coin = data['coin']
            self.assets_data['assets'][coin] = data
            prices[symbol] = data['price']
            
            # Log
            signal_icon = "🟢" if "BUY" in data['signal'] else "🔴" if "SELL" in data['signal'] else "🟡"
            print(f"  {coin}: ${data['price']:,.2f} | Score: {data['council_score']:.0f} | {signal_icon} {data['signal']}")
            
            # Manage existing position
            self.manage_positions(data)
            
            # Check for new entry
            holdings = self.brain.state.get('holdings', {})
            if symbol not in holdings and "BUY" in data['signal']:
                cash = self.brain.get_cash()
                max_invest = cash * Config.MAX_POSITION_SIZE
                
                if max_invest > 10:  # Minimum $10
                    plan = self.risk_manager.calculate_entry_params(cash, data['price'], data['atr'])
                    qty = min(plan['quantity'], max_invest / data['price'])
                    
                    print(f"  ⚡ BUY SIGNAL: {coin}!")
                    
                    order = self.execute_order(symbol, 'buy', qty, data['price'])
                    if order:
                        self.brain.update_position(symbol, {
                            'quantity': qty,
                            'entry_price': data['price'],
                            'stop_loss': plan['stop_loss'],
                            'take_profit': plan['take_profit'],
                            'order_id': order.get('id', 'SIM')
                        })
        
        # Check manual commands AFTER assets_data is populated
        self.check_commands()
        
        # Update prices and save
        self.brain.update_prices(prices)
        
        # Portfolio metrics
        equity = self.brain.get_equity()
        cash = self.brain.get_cash()
        pnl = self.brain.state['portfolio']['realized_pnl']
        max_bal = self.brain.state['portfolio']['max_balance']
        dd = ((max_bal - equity) / max_bal * 100) if max_bal > 0 else 0
        
        self.assets_data['portfolio'] = {
            'cash': cash,
            'equity': equity,
            'realized_pnl': pnl,
            'max_drawdown': dd,
            'holdings': self.brain.state.get('holdings', {}),
            'open_positions': len(self.brain.state.get('holdings', {}))
        }
        
        # Save for dashboard
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        with open(Config.LIVE_DATA_FILE, 'w') as f:
            json.dump(self.assets_data, f, indent=2)
        
        print(f"💰 Equity: ${equity:,.2f} | Cash: ${cash:,.2f} | PnL: ${pnl:,.2f}")

if __name__ == "__main__":
    bot = SATV3_MultiEngine()
    
    print(f"\n{'='*60}")
    print("🤖 SAT-V3 MULTI-CRYPTO BOT STARTED")
    print(f"💰 Initial Capital: ${Config.INITIAL_CAPITAL:,.2f}")
    print(f"📊 Trading: {', '.join([p.split('/')[0] for p in Config.TRADING_PAIRS])}")
    print("Press Ctrl+C to stop")
    print(f"{'='*60}")
    
    try:
        while True:
            bot.run_cycle()
            time.sleep(5)  # 5 second cycles for faster updates
    except KeyboardInterrupt:
        print("\n🛑 SHUTDOWN.")
        print(f"💰 Final Equity: ${bot.brain.get_equity():,.2f}")
