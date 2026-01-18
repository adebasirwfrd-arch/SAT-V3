import pandas as pd
import numpy as np
from src.utils.risk_manager import RiskManager

def run_test():
    print("🛡️ TESTING IMMORTAL SHIELD (Risk Manager)...\n")
    
    # 1. Setup Dummy Data for ATR
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    df = pd.DataFrame({'time': dates})
    df['high'] = np.random.uniform(20100, 20200, 100)
    df['low']  = np.random.uniform(19800, 19900, 100)
    df['close'] = (df['high'] + df['low']) / 2
    
    # 2. Initialize Risk Manager
    risk_man = RiskManager(max_risk_pct=0.02, atr_multiplier=2.0)
    
    # 3. Calculate Logic
    current_atr = risk_man.calculate_atr(df)
    print(f"📊 Market Volatility (ATR): {current_atr:.2f}")
    
    balance = 10000 # $10,000
    entry_price = 20000 # BTC Price
    
    print(f"💰 Account Balance: ${balance}")
    print(f"🎯 Entry Price: ${entry_price}")
    
    params = risk_man.calculate_entry_params(balance, entry_price, current_atr)
    
    print("\n📝 TRADE PLAN CALCULATED:")
    print(f"   Stop Loss Price : ${params['stop_loss']:.2f}")
    print(f"   Take Profit     : ${params['take_profit']:.2f} (1.5R)")
    print(f"   Quantity to Buy : {params['quantity']:.4f} BTC")
    print(f"   Risk Amount     : ${params['risk_amount_usdt']:.2f} (Max Loss)")
    
    # 4. Validation
    potential_loss = (entry_price - params['stop_loss']) * params['quantity']
    print(f"\n🧮 Math Check: Real Potential Loss = ${potential_loss:.2f}")
    
    # Toleransi pembulatan floating point
    if abs(potential_loss - params['risk_amount_usdt']) < 0.1:
        print("✅ TEST PASSED: Position Sizing protects capital perfectly.")
    else:
        print("❌ TEST FAILED: Math mismatch.")

if __name__ == "__main__":
    run_test()
