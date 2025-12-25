"""
기술 지표 계산 모듈
Technical indicators calculation module
"""

import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalIndicators:
    """기술 지표 계산기"""
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            data: Price data series
            period: EMA period
            
        Returns:
            EMA values
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price data series (typically close prices)
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line period (default: 9)
            
        Returns:
            Tuple of (MACD line, Signal line, MACD histogram)
        """
        fast_ema = TechnicalIndicators.calculate_ema(data, fast_period)
        slow_ema = TechnicalIndicators.calculate_ema(data, slow_period)
        
        macd_line = fast_ema - slow_ema
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal_period)
        macd_histogram = macd_line - signal_line
        
        return macd_line, signal_line, macd_histogram
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index)
        
        Args:
            data: Price data series
            period: RSI period (default: 14)
            
        Returns:
            RSI values
        """
        # Calculate price changes
        delta = data.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data: Price data series
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2.0)
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to the dataframe
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added technical indicators
        """
        df = df.copy()
        
        # Calculate EMAs
        print("Calculating EMAs...")
        df['ema_12'] = TechnicalIndicators.calculate_ema(df['close'], 12)
        df['ema_26'] = TechnicalIndicators.calculate_ema(df['close'], 26)
        df['ema_50'] = TechnicalIndicators.calculate_ema(df['close'], 50)
        df['ema_200'] = TechnicalIndicators.calculate_ema(df['close'], 200)
        
        # Calculate MACD
        print("Calculating MACD...")
        macd_line, signal_line, macd_histogram = TechnicalIndicators.calculate_macd(df['close'])
        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_histogram'] = macd_histogram
        
        # Calculate RSI
        print("Calculating RSI...")
        df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'])
        
        # Calculate Bollinger Bands
        print("Calculating Bollinger Bands...")
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower
        
        print("All indicators calculated successfully")
        
        return df
    
    @staticmethod
    def validate_indicators(df: pd.DataFrame) -> bool:
        """
        Validate calculated indicators
        
        Args:
            df: DataFrame with indicators
            
        Returns:
            True if indicators are valid, False otherwise
        """
        required_indicators = [
            'ema_12', 'ema_26', 'ema_50', 'ema_200',
            'macd', 'macd_signal', 'macd_histogram',
            'rsi',
            'bb_upper', 'bb_middle', 'bb_lower'
        ]
        
        # Check if all indicators exist
        missing = [ind for ind in required_indicators if ind not in df.columns]
        if missing:
            print(f"Validation failed: Missing indicators: {missing}")
            return False
        
        # Check RSI range (should be 0-100)
        rsi_values = df['rsi'].dropna()
        if not rsi_values.empty:
            if (rsi_values < 0).any() or (rsi_values > 100).any():
                print("Validation warning: RSI values outside 0-100 range")
        
        # Check Bollinger Bands order (upper >= middle >= lower)
        bb_check = df[['bb_upper', 'bb_middle', 'bb_lower']].dropna()
        if not bb_check.empty:
            invalid_bb = (bb_check['bb_upper'] < bb_check['bb_middle']) | \
                         (bb_check['bb_middle'] < bb_check['bb_lower'])
            if invalid_bb.any():
                print(f"Validation warning: Found {invalid_bb.sum()} invalid Bollinger Band relationships")
        
        # Count NaN values
        nan_counts = df[required_indicators].isna().sum()
        total_rows = len(df)
        print(f"\nIndicator validation summary:")
        print(f"Total rows: {total_rows}")
        for indicator, nan_count in nan_counts.items():
            if nan_count > 0:
                print(f"  {indicator}: {nan_count} NaN values ({nan_count/total_rows*100:.2f}%)")
        
        print("Indicator validation completed")
        return True
