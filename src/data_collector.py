"""
바이낸스 암호화폐 데이터 수집 모듈

바이낸스 거래소 API를 사용하여 OHLCV 데이터(시가, 고가, 저가, 종가, 거래량)를 수집하고 검증합니다.
"""

import ccxt
import pandas as pd
from datetime import datetime, timezone
import time
from typing import Optional


class DataCollector:
    """
    바이낸스 데이터 수집기 클래스

    바이낸스 거래소에서 암호화폐 OHLCV 데이터를 수집하고 검증하는 기능을 제공합니다.
    ccxt 라이브러리를 사용하여 API 통신을 처리합니다.
    """

    def __init__(self, symbol: str = 'BTC/USDT', timeframe: str = '1m'):
        """
        데이터 수집기 초기화

        매개변수:
            symbol: 거래 페어 심볼 (기본값: 'BTC/USDT')
                   예: 'BTC/USDT', 'ETH/USDT', 'BNB/USDT'
            timeframe: 캔들 타임프레임 (기본값: '1m')
                      예: '1m', '5m', '15m', '1h', '1d'

        속성:
            self.symbol: 수집할 거래 페어
            self.timeframe: 캔들 시간 간격
            self.exchange: 바이낸스 거래소 API 클라이언트
        """
        self.symbol = symbol
        self.timeframe = timeframe
        # 바이낸스 거래소 API 클라이언트 초기화
        self.exchange = ccxt.binance({
            'enableRateLimit': True,  # API 요청 제한 자동 처리
            'options': {'defaultType': 'spot'}  # 현물 시장 사용
        })

    def fetch_ohlcv(self, since: Optional[int] = None, limit: int = 1000) -> pd.DataFrame:
        """
        OHLCV 데이터 수집

        매개변수:
            since: 시작 시간 (밀리초 타임스탬프)
            limit: 수집할 캔들 개수 (최대 1000)

        반환값:
            OHLCV 데이터프레임 (컬럼: timestamp, open, high, low, close, volume)
            timestamp는 UTC 시간 (타임존 제거)
        """
        try:
            # 바이낸스에서 OHLCV 데이터 요청
            ohlcv = self.exchange.fetch_ohlcv(
                self.symbol,
                timeframe=self.timeframe,
                since=since,
                limit=limit
            )

            # 데이터프레임으로 변환
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            # 타임스탬프를 UTC 시간으로 변환 (타임존 제거)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_localize(None)

            return df

        except Exception as e:
            print(f"데이터 수집 오류: {e}")
            raise

    def fetch_all_historical_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        과거 데이터 전체 수집

        바이낸스 API 제한(1회 최대 1000개)으로 인해 배치 단위로 나누어 수집합니다.

        매개변수:
            start_date: 시작 날짜 ('YYYY-MM-DD')
            end_date: 종료 날짜 ('YYYY-MM-DD') - 해당 날짜 23:59:59까지 포함

        반환값:
            전체 OHLCV 데이터프레임
        """
        # 기본 날짜 설정
        if start_date is None:
            start_date = '2017-01-01'
        if end_date is None:
            end_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')

        # 날짜를 밀리초 단위 타임스탬프로 변환
        # 시작: 해당 날짜 00:00:00
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)

        # 종료: 해당 날짜 23:59:59 (해당 날짜 전체 포함)
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999000)
        end_ts = int(end_dt.timestamp() * 1000)

        print(f"데이터 수집 시작: {start_date} ~ {end_date}")
        print(f"심볼: {self.symbol}, 타임프레임: {self.timeframe}")

        all_data = []
        current_ts = start_ts
        batch_count = 0

        # 배치 단위로 데이터 수집 (한 번에 최대 1000개)
        while current_ts < end_ts:
            try:
                # 1000개 캔들 수집
                df = self.fetch_ohlcv(since=current_ts, limit=1000)

                if df.empty:
                    print("더 이상 데이터 없음")
                    break

                all_data.append(df)
                batch_count += 1

                # 다음 배치 타임스탬프 계산
                last_timestamp = df['timestamp'].iloc[-1]
                current_ts = int(last_timestamp.timestamp() * 1000) + 60000  # +1분

                # 진행 상황 출력
                if batch_count % 10 == 0:
                    print(f"{batch_count}개 배치 완료, 마지막: {last_timestamp}")

                # API 요청 제한 방지
                time.sleep(0.5)

                # 종료 시간 도달 확인
                if current_ts >= end_ts:
                    break

            except Exception as e:
                print(f"배치 {batch_count} 오류: {e}")
                time.sleep(2)
                continue

        if not all_data:
            raise ValueError("수집된 데이터 없음")

        # 모든 배치 결합
        combined_df = pd.concat(all_data, ignore_index=True)

        # 중복 제거 및 정렬
        combined_df = combined_df.drop_duplicates(subset=['timestamp'])
        combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)

        # 종료 날짜 이후 데이터 제거 (end_date 23:59:59까지만 포함)
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        combined_df = combined_df[combined_df['timestamp'] <= end_datetime]
        combined_df = combined_df.reset_index(drop=True)

        print(f"\n총 {len(combined_df):,}개 캔들 수집 완료")
        print(f"기간: {combined_df['timestamp'].min()} ~ {combined_df['timestamp'].max()}")

        return combined_df

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        데이터 유효성 검증

        검증 항목:
            1. 빈 데이터 확인
            2. 필수 컬럼 존재 확인
            3. NULL 값 확인
            4. 가격 데이터 범위 확인 (양수)
            5. OHLC 논리 확인 (고가 >= 저가 등)
            6. 중복 타임스탬프 확인

        매개변수:
            df: 검증할 데이터프레임

        반환값:
            유효하면 True, 아니면 False
        """
        # 빈 데이터 확인
        if df.empty:
            print("검증 실패: 빈 데이터")
            return False

        # 필수 컬럼 확인
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            print(f"검증 실패: 필수 컬럼 누락")
            return False

        # NULL 값 확인
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            print(f"검증 경고: NULL 값 발견\n{null_counts[null_counts > 0]}")

        # 가격 양수 확인
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if (df[col] <= 0).any():
                print(f"검증 실패: {col}에 0 이하 값 존재")
                return False

        # OHLC 논리 검증
        invalid_high = (df['high'] < df['low']) | (df['high'] < df['open']) | (df['high'] < df['close'])
        invalid_low = (df['low'] > df['open']) | (df['low'] > df['close'])

        if invalid_high.any() or invalid_low.any():
            total_invalid = invalid_high.sum() + invalid_low.sum()
            print(f"검증 경고: {total_invalid}개 캔들에서 OHLC 오류")

        # 중복 타임스탬프 확인
        duplicates = df.duplicated(subset=['timestamp']).sum()
        if duplicates > 0:
            print(f"검증 경고: {duplicates}개 중복 타임스탬프")

        print("검증 완료: 데이터 정상")
        return True

