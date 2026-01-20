import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Update path to include project root
sys.path.append(os.getcwd())

from src.backtest.data_loader import DataLoader
from src.backtest.position_manager import PositionManager
from src.council.entry_logic_game_theory_optimized import EntryLogicGameTheoryOptimized, calculate_god_tier_trailing

class BacktestEngineOptimized:
    """
    Optimized Backtest Engine (Runner for Shadow Sniper Optimized)
    """
    
    def __init__(self, csv_path="data/BTCUSDT-1m-2017-08-to-2023-03 (Binance SPOT).csv", initial_capital=10000.0):
        print("\n" + "=" * 80)
        print("LOADING DATA")
        print("=" * 80)
        
        # Components
        self.data_loader = DataLoader(csv_path)
        self.position_manager = PositionManager(initial_capital=initial_capital)
        self.initial_capital = initial_capital
        
        # Data
        self.df_1m = self.data_loader.df_1m
        if self.df_1m is None:
            self.df_1m = self.data_loader.load_data()
            
        # Stats
        self.month_trades = []
        self.monthly_stats = []
        self.trade_log = []

    def run_backtest(self):
        print("\n" + "=" * 80)
        print("STARTING BACKTEST - SHADOW SNIPER OPTIMIZED (WINRATE BOOSTER)")
        print("=" * 80)
        
        strategy = EntryLogicGameTheoryOptimized()
        
        # Pre-calculate CLOSED H1 for history
        print("Pre-calculating Closed H1 History...")
        self.df_h1_closed = self.df_1m.resample('1h').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna()
        
        print(f"1m Data: {len(self.df_1m)} | H1 History: {len(self.df_h1_closed)}")
        print("Entering Execution Loop (Optimized)...")
        
        symbol = 'BTCUSDT'
        start_idx = 20000 # Warmup (approx 14 days)
        last_check_idx = 0
        check_interval = 15 # Check signals every 15 minutes
        
        last_month = self.df_1m.index[start_idx].month
        
        for i in range(start_idx, len(self.df_1m)):
            current_idx = self.df_1m.index[i]
            candle = self.df_1m.iloc[i]
            
            # --- 1. MONTHLY LOGGING ---
            if current_idx.month != last_month:
                self.log_monthly_stats(current_idx)
                last_month = current_idx.month

            # --- 2. SIGNAL CHECK (Every 15m) ---
            if (i - last_check_idx) >= check_interval:
                last_check_idx = i
                
                # Hybrid Slice: History + Partial Current Hour
                curr_hour_start = current_idx.replace(minute=0, second=0, microsecond=0)
                h1_hist = self.df_h1_closed[self.df_h1_closed.index < curr_hour_start]
                
                m1_partial = self.df_1m.loc[curr_hour_start : current_idx]
                if not m1_partial.empty:
                    partial_h1 = pd.DataFrame([{
                        'open': m1_partial['open'].iloc[0],
                        'high': m1_partial['high'].max(),
                        'low': m1_partial['low'].min(),
                        'close': m1_partial['close'].iloc[-1],
                        'volume': m1_partial['volume'].sum()
                    }], index=[curr_hour_start])
                    h1_full = pd.concat([h1_hist, partial_h1])
                else:
                    h1_full = h1_hist
                
                if len(h1_full) >= 200:
                    analysis = strategy.analyze(h1_full)
                    if analysis['signal'] == 'STRONG BUY' and symbol not in self.position_manager.open_positions:
                        entry_data = analysis['entry_data']
                        pos_data = {
                            'entry_price': candle['close'],
                            'stop_loss': entry_data['stop_loss'],
                            'initial_sl': entry_data['stop_loss'],
                            'atr': entry_data['atr'],
                            'entry_type': 'V6_OPTIMIZED',
                            'breakeven_ratio': 1.5, # Delayed BE per strategy
                            'trailing_multiplier': 3.0,
                            'highest_high': candle['high'],
                            'reason': analysis.get('reason', 'Signal')
                        }
                        if self.position_manager.open_position(symbol, current_idx, pos_data):
                            print(f"[{current_idx}] 🚀 ENTRY @ ${candle['close']:.2f} ({analysis['reason']})")

            # --- 3. POSITION MANAGEMENT (Every 1m) ---
            if symbol in self.position_manager.open_positions:
                pos = self.position_manager.open_positions[symbol]
                if candle['high'] > pos.highest_high:
                    pos.highest_high = candle['high']
                
                # Update Trail SL every 15m
                # Note: We must call the NEW calculate_god_tier_trailing from the optimized file
                if (i - last_check_idx) == 0:
                    res = calculate_god_tier_trailing(
                        pos.entry_price, pos.initial_sl, candle['close'], 
                        pos.highest_high, pos.atr, pos.is_breakeven, 
                        pos.trailing_multiplier, pos.breakeven_ratio
                    )
                    pos.current_sl = res['stop_loss']
                    pos.is_breakeven = res['is_breakeven']
                
                # Check SL
                if candle['low'] <= pos.current_sl:
                    closed = self.position_manager.close_position(symbol, pos.current_sl, current_idx, "TRAIL_HIT")
                    self.month_trades.append(closed)
                    
                    # LOG
                    reason_msg = getattr(pos, 'reason', 'Signal') # Might fail if pos object doesn't have it, but consistent with v1 logic
                    
                    self.trade_log.append({
                        'date': current_idx,
                        'entry_price': pos.entry_price,
                        'exit_price': pos.current_sl,
                        'pnl': closed.pnl,
                        'pnl_r': closed.r_multiple,
                        'reason': 'Shadow Sniper Optimized'
                    })
                    
                    print(f"[{current_idx}] 💰 CLOSED PnL: ${closed.pnl:.2f} ({closed.r_multiple:.2f}R)")

        self.final_report()

    def log_monthly_stats(self, ts):
        equity = self.position_manager.equity
        trades = len(self.month_trades)
        wins = sum(1 for t in self.month_trades if t.pnl > 0)
        wr = (wins/trades*100) if trades > 0 else 0
        print(f"\n📊 {ts.strftime('%b %Y')}: Equity ${equity:,.2f} | Trades: {trades} | WR: {wr:.0f}%")
        self.month_trades = []

    def final_report(self):
        print("\n" + "=" * 80)
        print("BACKTEST COMPLETE")
        print("=" * 80)
        print(f"Final Equity: ${self.position_manager.equity:,.2f}")
        total_pnl = self.position_manager.equity - self.initial_capital
        print(f"Total PnL: ${total_pnl:,.2f} ({(total_pnl/self.initial_capital)*100:.2f}%)")
        print("=" * 80 + "\n")

    def save_results(self, output_dir="results/backtest_optimized_v3"):
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        df_trades = pd.DataFrame(self.trade_log)
        if not df_trades.empty:
            df_trades.to_csv(f"{output_dir}/trades.csv", index=False)
            print(f"✅ Trade log saved to: {output_dir}/trades.csv")
            
            # Simple Report
            wins = df_trades[df_trades['pnl'] > 0]
            losses = df_trades[df_trades['pnl'] <= 0]
            total = len(df_trades)
            win_rate = (len(wins) / total * 100) if total > 0 else 0
            
            with open(f"{output_dir}/report.md", "w") as f:
                f.write(f"# Shadow Sniper Optimized Report\n\n")
                f.write(f"- Final Equity: ${self.position_manager.equity:,.2f}\n")
                f.write(f"- Win Rate: {win_rate:.2f}%\n")
                f.write(f"- Total Trades: {total}\n")
                f.write(f"- Avg Win: {wins['pnl_r'].mean():.2f}R\n")
                f.write(f"- Avg Loss: {losses['pnl_r'].mean():.2f}R\n")

if __name__ == "__main__":
    engine = BacktestEngineOptimized()
    engine.run_backtest()
    engine.save_results()
