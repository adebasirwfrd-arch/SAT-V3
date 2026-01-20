from src.backtest.backtest_engine_v2 import BacktestEngineV2

# Konfigurasi Path
DATA_PATH = '/Users/izzadev/.gemini/antigravity/scratch/SAT-V3/data/BTCUSDT-1m-2017-08-to-2023-03 (Binance SPOT).csv'

if __name__ == "__main__":
    print("Initializing Hybrid V2 Backtest...")
    engine = BacktestEngineV2(DATA_PATH)
    engine.run()
    
    # Final confirmation
    print(f"DONE. Final Equity: ${engine.equity:.2f}")
