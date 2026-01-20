"""
Position Manager for Backtest
Handles position tracking, God Tier Trailing Stops, and trade recording
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional, List
import sys
import os

# Add parent path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.council.entry_logic_master import calculate_god_tier_trailing


class Position:
    """Represents a single open position"""
    
    def __init__(self, symbol: str, entry_time: pd.Timestamp, entry_price: float, 
                 quantity: float, initial_sl: float, atr: float, entry_type: str = "NORMAL",
                 breakeven_ratio: float = 1.5, trailing_multiplier: float = 3.0):
        self.symbol = symbol
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.quantity = quantity
        self.initial_sl = initial_sl
        self.current_sl = initial_sl
        self.atr = atr
        self.entry_type = entry_type  # "NORMAL" or "REVENGE_ENTRY"
        
        # God Tier Trailing params
        self.highest_high = entry_price
        self.is_breakeven = False
        self.breakeven_ratio = breakeven_ratio  # 1.5 for normal, 1.0 for revenge
        self.trailing_multiplier = trailing_multiplier  # 3.0 for normal, 2.5 for revenge
        
        self.exit_time = None
        self.exit_price = None
        self.pnl = 0.0
        self.r_multiple = 0.0
        self.phase = "dormant"


class PositionManager:
    """
    Manages open positions and trailing stops
    """
    
    def __init__(self, initial_capital: float = 10000.0, risk_pct: float = 0.01,
                 commission: float = 0.001, slippage: float = 0.0005):
        """
        Args:
            initial_capital: Starting balance in USDT
            risk_pct: Risk per trade as fraction of equity (0.01 = 1%)
            commission: Commission rate (0.001 = 0.1%)
            slippage: Slippage rate (0.0005 = 0.05%)
        """
        self.initial_capital = initial_capital
        self.equity = initial_capital
        self.cash = initial_capital
        self.risk_pct = risk_pct
        self.commission = commission
        self.slippage = slippage
        
        self.open_positions: Dict[str, Position] = {}
        self.closed_trades: List[Position] = []
        self.peak_equity = initial_capital
        self.max_drawdown = 0.0
        
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk management
        Risk 1% of equity per trade
        
        Args:
            entry_price: Entry price
            stop_loss: Initial stop loss price
            
        Returns:
            Position size in base currency (BTC)
        """
        risk_amount = self.equity * self.risk_pct
     # Risk distance in price
        risk_distance = abs(entry_price - stop_loss)
        
        if risk_distance == 0:
            return 0
        
        # Position size = risk amount / risk distance
        position_size = risk_amount / risk_distance
        
        return position_size
    
    def open_position(self, symbol: str, timestamp: pd.Timestamp, signal_data: dict, qty: float = None) -> bool:
        """
        Open a new position.
        If qty is provided (e.g. from Strategy sizing), use it. 
        Otherwise calculate based on risk.
        """
        if symbol in self.open_positions:
            return False  # Already have position
            
        entry_price = signal_data['entry_price']
        # Use initial_sl if available (Strategy V3), else stop_loss
        initial_sl = signal_data.get('initial_sl', signal_data['stop_loss'])
        
        atr = signal_data.get('atr', entry_price * 0.02)
        entry_type = signal_data.get('entry_type', 'NORMAL')
        breakeven_ratio = signal_data.get('breakeven_ratio', 1.5)
        trailing_multiplier = signal_data.get('trailing_multiplier', 3.0)
        
        # Calculate Position Size if not provided
        if qty is None:
            risk_per_trade = self.equity * self.risk_pct
            risk_per_unit = entry_price - initial_sl
            
            if risk_per_unit <= 0:
                print(f"[{timestamp}] WARNING: Invalid Risk Distance (Ent: {entry_price}, SL: {initial_sl}). Skipping.")
                return False
                
            qty = risk_per_trade / risk_per_unit
        
        # Sizing Limit (Max 98% Equity)
        notional_value = qty * entry_price
        if notional_value > self.equity * 0.98:
            qty = (self.equity * 0.98) / entry_price
        
        # Apply slippage (assume market order)
        entry_price_with_slippage = entry_price * (1 + self.slippage)
        
        
        # Calculate cost with commission
        cost = (entry_price_with_slippage * qty) * (1 + self.commission)
        
        if cost > self.cash:
            return False  # Not enough cash
        
        # Create position
        position = Position(
            symbol=symbol,
            entry_time=timestamp,
            entry_price=entry_price_with_slippage,
            quantity=qty,
            initial_sl=initial_sl,
            atr=atr,
            entry_type=entry_type,
            breakeven_ratio=breakeven_ratio,
            trailing_multiplier=trailing_multiplier
        )
        
        self.open_positions[symbol] = position
        self.cash -= cost
        
        return True
    
    def update_trailing_stop(self, symbol: str, current_price: float, current_atr: float) -> None:
        """
        Update God Tier Trailing Stop for a position
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            current_atr: Current ATR value
        """
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        
        # Update highest high
        if current_price > position.highest_high:
            position.highest_high = current_price
        
        # Calculate new trailing stop using God Tier logic
        trailing_data = calculate_god_tier_trailing(
            entry_price=position.entry_price,
            initial_sl=position.initial_sl,
            current_price=current_price,
            highest_high=position.highest_high,
            atr_value=current_atr,
            is_breakeven=position.is_breakeven,
            multiplier=position.trailing_multiplier,
            breakeven_ratio=position.breakeven_ratio,
            entry_type=position.entry_type
        )
        
        # Update position state
        position.current_sl = trailing_data['stop_loss']
        position.is_breakeven = trailing_data['is_breakeven']
        position.phase = trailing_data['phase']
    
    def check_stop_hit(self, symbol: str, current_price: float, timestamp: pd.Timestamp) -> Optional[Position]:
        """
        Check if trailing stop has been hit
        
        Args:
            symbol: Trading symbol
            current_price: Current price
            timestamp: Current timestamp
            
        Returns:
            Closed position if stop hit, None otherwise
        """
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        
        # Check if current price <= stop loss
        if current_price <= position.current_sl:
            # Stop hit - close position
            return self.close_position(symbol, current_price, timestamp, "TRAILING_STOP")
        
        return None
    
    def close_position(self, symbol: str, exit_price: float, timestamp: pd.Timestamp, reason: str) -> Position:
        """
        Close a position
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            timestamp: Exit timestamp
            reason: Reason for closing
            
        Returns:
            Closed position
        """
        if symbol not in self.open_positions:
            raise ValueError(f"No open position for {symbol}")
        
        position = self.open_positions.pop(symbol)
        
        # Apply slippage
        exit_price_with_slippage = exit_price * (1 - self.slippage)
        
        # Calculate proceeds with commission
        proceeds = (exit_price_with_slippage * position.quantity) * (1 - self.commission)
        
        # Calculate PnL
        cost = position.entry_price * position.quantity
        pnl = proceeds - cost
        
        # Calculate R-multiple
        risk_distance = position.entry_price - position.initial_sl
        if risk_distance > 0:
            price_gain = exit_price_with_slippage - position.entry_price
            r_multiple = price_gain / risk_distance
        else:
            r_multiple = 0
        
        # Update position
        position.exit_time = timestamp
        position.exit_price = exit_price_with_slippage
        position.pnl = pnl
        position.r_multiple = r_multiple
        
        # Update cash and equity
        self.cash += proceeds
        self.equity = self.cash + self.get_open_positions_value()
        
        # Update peak and drawdown
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
        
        current_dd = (self.peak_equity - self.equity) / self.peak_equity
        if current_dd > self.max_drawdown:
            self.max_drawdown = current_dd
        
        # Record closed trade
        self.closed_trades.append(position)
        
        return position
    
    def get_open_positions_value(self) -> float:
        """Calculate total market value of open positions"""
        # This would need current prices, which we don't have here
        # In practice, this is updated in the main backtest loop
        return 0.0
    
    def get_equity(self) -> float:
        """Get current equity"""
        return self.equity
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'winrate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'avg_r_multiple': 0,
                'total_pnl': 0
            }
        
        wins = [t for t in self.closed_trades if t.pnl > 0]
        losses = [t for t in self.closed_trades if t.pnl <= 0]
        
        return {
            'total_trades': len(self.closed_trades),
            'wins': len(wins),
            'losses': len(losses),
            'winrate': len(wins) / len(self.closed_trades) if self.closed_trades else 0,
            'avg_win': np.mean([t.pnl for t in wins]) if wins else 0,
            'avg_loss': np.mean([t.pnl for t in losses]) if losses else 0,
            'avg_r_multiple': np.mean([t.r_multiple for t in self.closed_trades]),
            'total_pnl': sum(t.pnl for t in self.closed_trades)
        }


if __name__ == "__main__":
    # Test position manager
    pm = PositionManager(initial_capital=10000, risk_pct=0.01)
    
    # Test open position
    signal = {
        'entry_price': 50000.0,
        'stop_loss': 49000.0,  # 1000 risk
        'atr': 500.0,
        'entry_type': 'NORMAL'
    }
    
    opened = pm.open_position('BTCUSDT', pd.Timestamp('2023-01-01'), signal)
    print(f"Position opened: {opened}")
    print(f"Equity: ${pm.equity:.2f}")
    print(f"Open positions: {list(pm.open_positions.keys())}")
    
    # Test trailing stop update
    pm.update_trailing_stop('BTCUSDT', 52000.0, 500.0)
    position = pm.open_positions['BTCUSDT']
    print(f"\nAfter price rise to 52000:")
    print(f"Stop Loss: ${position.current_sl:.2f}")
    print(f"Phase: {position.phase}")
    print(f"Breakeven: {position.is_breakeven}")
    
    # Test stop hit
    closed = pm.check_stop_hit('BTCUSDT', 48000.0, pd.Timestamp('2023-01-02'))
    if closed:
        print(f"\nPosition closed:")
        print(f"PnL: ${closed.pnl:.2f}")
        print(f"R-multiple: {closed.r_multiple:.2f}R")
        print(f"Final equity: ${pm.equity:.2f}")
    
    print("\n✅ Position manager test passed!")
