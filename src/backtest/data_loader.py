"""
Data Loader for Historical Backtest
Loads 1-minute BTCUSDT data and resamples to 1H for signal detection
Ensures no look-ahead bias
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Optional


class DataLoader:
    """
    Load and preprocess historical OHLCV data for backtesting
    """
    
    def __init__(self, csv_path: str):
        """
        Args:
            csv_path: Path to BTCUSDT CSV file (1m data)
        """
        self.csv_path = csv_path
        self.df_1m = None
        self.df_1h = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load 1-minute data from CSV
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        print(f"Loading data from {self.csv_path}...")
        
        self.df_1m = pd.read_csv(self.csv_path)
        # Parse datetime with milliseconds support
        self.df_1m['date'] = pd.to_datetime(self.df_1m['date'], format='mixed')
        self.df_1m.set_index('date', inplace=True)
        
        # Validate data
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        assert all(col in self.df_1m.columns for col in required_cols), "Missing required columns"
        
        # Remove any NaN values
        initial_len = len(self.df_1m)
        self.df_1m.dropna(inplace=True)
        dropped = initial_len - len(self.df_1m)
        
        print(f"✅ Loaded {len(self.df_1m):,} candles (dropped {dropped} NaN rows)")
        print(f"📅 Date range: {self.df_1m.index[0]} to {self.df_1m.index[-1]}")
        
        return self.df_1m
    
    def resample_to_1h(self, no_lookahead: bool = True) -> pd.DataFrame:
        """
        Resample 1m data to 1H for signal detection
        
        Args:
            no_lookahead: If True, only return completed bars (critical for backtest integrity)
        
        Returns:
            DataFrame with 1H candles
        """
        if self.df_1m is None:
            raise ValueError("Must call load_data() first")
        
        print("Resampling to 1H...")
        
        # Resample OHLCV data
        self.df_1h = self.df_1m.resample('1H').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        
        # Drop incomplete bars (no lookahead)
        if no_lookahead:
            self.df_1h = self.df_1h[:-1]  # Remove last incomplete bar
        
        self.df_1h.dropna(inplace=True)
        
        print(f"✅ Created {len(self.df_1h):,} 1H candles")
        
        return self.df_1h
    
    def get_1h_data_until(self, timestamp: pd.Timestamp) -> pd.DataFrame:
        """
        Get 1H data up to (but not including) the given timestamp
        
        This ensures NO LOOK-AHEAD BIAS: at time T, we only have data < T
        
        Args:
            timestamp: Current timestamp in backtest
            
        Returns:
            DataFrame with 1H candles before timestamp
        """
        if self.df_1h is None:
            raise ValueError("Must call resample_to_1h() first")
        
        # Get only completed 1H bars before this timestamp
        return self.df_1h[self.df_1h.index < timestamp].copy()
    
    def get_date_range(self) -> Tuple[datetime, datetime]:
        """Get start and end dates of dataset"""
        if self.df_1m is None:
            raise ValueError("Must call load_data() first")
        return self.df_1m.index[0], self.df_1m.index[-1]
    
    def get_1m_candles_between(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """
        Get 1-minute candles in a specific range
        Used for precise execution and trailing stop updates
        
        Args:
            start: Start timestamp (inclusive)
            end: End timestamp (exclusive)
            
        Returns:
            DataFrame with 1m candles in range
        """
        if self.df_1m is None:
            raise ValueError("Must call load_data() first")
        
        return self.df_1m[(self.df_1m.index >= start) & (self.df_1m.index < end)].copy()


if __name__ == "__main__":
    # Test the data loader
    loader = DataLoader("data/BTCUSDT-1m-2017-08-to-2023-03 (Binance SPOT).csv")
    
    # Load 1m data
    df_1m = loader.load_data()
    print(f"\n1m Data sample:")
    print(df_1m.head())
    
    # Resample to 1H
    df_1h = loader.resample_to_1h(no_lookahead=True)
    print(f"\n1H Data sample:")
    print(df_1h.head())
    
    # Test no-lookahead
    test_timestamp = pd.Timestamp('2017-08-20 12:00:00')
    historical_1h = loader.get_1h_data_until(test_timestamp)
    print(f"\n1H data available at {test_timestamp}:")
    print(f"Last bar: {historical_1h.index[-1]}")
    assert historical_1h.index[-1] < test_timestamp, "LOOK-AHEAD BIAS DETECTED!"
    
    print("\n✅ Data loader test passed!")
