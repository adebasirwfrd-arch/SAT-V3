import pandas as pd
import numpy as np
from src.council.institutional_hybrid_v2 import InstitutionalHybridV2
import datetime

class BacktestEngineV2:
    def __init__(self, data_path):
        self.data_path = data_path
        self.initial_capital = 10000
        self.equity = 10000
        self.strategy = InstitutionalHybridV2()
        self.trades = []
        self.monthly_stats = {}
        
        # Load directly here or lazy load
        self.df_strategy = None
        self.df_raw_1m = None

    def load_and_prep_data(self):
        print(f"Loading data from {self.data_path}...")
        # Load 1m Data
        # Using a reliable parser setup
        try:
             df = pd.read_csv(self.data_path)
        except Exception as e:
             print(f"Error loading CSV: {e}")
             return None

        # Standardize timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
            df.set_index('timestamp', inplace=True)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format='mixed')
            df.set_index('date', inplace=True)
            df.index.name = 'timestamp' # Rename index for consistency
        else:
            print("Error: No timestamp or date column found.")
            return None
            
        df.sort_index(inplace=True)
        
        # Resample to 1H for Strategy Signals
        print("Resampling to 1H...")
        df_1h = df.resample('1H').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna()
        
        # Resample to Daily for Filter (Shifted inside strategy)
        print("Resampling to 1D...")
        df_daily = df.resample('1D').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
        }).dropna()
        
        # Inject Indicators
        print("Calculating indicators (Manual Pandas)...")
        self.df_strategy = self.strategy.prepare_data(df_1h, df_daily)
        self.df_raw_1m = df # Simpan raw 1m untuk eksekusi trailing stop (future proofing)
        
        return self.df_strategy

    def run(self):
        df_sim = self.load_and_prep_data()
        if df_sim is None:
            print("Data simulation failed to load.")
            return

        active_position = None
        
        print(f"Starting Backtest on {len(df_sim)} H1 candles...")
        
        # Loop Candle by Candle (H1)
        # Using iterrows is slow but functional for logic translation. 
        # For strict index matching we iterate strictly.
        
        total_candles = len(df_sim)
        
        for i in range(1, total_candles):
            curr_candle = df_sim.iloc[i]
            prev_candle = df_sim.iloc[i-1]
            
            # Progress bar
            if i % 5000 == 0:
                print(f"Processing candle {i}/{total_candles} | CV: {self.equity:.2f}")

            # 1. MANAGEMENT POSISI (Trailing Stop Check)
            # Checked at H1 Close for this specific implementation as per steps
            if active_position:
                self.manage_active_position(active_position, curr_candle)
                if active_position['status'] == 'CLOSED':
                    self.trades.append(active_position)
                    self.strategy.record_result(active_position['result']) # Beritahu strategi Win/Loss
                    
                    # Log trade
                    print(f"[{curr_candle.name}] CLOSED {active_position['type']} | PnL: ${active_position['pnl']:.2f} | Eq: ${self.equity:.2f}")
                    
                    active_position = None
            
            # 2. CARI SIGNAL BARU (Jika tidak ada posisi)
            if not active_position:
                # Context EMA is already in the candle row
                signal = self.strategy.check_signal(curr_candle, prev_candle, curr_candle['EMA_200_Shifted'])
                
                if signal:
                    # OPEN POSITION
                    risk_per_trade = self.equity * 0.01 # 1% Risk
                    entry_price = curr_candle['close']
                    atr_val = curr_candle['ATR']
                    
                    # Stop Loss Logic
                    # Logic note: "swing low" was mentioned in text but steps simplified to "low - buffer" for quick implementation?
                    # "trade.stop_loss = swing_low - (0.5 * ATR_14)"
                    # Langkah 20 text code uses: stop_loss = curr_candle['low'] - sl_buffer
                    # We stick to Langkah 20 text code verbatim.
                    
                    sl_buffer = 0.5 * atr_val
                    stop_loss = curr_candle['low'] - sl_buffer
                    
                    # Position Sizing
                    risk_distance = entry_price - stop_loss
                    
                    # Sanity check
                    if risk_distance <= 0: 
                        continue 
                    
                    qty = risk_per_trade / risk_distance
                    
                    active_position = {
                        'entry_time': curr_candle.name,
                        'type': signal, # BULLET_1 or BULLET_2
                        'entry_price': entry_price,
                        'qty': qty,
                        'stop_loss': stop_loss,
                        'initial_sl': stop_loss,
                        'tp_1': entry_price + (1.5 * risk_distance),
                        'is_breakeven': False,
                        'status': 'OPEN',
                        'highest_high': entry_price,
                        'atr_at_entry': atr_val
                    }
                    print(f"[{curr_candle.name}] ENTRY {signal} @ {entry_price:.2f}")

        # Summary
        self.generate_report()

    def manage_active_position(self, pos, candle):
        # Update Highest High
        if candle['high'] > pos['highest_high']:
            pos['highest_high'] = candle['high']
            
        # --- GOD TIER TRAILING LOGIC ---
        risk_dist = pos['entry_price'] - pos['initial_sl']
        if risk_dist == 0: risk_dist = 0.0001 # prevent div by zero
        
        current_profit_r = (candle['close'] - pos['entry_price']) / risk_dist
        
        # Fase 2: Secure Breakeven (at 1.5R)
        if current_profit_r >= 1.5 and not pos['is_breakeven']:
            pos['stop_loss'] = pos['entry_price']
            pos['is_breakeven'] = True
            
        # Fase 3: Chandelier Trailing (ATR 3.0)
        # Only active if we secured breakeven/profit territory? 
        # Text says: "elif trade.is_breakeven:" -> So only after BE is hit.
        if pos['is_breakeven']:
            new_sl = pos['highest_high'] - (3.0 * pos['atr_at_entry'])
            if new_sl > pos['stop_loss']:
                pos['stop_loss'] = new_sl
        
        # --- CHECK STOP LOSS HIT ---
        # LOW priority check implies we check if low wikced us out.
        if candle['low'] <= pos['stop_loss']:
            exit_price = pos['stop_loss']
            
            # Simple slippage estimation: if gap down, could be lower. 
            # But for simulation we take SL level or Open if Open < SL (Gap)
            if candle['open'] < pos['stop_loss']:
                exit_price = candle['open']
            
            # Hitung PnL (dikurangi Slippage & Commision)
            gross_pnl = (exit_price - pos['entry_price']) * pos['qty']
            commission = (exit_price * pos['qty']) * 0.001 # 0.1% normal spot fee
            net_pnl = gross_pnl - commission
            
            pos['exit_time'] = candle.name
            pos['exit_price'] = exit_price
            pos['pnl'] = net_pnl
            pos['status'] = 'CLOSED'
            pos['result'] = 'WIN' if net_pnl > 0 else 'LOSS'
            
            # Update Equity
            self.equity += net_pnl

    def generate_report(self):
        total_trades = len(self.trades)
        wins = len([t for t in self.trades if t['result'] == 'WIN'])
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        print("\n" + "="*40)
        print("INSTITUTIONAL HYBRID V2 REPORT")
        print("="*40)
        print(f"Final Equity : ${self.equity:,.2f}")
        print(f"Total Trades : {total_trades}")
        print(f"Win Rate     : {win_rate:.2f}%")
        print(f"Wins         : {wins}")
        print(f"Losses       : {losses}")
        print("="*40)
        
        # Simple breakdown
        df_trades = pd.DataFrame(self.trades)
        if not df_trades.empty:
            print("\nLAST 10 TRADES:")
            print(df_trades[['entry_time', 'type', 'result', 'pnl']].tail(10))
            
            # Drawdown
            # Reconstruct equity curve roughly
            # (Note: self.trades only has closed trades, equity curve needs time series for accurate DD)
            pass
