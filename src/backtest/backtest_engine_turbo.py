import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Update path to include project root
sys.path.append(os.getcwd())

from src.backtest.data_loader import DataLoader
from src.backtest.position_manager import PositionManager
from src.council.entry_logic_turbo_sniper import EntryLogicTurboSniper, calculate_god_tier_trailing

class BacktestEngineTurbo:
    """
    Turbo Backtest Engine (M15 Support + Short Logic)
    """
    
    def __init__(self, csv_path="data/BTCUSDT-1m-2017-08-to-2023-03 (Binance SPOT).csv", initial_capital=10000.0):
        print("\n" + "=" * 80)
        print("LOADING DATA")
        print("=" * 80)
        
        self.data_loader = DataLoader(csv_path)
        self.position_manager = PositionManager(initial_capital=initial_capital)
        self.initial_capital = initial_capital
        
        self.df_1m = self.data_loader.df_1m
        if self.df_1m is None:
            self.df_1m = self.data_loader.load_data()
            
        self.month_trades = []
        self.trade_log = []

    def run_backtest(self):
        print("\n" + "=" * 80)
        print("STARTING BACKTEST - TURBO SNIPER V4 (M15 + SHORT ENABLED)")
        print("=" * 80)
        
        strategy = EntryLogicTurboSniper()
        
        # Pre-calculate CLOSED M15 for history
        print("Pre-calculating Closed M15 History...")
        self.df_m15_closed = self.df_1m.resample('15min').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna()
        
        print(f"1m Data: {len(self.df_1m)} | M15 History: {len(self.df_m15_closed)}")
        print("Entering Execution Loop (Turbo)...")
        
        symbol = 'BTCUSDT'
        start_idx = 20000 
        last_check_idx = 0
        check_interval = 5 # Check signals every 5 minutes/or 15? Strategy uses M15. Let's check every 15m align.
        # Actually better to check every 5m to catch intra-candle volatility? No, strategy operates on closed M15.
        # Let's align to 15m.
        
        last_month = self.df_1m.index[start_idx].month
        last_day = self.df_1m.index[start_idx].day
        self.start_of_day_equity = self.position_manager.equity
        
        for i in range(start_idx, len(self.df_1m)):
            current_idx = self.df_1m.index[i]
            candle = self.df_1m.iloc[i]
            
            # Day Reset & Month Log
            if current_idx.day != last_day:
                self.start_of_day_equity = self.position_manager.equity # Reset daily baseline
                last_day = current_idx.day
                
            if current_idx.month != last_month:
                self.log_monthly_stats(current_idx)
                last_month = current_idx.month

            # --- SIGNAL CHECK (Every 15m) ---
            if current_idx.minute % 15 == 0 and (i - last_check_idx) >= 1: 
                # Ensuring we only check once per 15m interval close
                last_check_idx = i
                
                # Hybrid Slice: History < Current Time 
                # (Lookahead Proof: Only data strictly BEFORE current_idx)
                # But since we run on 1m loop, 'current_idx' is the exact time.
                # If Minute is 0, 15, 30, 45 -> previous 15m block is closed.
                
                # Correct Slicing:
                curr_time_m15 = current_idx #.replace(second=0, microsecond=0)
                m15_hist = self.df_m15_closed[self.df_m15_closed.index < curr_time_m15]
                
                # We don't need partial candle construction if we only trade on CLOSED candles logic
                # Strategy uses _resample_to_m15 inside, but passing strict closed history is safer and faster.
                
                if len(m15_hist) >= 500:
                    # KILL SWITCH CALC
                    daily_pnl = self.position_manager.equity - self.start_of_day_equity
                    daily_pnl_pct = daily_pnl / self.start_of_day_equity
                    
                    analysis = strategy.analyze(m15_hist, daily_pnl_pct=daily_pnl_pct)
                    
                    if analysis['signal'] != 'NEUTRAL' and symbol not in self.position_manager.open_positions:
                        res = analysis['entry_data']
                        entry_type = res['type'] # BUY or SELL
                        
                        # Apply Size Multiplier (Manually adjust risk if PM doesn't support it native)
                        # PM.risk_pct is fixed usually. We can hack it by passing a huge account size? No.
                        # We pass custom 'risk_weight'?
                        # Let's assume standard risk 2% * multiplier.
                        base_risk_amount = self.position_manager.equity * 0.02
                        risk_amount = base_risk_amount * res.get('size_multiplier', 1.0)
                        
                        # Custom Logic to calc qty
                        risk_per_share = abs(res['entry_price'] - res['stop_loss'])
                        qty = risk_amount / risk_per_share if risk_per_share > 0 else 0
                        
                        # Initialize Position Metadata
                        pos_data = {
                            'entry_price': res['entry_price'],
                            'stop_loss': res['stop_loss'],
                            'initial_sl': res['stop_loss'],
                            'atr': res['atr'],
                            'entry_type': entry_type, # BUY/SELL
                            'breakeven_ratio': 1.5,
                            'trailing_multiplier': 2.5,
                            'highest_high': candle['high'], # For Long Trail
                            'lowest_low': candle['low'],    # For Short Trail
                            'reason': res['reason'],
                            'size_mult': res.get('size_multiplier', 1.0),
                            'side': entry_type # CRITICAL for short logic
                        }
                        
                        # OPEN POSITION (Bypassing PM sizing logic if needed, or update PM)
                        # For now, let's use standard PM open and manually track SIDE.
                        # Warning: PM might calculate PnL assuming Long only. We need to handle Short PnL calc.
                        
                        # --- MANUAL POSITION OPEN (Bypassing PM for Short Logic) ---
                        
                        # 1. Calculate Quantity (Long/Short Agnostic)
                        risk_per_unit = abs(res['entry_price'] - res['stop_loss']) 
                        if risk_per_unit > 0:
                            qty = risk_amount / risk_per_unit
                        else:
                            qty = 0
                        
                        # Max Size Check (Full Equity)
                        cost = qty * res['entry_price']
                        if cost > self.position_manager.equity * 0.98:
                            qty = (self.position_manager.equity * 0.98) / res['entry_price']
                        
                        if qty > 0:
                            # 2. Manual Object Creation
                            # Need to import Position class? Or simple duck typing?
                            # PM stores 'Position' objects. Let's try to import it or Mock it.
                            # Standard PM.Position class unavailable here without import.
                            # We can simply use a generic object or SimpleNamespace.
                            
                            class TurboPosition:
                                def __init__(self, **kwargs):
                                    self.__dict__.update(kwargs)
                                    
                            pos = TurboPosition(
                                symbol=symbol,
                                entry_time=current_idx,
                                entry_price=res['entry_price'],
                                quantity=qty,
                                initial_sl=res['stop_loss'],
                                current_sl=res['stop_loss'],
                                atr=res['atr'],
                                is_breakeven=False,
                                entry_type=entry_type,
                                breakeven_ratio=1.5,
                                trailing_multiplier=2.5,
                                highest_high=candle['high'],
                                lowest_low=candle['low'],
                                side=entry_type,
                                size_mult=res.get('size_multiplier', 1.0),
                                reason=res['reason']
                            )
                            
                            # 3. Inject into PM (Simulate Cash Deduction? Actually Equity is key)
                            # Turbo Engine tracks Equity directly via PnL updates. We can ignore 'Cash' field of PM if we focus on Equity PnL.
                            self.position_manager.open_positions[symbol] = pos
                            
                            print(f"[{current_idx}] ⚡ {entry_type} @ ${candle['close']:.2f} (x{res.get('size_multiplier', 1.0)}) | {res['reason']}")

            # --- POSITION MANAGEMENT (Every 1m) ---
            if symbol in self.position_manager.open_positions:
                pos = self.position_manager.open_positions[symbol]
                
                is_long = getattr(pos, 'side', 'BUY') == 'BUY'
                
                # Track Highs/Lows
                if candle['high'] > pos.highest_high: pos.highest_high = candle['high']
                if candle['low'] < getattr(pos, 'lowest_low', 999999): pos.lowest_low = candle['low']
                
                # --- UPDATE TRAILING STOP (Every 15m) ---
                if current_idx.minute % 15 == 0:
                    res = calculate_god_tier_trailing(
                        pos.entry_price, 
                        pos.current_sl, # Pass Current Active SL
                        candle['close'], 
                        pos.highest_high, 
                        getattr(pos, 'lowest_low', 0),
                        pos.atr, 
                        is_long=is_long,
                        is_breakeven=pos.is_breakeven, 
                        multiplier=pos.trailing_multiplier
                    )
                    pos.current_sl = res['stop_loss']
                    pos.is_breakeven = res['is_breakeven']
                
                # --- CHECK EXIT ---
                exit_triggered = False
                exit_price = 0
                
                if is_long:
                    # SL Hit
                    if candle['low'] <= pos.current_sl:
                        exit_price = pos.current_sl
                        exit_triggered = True
                else:
                    # Short SL Hit (Price goes UP above SL)
                    if candle['high'] >= pos.current_sl:
                        exit_price = pos.current_sl
                        exit_triggered = True
                        
                if exit_triggered:
                    # Close Logic
                    # We need to manually calculate PnL for Shorts if PM is Long-Only
                    # Or we patch PM. Let's do it here manually for safety.
                    
                    closed_qty = pos.quantity
                    if is_long:
                        pnl = (exit_price - pos.entry_price) * closed_qty
                    else:
                        pnl = (pos.entry_price - exit_price) * closed_qty # Short PnL
                        
                    # Fee (0.1% approx)
                    fee = (exit_price * closed_qty) * 0.001
                    pnl -= fee
                    
                    self.position_manager.equity += pnl # Update Equity directly
                    
                    # Log
                    risk_r = abs(pos.entry_price - pos.initial_sl)
                    pnl_r = (pnl / (risk_r * closed_qty)) if risk_r > 0 else 0
                    
                    # Remove
                    del self.position_manager.open_positions[symbol]
                    
                    # Record
                    trade_rec = {
                        'date': current_idx,
                        'type': pos.side,
                        'entry': pos.entry_price,
                        'exit': exit_price,
                        'pnl': pnl,
                        'pnl_r': pnl_r,
                        'reason': pos.reason
                    }
                    self.trade_log.append(trade_rec)
                    self.month_trades.append(trade_rec) # For stats
                    
                    print(f"[{current_idx}] 💰 CLOSED {pos.side} PnL: ${pnl:.2f} ({pnl_r:.2f}R)")

        self.final_report()

    def log_monthly_stats(self, ts):
        equity = self.position_manager.equity
        trades = len(self.month_trades)
        wins = sum(1 for t in self.month_trades if t['pnl'] > 0)
        wr = (wins/trades*100) if trades > 0 else 0
        print(f"\n📊 {ts.strftime('%b %Y')}: Equity ${equity:,.2f} | Trades: {trades} | WR: {wr:.0f}%")
        self.month_trades = []

    def final_report(self):
        print("\n" + "=" * 80)
        print("TURBO BACKTEST COMPLETE")
        print("=" * 80)
        print(f"Final Equity: ${self.position_manager.equity:,.2f}")
        
    def save_results(self):
        df = pd.DataFrame(self.trade_log)
        df.to_csv("results/turbo_trades.csv", index=False)
        print("Draft saved to results/turbo_trades.csv")

if __name__ == "__main__":
    engine = BacktestEngineTurbo()
    engine.run_backtest()
    engine.save_results()
