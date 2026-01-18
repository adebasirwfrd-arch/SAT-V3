import pandas as pd
import numpy as np
from src.council.chairman import TheChairman

def run_test():
    print("🧪 Generating Dummy Market Data...")
    dates = pd.date_range(start='2024-01-01', periods=300, freq='1h')
    df = pd.DataFrame({'time': dates})
    # Data Netral/Sideways
    df['close'] = np.linspace(100, 110, 300) + np.random.normal(0, 2, 300)
    df['open'] = df['close'] - 1
    df['high'] = df['close'] + 2
    df['low'] = df['close'] - 2
    df['volume'] = 1000

    chairman = TheChairman()
    
    # Test: Kita jalankan voting. 
    # Karena SentimentMaster menggunakan random mock news, 
    # perhatikan output console apakah "HYPE DETECTED" muncul atau tidak.
    
    result = chairman.solicit_votes(df)
    
    if 'sentiment' in result:
        print(f"✅ TEST PASSED: Sentiment Engine integrated correctly.")
        print(f"   Detected Mood: {result['sentiment']['mode']}")
    else:
        print("❌ TEST FAILED: Sentiment data missing.")

if __name__ == "__main__":
    run_test()
