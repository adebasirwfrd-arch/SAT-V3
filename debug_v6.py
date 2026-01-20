import os
import sys
import pandas as pd
import numpy as np

# Adjust path
sys.path.append(os.getcwd())

from src.backtest.data_loader import DataLoader
from src.council.entry_logic_master_v6 import EntryLogicMasterV6

def debug_v6_sep_2017():
    print("DEBUGER: Inspecting V6 on Sep 2017...")
    loader = DataLoader("data/BTCUSDT-1m-2017-08-to-2023-03 (Binance SPOT).csv")
    df_1m = loader.load_data()
    
    # Slice Nov 2017
    start_date = "2017-10-01"
    end_date = "2017-12-30"
    df_subset = df_1m.loc[start_date:end_date]
    
    strategy = EntryLogicMasterV6()
    
    # Resample to H1
    df_h1 = df_subset.resample('1h').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
    }).dropna()
    
    # Calculate indicators manually for inspection
    df_h1['EMA_200'] = df_h1['close'].ewm(span=200, adjust=False).mean()
    df_h1['Resistance'] = df_h1['high'].rolling(window=24).max().shift(1)
    
    print(f"H1 Data Size: {len(df_h1)}")
    
    # Loop through Nov 2017 (index starts after 200 bars warmup)
    for i in range(500, len(df_h1)):
        row = df_h1.iloc[i]
        prev = df_h1.iloc[i-1]
        
        is_above_ema = row['close'] > row['EMA_200']
        is_price_break = prev['close'] > row['Resistance']
        
        # Debugging the lack of breakouts
        if i % 100 == 0:
            print(f"[{df_h1.index[i]}] Price: {row['close']:.2f}, Res: {row['Resistance']:.2f}, EMA: {row['EMA_200']:.2f}")

        res = strategy.analyze(df_h1.iloc[:i+1])
        if res['signal'] == 'STRONG BUY':
            print(f"[{df_h1.index[i]}] ✅ SIGNAL DETECTED: {res['reason']}")
        elif strategy.waiting_retest:
             if i % 10 == 0:
                 print(f"  ... [{df_h1.index[i]}] Waiting retest of {strategy.flip_zone:.2f}")

if __name__ == "__main__":
    debug_v6_sep_2017()
