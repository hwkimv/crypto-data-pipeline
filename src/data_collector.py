"""
바이낸스에서 BTC/USDT 1분봉 데이터를 수집하는 모듈
Collects BTC/USDT 1-minute candle data from Binance
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List


class DataCollector:
    """바이낸스 데이터 수집기"""
    
    def __init__(self, symbol: str = 'BTC/USDT', timeframe: str = '1m'):
        """
        Initialize data collector
        
        Args:
            symbol: Trading pair symbol (default: BTC/USDT)
            timeframe: Candle timeframe (default: 1m)
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}  # Use spot market
        })
        
    def fetch_ohlcv(self, since: Optional[int] = None, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch OHLCV data from Binance
        
        Args:
            since: Start timestamp in milliseconds (optional)
            limit: Number of candles to fetch (max 1000)
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                self.symbol,
                timeframe=self.timeframe,
                since=since,
                limit=limit
            )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"Error fetching OHLCV data: {e}")
            raise
    
    def fetch_all_historical_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch all historical data from Binance
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD' (optional, defaults to 2017-01-01)
            end_date: End date in format 'YYYY-MM-DD' (optional, defaults to now)
            
        Returns:
            DataFrame with all historical OHLCV data
        """
        # Set default dates
        if start_date is None:
            start_date = '2017-01-01'  # Bitcoin futures started around this time
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Convert to timestamps
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
        
        print(f"Fetching data from {start_date} to {end_date}...")
        print(f"Symbol: {self.symbol}, Timeframe: {self.timeframe}")
        
        all_data = []
        current_ts = start_ts
        batch_count = 0
        
        # Fetch data in batches
        while current_ts < end_ts:
            try:
                df = self.fetch_ohlcv(since=current_ts, limit=1000)
                
                if df.empty:
                    print("No more data available")
                    break
                
                all_data.append(df)
                batch_count += 1
                
                # Update timestamp for next batch
                last_timestamp = df['timestamp'].iloc[-1]
                current_ts = int(last_timestamp.timestamp() * 1000) + 60000  # +1 minute
                
                # Progress update
                if batch_count % 10 == 0:
                    print(f"Fetched {batch_count} batches, last timestamp: {last_timestamp}")
                
                # Rate limiting
                time.sleep(0.5)  # Sleep to avoid rate limits
                
                # Break if we've reached the end date
                if current_ts >= end_ts:
                    break
                    
            except Exception as e:
                print(f"Error at batch {batch_count}: {e}")
                # Wait and retry
                time.sleep(2)
                continue
        
        if not all_data:
            raise ValueError("No data was collected")
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Remove duplicates and sort
        combined_df = combined_df.drop_duplicates(subset=['timestamp'])
        combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
        
        print(f"\nTotal candles collected: {len(combined_df)}")
        print(f"Date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
        
        return combined_df
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate collected data
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        if df.empty:
            print("Validation failed: DataFrame is empty")
            return False
        
        # Check for required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            print(f"Validation failed: Missing required columns")
            return False
        
        # Check for null values
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            print(f"Validation warning: Found null values:\n{null_counts[null_counts > 0]}")
        
        # Check for negative prices
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if (df[col] <= 0).any():
                print(f"Validation failed: Found negative or zero values in {col}")
                return False
        
        # Check OHLC logic (high >= low, high >= open, high >= close, low <= open, low <= close)
        invalid_high = (df['high'] < df['low']) | (df['high'] < df['open']) | (df['high'] < df['close'])
        invalid_low = (df['low'] > df['open']) | (df['low'] > df['close'])
        
        if invalid_high.any() or invalid_low.any():
            print(f"Validation warning: Found {invalid_high.sum() + invalid_low.sum()} candles with invalid OHLC relationships")
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['timestamp']).sum()
        if duplicates > 0:
            print(f"Validation warning: Found {duplicates} duplicate timestamps")
        
        print("Validation completed successfully")
        return True
