"""
Example script showing how to use the crypto data pipeline
"""

from src.pipeline import CryptoDataPipeline
from src.data_collector import DataCollector
from src.indicators import TechnicalIndicators
import pandas as pd

# Example 1: Using the full pipeline
print("="*80)
print("Example 1: Full Pipeline")
print("="*80)

pipeline = CryptoDataPipeline(symbol='BTC/USDT', timeframe='1m')

# Run for a specific date range
# Note: This requires internet connection to Binance API
# df = pipeline.run(
#     start_date='2024-12-01',
#     end_date='2024-12-31',
#     output_file='btc_december_2024.csv'
# )

print("\nTo run the full pipeline:")
print("  pipeline = CryptoDataPipeline()")
print("  df = pipeline.run(start_date='2024-01-01', output_file='data.csv')")

# Example 2: Using individual components
print("\n" + "="*80)
print("Example 2: Using Individual Components")
print("="*80)

# Collect data
print("\n1. Data Collection:")
print("  collector = DataCollector(symbol='BTC/USDT', timeframe='1m')")
print("  df = collector.fetch_all_historical_data('2024-01-01', '2024-12-31')")

# Calculate indicators
print("\n2. Calculate Indicators:")
print("  df_with_indicators = TechnicalIndicators.add_all_indicators(df)")

# Validate
print("\n3. Validate:")
print("  collector.validate_data(df)")
print("  TechnicalIndicators.validate_indicators(df_with_indicators)")

# Save
print("\n4. Save to CSV:")
print("  df_with_indicators.to_csv('output.csv', index=False)")

# Example 3: Using with your own data
print("\n" + "="*80)
print("Example 3: Using with Your Own Data")
print("="*80)

# Create sample data
data = {
    'timestamp': pd.date_range('2024-01-01', periods=1000, freq='1min'),
    'open': [50000 + i for i in range(1000)],
    'high': [50100 + i for i in range(1000)],
    'low': [49900 + i for i in range(1000)],
    'close': [50050 + i for i in range(1000)],
    'volume': [100] * 1000
}
df = pd.DataFrame(data)

print("\nCalculating indicators on custom data...")
df_with_indicators = TechnicalIndicators.add_all_indicators(df)

print(f"✓ Added {len(df_with_indicators.columns) - len(df.columns)} indicators")
print(f"\nAvailable indicators:")
indicator_cols = [col for col in df_with_indicators.columns if col not in df.columns]
for col in indicator_cols:
    print(f"  - {col}")

print("\n" + "="*80)
print("For more information, see README.md")
print("="*80)
