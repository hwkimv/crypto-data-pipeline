"""
Test script to verify the pipeline works with sample data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import tempfile

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

from indicators import TechnicalIndicators


def generate_sample_data(days=2, start_price=50000):
    """Generate sample OHLCV data for testing"""
    # Generate 1-minute candles for specified days
    minutes = days * 24 * 60
    
    timestamps = []
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []
    volumes = []
    
    start_time = datetime(2024, 12, 24, 0, 0, 0)
    current_price = start_price
    
    for i in range(minutes):
        # Random walk for price
        change_pct = np.random.randn() * 0.001  # 0.1% standard deviation
        current_price = current_price * (1 + change_pct)
        
        # Generate OHLC for this candle
        open_price = current_price
        high_price = current_price * (1 + abs(np.random.randn() * 0.0005))
        low_price = current_price * (1 - abs(np.random.randn() * 0.0005))
        close_price = current_price * (1 + np.random.randn() * 0.0003)
        
        # Ensure OHLC logic
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        # Volume
        volume = np.random.uniform(10, 100)
        
        timestamps.append(start_time + timedelta(minutes=i))
        open_prices.append(open_price)
        high_prices.append(high_price)
        low_prices.append(low_price)
        close_prices.append(close_price)
        volumes.append(volume)
        
        current_price = close_price
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })
    
    return df


def test_indicators():
    """Test indicator calculation"""
    print("Generating sample data...")
    df = generate_sample_data(days=2, start_price=50000)
    
    print(f"Generated {len(df)} candles")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    print("\nCalculating indicators...")
    df_with_indicators = TechnicalIndicators.add_all_indicators(df)
    
    print("\nValidating indicators...")
    if TechnicalIndicators.validate_indicators(df_with_indicators):
        print("✓ All indicators calculated successfully!")
    
    print("\nSample data (last 5 rows):")
    print(df_with_indicators.tail())
    
    print("\nColumns available:")
    for i, col in enumerate(df_with_indicators.columns, 1):
        print(f"  {i}. {col}")
    
    # Save sample data
    output_file = os.path.join(tempfile.gettempdir(), 'sample_btc_data.csv')
    df_with_indicators.to_csv(output_file, index=False)
    print(f"\nSample data saved to: {output_file}")
    
    return df_with_indicators


if __name__ == '__main__':
    df = test_indicators()
    print("\n✓ Test completed successfully!")
