import ccxt
import pandas as pd
import sys
import os

def check_setup():
    print(f"✅ Python Version: {sys.version.split()[0]}")
    
    try:
        import pandas_ta
        print(f"✅ Pandas TA Version: {pandas_ta.version}")
    except ImportError:
        print("❌ Pandas TA not installed")

    try:
        exchange = ccxt.binance()
        # Fetch public ticker to test connection without keys
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Binance Connection (Public): SUCCESS")
        print(f"   BTC Price: {ticker['last']} USDT")
    except Exception as e:
        print(f"❌ Binance Connection Failed: {str(e)}")

    # Check directories
    dirs = ['logs', 'data', 'src', 'config']
    all_dirs_exist = all(os.path.exists(d) for d in dirs)
    if all_dirs_exist:
        print("✅ Directory Structure: VERIFIED")
    else:
        print("❌ Directory Structure: INCOMPLETE")

if __name__ == "__main__":
    check_setup()
