import json
import os
from datetime import datetime

class StateManager:
    def __init__(self, file_path='data/memory.json'):
        self.file_path = file_path
        self.wallet_path = 'data/wallet.json'
        
        # Default State
        self.default_state = {
            "status": "IDLE",
            "last_update": "",
            "portfolio": {
                "cash": 10000.0,
                "equity": 10000.0,
                "realized_pnl": 0.0,
                "max_balance": 10000.0
            },
            "positions": {},
            "holdings": {},
            "daily_stats": {
                "trades_today": 0,
                "pnl_today": 0.0
            }
        }
        self.state = self.load_state()
        self._ensure_structure()

    def _ensure_structure(self):
        """Ensure all required keys exist"""
        if 'portfolio' not in self.state:
            self.state['portfolio'] = self.default_state['portfolio'].copy()
        if 'holdings' not in self.state:
            self.state['holdings'] = {}
        if 'positions' not in self.state:
            self.state['positions'] = {}
        if 'daily_stats' not in self.state:
            self.state['daily_stats'] = self.default_state['daily_stats'].copy()
        
        # Ensure portfolio has all keys
        for key in self.default_state['portfolio']:
            if key not in self.state['portfolio']:
                self.state['portfolio'][key] = self.default_state['portfolio'][key]

    def load_state(self):
        # Try wallet file first
        if os.path.exists(self.wallet_path):
            try:
                with open(self.wallet_path, 'r') as f:
                    wallet = json.load(f)
                    state = self.default_state.copy()
                    state['portfolio'] = state['portfolio'].copy()
                    state['portfolio']['cash'] = wallet.get('cash', 10000)
                    state['holdings'] = wallet.get('holdings', {})
                    state['portfolio']['realized_pnl'] = wallet.get('realized_pnl', 0)
                    state['portfolio']['max_balance'] = wallet.get('max_balance', 10000)
                    return state
            except:
                pass
        
        if not os.path.exists(self.file_path):
            print("💾 Memory file not found. Creating new brain...")
            return self.save_state(self.default_state.copy())
        
        try:
            with open(self.file_path, 'r') as f:
                loaded = json.load(f)
                # Merge with defaults
                state = self.default_state.copy()
                state.update(loaded)
                return state
        except:
            print("⚠️ Memory corrupted! Resetting brain...")
            return self.save_state(self.default_state.copy())

    def save_state(self, new_state=None):
        if new_state:
            self.state = new_state
        
        self._ensure_structure()
        self.state['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        os.makedirs(os.path.dirname(self.file_path) if os.path.dirname(self.file_path) else '.', exist_ok=True)
        
        with open(self.file_path, 'w') as f:
            json.dump(self.state, f, indent=4)
        
        return self.state

    def save_wallet(self):
        """Save persistent wallet data"""
        self._ensure_structure()
        os.makedirs(os.path.dirname(self.wallet_path) if os.path.dirname(self.wallet_path) else '.', exist_ok=True)
        wallet = {
            "cash": self.state['portfolio']['cash'],
            "holdings": self.state.get('holdings', {}),
            "realized_pnl": self.state['portfolio']['realized_pnl'],
            "max_balance": self.state['portfolio']['max_balance']
        }
        with open(self.wallet_path, 'w') as f:
            json.dump(wallet, f, indent=4)

    def get_cash(self):
        self._ensure_structure()
        return self.state['portfolio']['cash']

    def get_equity(self):
        self._ensure_structure()
        holdings_value = sum(h.get('current_value', 0) for h in self.state.get('holdings', {}).values())
        return self.state['portfolio']['cash'] + holdings_value

    def update_position(self, symbol, entry_data):
        """Add or update a position for a symbol"""
        self._ensure_structure()
        
        self.state['holdings'][symbol] = {
            "qty": entry_data['quantity'],
            "entry_price": entry_data['entry_price'],
            "current_price": entry_data['entry_price'],
            "current_value": entry_data['quantity'] * entry_data['entry_price'],
            "stop_loss": entry_data['stop_loss'],
            "take_profit": entry_data['take_profit'],
            "trailing_phase": 1,
            "order_id": entry_data.get('order_id', 'SIMULATED')
        }
        
        cost = entry_data['quantity'] * entry_data['entry_price']
        self.state['portfolio']['cash'] -= cost
        self.state['status'] = "IN_POSITION"
        
        self.save_state()
        self.save_wallet()
        print(f"💾 Position opened: {symbol}")

    def close_position(self, symbol, sell_price):
        """Close a position and realize PnL"""
        self._ensure_structure()
        
        if symbol not in self.state.get('holdings', {}):
            return 0
        
        pos = self.state['holdings'][symbol]
        sell_value = pos['qty'] * sell_price
        pnl = sell_value - (pos['qty'] * pos['entry_price'])
        
        self.state['portfolio']['cash'] += sell_value
        self.state['portfolio']['realized_pnl'] += pnl
        self.state['daily_stats']['pnl_today'] += pnl
        self.state['daily_stats']['trades_today'] += 1
        
        equity = self.get_equity()
        if equity > self.state['portfolio']['max_balance']:
            self.state['portfolio']['max_balance'] = equity
        
        # Log trade to history for calendar
        self._log_trade(symbol, pnl, pos['entry_price'], sell_price, pos['qty'])
        
        del self.state['holdings'][symbol]
        
        if not self.state['holdings']:
            self.state['status'] = "IDLE"
        
        self.save_state()
        self.save_wallet()
        print(f"💾 Position closed: {symbol}, PnL: ${pnl:.2f}")
        return pnl
    
    def _log_trade(self, symbol, pnl, entry_price, exit_price, qty):
        """Log trade to trade_history.json for calendar display"""
        history_path = 'data/trade_history.json'
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    history = json.load(f)
            else:
                history = {"trades": [], "daily_summary": {}}
            
            # Add trade record
            trade = {
                "date": today,
                "time": datetime.now().strftime('%H:%M:%S'),
                "symbol": symbol,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "qty": qty,
                "pnl": pnl,
                "type": "WIN" if pnl > 0 else "LOSS"
            }
            history["trades"].append(trade)
            
            # Update daily summary
            if today not in history["daily_summary"]:
                history["daily_summary"][today] = {"pnl": 0, "trades": [], "wins": 0, "losses": 0}
            
            history["daily_summary"][today]["pnl"] += pnl
            history["daily_summary"][today]["trades"].append({
                "symbol": symbol.split('/')[0],
                "pnl": pnl
            })
            if pnl > 0:
                history["daily_summary"][today]["wins"] += 1
            else:
                history["daily_summary"][today]["losses"] += 1
            
            with open(history_path, 'w') as f:
                json.dump(history, f, indent=2)
                
            print(f"📊 Trade logged: {symbol} {'✅' if pnl > 0 else '❌'} ${pnl:.2f}")
        except Exception as e:
            print(f"⚠️ Trade logging error: {e}")

    def update_prices(self, prices_dict):
        """Update current prices for all holdings"""
        self._ensure_structure()
        
        for symbol, price in prices_dict.items():
            if symbol in self.state.get('holdings', {}):
                self.state['holdings'][symbol]['current_price'] = price
                self.state['holdings'][symbol]['current_value'] = self.state['holdings'][symbol]['qty'] * price
        
        self.state['portfolio']['equity'] = self.get_equity()
        self.save_state()
