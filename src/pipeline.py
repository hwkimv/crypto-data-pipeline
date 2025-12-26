"""
데이터 수집 및 지표 계산 파이프라인
Data collection and indicator calculation pipeline
"""

import os
import sys
from datetime import datetime
import pandas as pd

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import DataCollector
from indicators import TechnicalIndicators


class CryptoDataPipeline:
    """암호화폐 데이터 파이프라인"""
    
    def __init__(self, symbol: str = 'BTC/USDT', timeframe: str = '1m'):
        """
        Initialize pipeline
        
        Args:
            symbol: Trading pair symbol (default: BTC/USDT)
            timeframe: Candle timeframe (default: 1m)
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.collector = DataCollector(symbol=symbol, timeframe=timeframe)
        self.data = None
        
    def run(
        self,
        start_date: str = None,
        end_date: str = None,
        output_file: str = None
    ) -> pd.DataFrame:
        """
        Run the complete pipeline
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD' (optional)
            end_date: End date in format 'YYYY-MM-DD' (optional)
            output_file: Output CSV file path (optional)
            
        Returns:
            DataFrame with OHLCV data and technical indicators
        """
        print("="*80)
        print("암호화폐 데이터 수집 파이프라인")
        print("Crypto Data Collection Pipeline")
        print("="*80)
        
        # Step 1: Collect data
        print("\n[Step 1/4] Collecting historical data from Binance...")
        try:
            self.data = self.collector.fetch_all_historical_data(
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            print(f"Error collecting data: {e}")
            raise
        
        # Step 2: Validate raw data
        print("\n[Step 2/4] Validating collected data...")
        if not self.collector.validate_data(self.data):
            raise ValueError("Data validation failed")
        
        # Step 3: Calculate technical indicators
        print("\n[Step 3/4] Calculating technical indicators...")
        try:
            self.data = TechnicalIndicators.add_all_indicators(self.data)
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            raise
        
        # Validate indicators
        if not TechnicalIndicators.validate_indicators(self.data):
            raise ValueError("Indicator validation failed")
        
        # Step 4: Save to CSV
        if output_file is None:
            # Create default filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"btc_usdt_1m_{timestamp}.csv"
        
        print(f"\n[Step 4/4] Saving data to {output_file}...")
        try:
            self.save_to_csv(output_file)
        except Exception as e:
            print(f"Error saving data: {e}")
            raise
        
        # Display summary
        self.display_summary()
        
        print("\n" + "="*80)
        print("Pipeline completed successfully!")
        print("="*80)
        
        return self.data
    
    def save_to_csv(self, filename: str):
        """
        Save data to CSV file
        
        Args:
            filename: Output file path
        """
        if self.data is None:
            raise ValueError("No data to save. Run the pipeline first.")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save to CSV
        self.data.to_csv(filename, index=False)
        
        # Get file size
        file_size = os.path.getsize(filename)
        size_mb = file_size / (1024 * 1024)
        
        print(f"Data saved successfully!")
        print(f"  File: {filename}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Rows: {len(self.data)}")
        print(f"  Columns: {len(self.data.columns)}")
    
    def display_summary(self):
        """Display summary statistics"""
        if self.data is None:
            print("No data available")
            return
        
        print("\n" + "="*80)
        print("Data Summary")
        print("="*80)
        
        print(f"\nBasic Information:")
        print(f"  Symbol: {self.symbol}")
        print(f"  Timeframe: {self.timeframe}")
        print(f"  Total candles: {len(self.data)}")
        print(f"  Date range: {self.data['timestamp'].min()} to {self.data['timestamp'].max()}")
        
        print(f"\nPrice Statistics (Close):")
        print(f"  Min: ${self.data['close'].min():.2f}")
        print(f"  Max: ${self.data['close'].max():.2f}")
        print(f"  Mean: ${self.data['close'].mean():.2f}")
        print(f"  Current: ${self.data['close'].iloc[-1]:.2f}")
        
        print(f"\nVolume Statistics:")
        print(f"  Min: {self.data['volume'].min():.2f}")
        print(f"  Max: {self.data['volume'].max():.2f}")
        print(f"  Mean: {self.data['volume'].mean():.2f}")
        
        print(f"\nTechnical Indicators (Latest Values):")
        latest = self.data.iloc[-1]
        if 'rsi' in self.data.columns:
            print(f"  RSI: {latest['rsi']:.2f}")
        if 'macd' in self.data.columns:
            print(f"  MACD: {latest['macd']:.2f}")
            print(f"  MACD Signal: {latest['macd_signal']:.2f}")
        if 'ema_12' in self.data.columns:
            print(f"  EMA(12): ${latest['ema_12']:.2f}")
            print(f"  EMA(26): ${latest['ema_26']:.2f}")
            print(f"  EMA(50): ${latest['ema_50']:.2f}")
            print(f"  EMA(200): ${latest['ema_200']:.2f}")
        
        print(f"\nColumn List:")
        for i, col in enumerate(self.data.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\nData Quality:")
        null_counts = self.data.isnull().sum()
        total_nulls = null_counts.sum()
        print(f"  Total null values: {total_nulls}")
        if total_nulls > 0:
            print(f"  Columns with nulls:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"    {col}: {count}")


def main():
    """메인 실행 함수 - 커맨드라인 인자 처리"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='바이낸스 BTC/USDT 데이터 수집 및 기술지표 계산 파이프라인'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='시작 날짜 (YYYY-MM-DD, 기본: 2017-01-01)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='종료 날짜 (YYYY-MM-DD, 기본: 오늘)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='출력 CSV 파일 경로 (기본: btc_usdt_1m_TIMESTAMP.csv)'
    )
    parser.add_argument(
        '--symbol',
        type=str,
        default='BTC/USDT',
        help='거래쌍 (기본: BTC/USDT)'
    )
    parser.add_argument(
        '--timeframe',
        type=str,
        default='1m',
        help='캔들 간격 (기본: 1m)'
    )
    
    args = parser.parse_args()
    
    # 파이프라인 실행
    pipeline = CryptoDataPipeline(symbol=args.symbol, timeframe=args.timeframe)
    
    try:
        pipeline.run(
            start_date=args.start_date,
            end_date=args.end_date,
            output_file=args.output
        )
    except KeyboardInterrupt:
        print("\n\n사용자가 중단했습니다")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n파이프라인 실패: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
