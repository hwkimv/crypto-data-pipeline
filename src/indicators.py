"""
암호화폐 트레이딩 기술 지표 계산 모듈

이 모듈은 가격 데이터를 기반으로 다양한 기술적 분석 지표를 계산합니다.
EMA, MACD, RSI, 볼린저 밴드 등의 주요 지표를 제공합니다.
"""

import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalIndicators:
    """
    기술 지표 계산기 클래스

    다양한 트레이딩 기술 지표를 계산하는 정적 메서드들을 제공합니다.
    모든 메서드는 정적 메서드로 구현되어 인스턴스 생성 없이 사용할 수 있습니다.

    제공하는 지표:
        - EMA (지수 이동 평균): 최근 데이터에 더 큰 가중치를 부여하는 이동 평균
        - MACD (이동 평균 수렴 확산): 추세의 방향과 강도를 파악
        - RSI (상대 강도 지수): 과매수/과매도 상태 판단
        - 볼린저 밴드: 가격의 변동성 측정
    """

    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """
        지수 이동 평균(EMA) 계산

        EMA는 최근 데이터에 더 큰 가중치를 부여하는 이동 평균입니다.
        단순 이동 평균보다 최근 가격 변화에 더 민감하게 반응합니다.

        매개변수:
            data: 가격 데이터 시리즈 (일반적으로 종가 사용)
            period: EMA 계산 기간
                   예: 12, 26, 50, 200 등

        반환값:
            계산된 EMA 값들의 시리즈
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
        MACD (이동 평균 수렴 확산) 계산

        MACD는 추세의 방향, 강도, 모멘텀을 파악하는 데 사용되는 지표입니다.
        두 개의 EMA 차이를 이용하여 매매 신호를 생성합니다.

        구성요소:
            - MACD 라인: 빠른 EMA - 느린 EMA
            - 시그널 라인: MACD 라인의 EMA
            - 히스토그램: MACD 라인 - 시그널 라인

        매개변수:
            data: 가격 데이터 시리즈 (일반적으로 종가 사용)
            fast_period: 빠른 EMA 기간 (기본값: 12)
            slow_period: 느린 EMA 기간 (기본값: 26)
            signal_period: 시그널 라인 EMA 기간 (기본값: 9)

        반환값:
            (MACD 라인, 시그널 라인, MACD 히스토그램) 튜플

        해석:
            - MACD가 시그널을 상향 돌파: 매수 신호
            - MACD가 시그널을 하향 돌파: 매도 신호
        """
        # 빠른 EMA와 느린 EMA 계산
        fast_ema = TechnicalIndicators.calculate_ema(data, fast_period)
        slow_ema = TechnicalIndicators.calculate_ema(data, slow_period)

        # MACD 라인 = 빠른 EMA - 느린 EMA
        macd_line = fast_ema - slow_ema
        # 시그널 라인 = MACD 라인의 EMA
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal_period)
        # 히스토그램 = MACD 라인 - 시그널 라인
        macd_histogram = macd_line - signal_line

        return macd_line, signal_line, macd_histogram

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        RSI (상대 강도 지수) 계산

        RSI는 가격의 상승 압력과 하락 압력의 상대적인 강도를 나타내는 지표입니다.
        과매수/과매도 구간을 판단하여 매매 타이밍을 포착하는 데 사용됩니다.

        매개변수:
            data: 가격 데이터 시리즈 (일반적으로 종가 사용)
            period: RSI 계산 기간 (기본값: 14)

        반환값:
            계산된 RSI 값들의 시리즈 (0~100 범위)

        해석:
            - RSI > 70: 과매수 구간 (매도 고려)
            - RSI < 30: 과매도 구간 (매수 고려)
            - RSI = 50: 중립
        """
        # 가격 변화량 계산
        delta = data.diff()

        # 상승분과 하락분 분리
        gains = delta.where(delta > 0, 0)  # 상승한 경우만 값 유지
        losses = -delta.where(delta < 0, 0)  # 하락한 경우만 값 유지 (양수로 변환)

        # 평균 상승분과 평균 하락분 계산 (EMA 방식)
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()

        # RS (상대 강도) = 평균 상승분 / 평균 하락분
        rs = avg_gains / avg_losses
        # RSI = 100 - (100 / (1 + RS))
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        볼린저 밴드 계산

        볼린저 밴드는 가격의 변동성을 측정하고 상대적인 고가/저가를 판단하는 지표입니다.
        가격이 밴드 내에서 움직이는 경향이 있으며, 밴드를 벗어나면 추세 전환 가능성을 시사합니다.

        구성요소:
            - 중간 밴드: 단순 이동 평균 (SMA)
            - 상단 밴드: 중간 밴드 + (표준편차 × 배수)
            - 하단 밴드: 중간 밴드 - (표준편차 × 배수)

        매개변수:
            data: 가격 데이터 시리즈 (일반적으로 종가 사용)
            period: 이동 평균 계산 기간 (기본값: 20)
            std_dev: 표준편차 배수 (기본값: 2.0)
                    값이 클수록 밴드 폭이 넓어짐

        반환값:
            (상단 밴드, 중간 밴드, 하단 밴드) 튜플

        해석:
            - 가격이 상단 밴드 접근: 과매수 가능성
            - 가격이 하단 밴드 접근: 과매도 가능성
            - 밴드 폭 확대: 변동성 증가
            - 밴드 폭 축소: 변동성 감소 (큰 움직임 임박 가능)
        """
        # 중간 밴드 (단순 이동 평균)
        middle_band = data.rolling(window=period).mean()
        # 표준 편차 계산
        std = data.rolling(window=period).std()

        # 상단 밴드와 하단 밴드 계산
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band, middle_band, lower_band

    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        모든 기술 지표를 데이터프레임에 추가

        OHLCV 데이터에 다양한 기술 지표를 계산하여 추가

        매개변수:
            df: OHLCV 데이터프레임 (필수: 'close' 컬럼)

        반환값:
            지표가 추가된 데이터프레임

        추가 지표:
            - ema_12, ema_26, ema_50, ema_200
            - macd, macd_signal, macd_histogram
            - rsi
            - bb_upper, bb_middle, bb_lower
        """
        df = df.copy()

        print("EMA 계산 중...")
        df['ema_12'] = TechnicalIndicators.calculate_ema(df['close'], 12)
        df['ema_26'] = TechnicalIndicators.calculate_ema(df['close'], 26)
        df['ema_50'] = TechnicalIndicators.calculate_ema(df['close'], 50)
        df['ema_200'] = TechnicalIndicators.calculate_ema(df['close'], 200)

        print("MACD 계산 중...")
        macd_line, signal_line, macd_histogram = TechnicalIndicators.calculate_macd(df['close'])
        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_histogram'] = macd_histogram

        print("RSI 계산 중...")
        df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'])

        print("볼린저 밴드 계산 중...")
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower

        print("지표 계산 완료")

        return df

    @staticmethod
    def validate_indicators(df: pd.DataFrame) -> bool:
        """
        지표 유효성 검증

        검증 항목:
            1. 필수 지표 존재
            2. RSI 범위 (0~100)
            3. 볼린저 밴드 순서 (상단 >= 중간 >= 하단)
            4. NaN 값 확인

        매개변수:
            df: 지표가 포함된 데이터프레임

        반환값:
            유효하면 True
        """
        required_indicators = [
            'ema_12', 'ema_26', 'ema_50', 'ema_200',
            'macd', 'macd_signal', 'macd_histogram',
            'rsi',
            'bb_upper', 'bb_middle', 'bb_lower'
        ]

        # 지표 존재 확인
        missing = [ind for ind in required_indicators if ind not in df.columns]
        if missing:
            print(f"검증 실패: 누락 지표 {missing}")
            return False

        # RSI 범위 확인
        rsi_values = df['rsi'].dropna()
        if not rsi_values.empty:
            if (rsi_values < 0).any() or (rsi_values > 100).any():
                print("검증 경고: RSI 범위 벗어남 (0~100)")

        # 볼린저 밴드 순서 확인
        bb_check = df[['bb_upper', 'bb_middle', 'bb_lower']].dropna()
        if not bb_check.empty:
            invalid_bb = (bb_check['bb_upper'] < bb_check['bb_middle']) | \
                         (bb_check['bb_middle'] < bb_check['bb_lower'])
            if invalid_bb.any():
                invalid_count = invalid_bb.sum()
                print(f"검증 경고: {invalid_count}개 볼린저 밴드 오류")

        # NaN 통계
        nan_counts = df[required_indicators].isna().sum()
        total_rows = len(df)
        print(f"\n지표 검증:")
        print(f"총 행: {total_rows:,}개")
        for indicator, nan_count in nan_counts.items():
            if nan_count > 0:
                percentage = nan_count / total_rows * 100
                print(f"  {indicator}: {nan_count}개 NaN ({percentage:.2f}%)")

        print("검증 완료")
        return True

