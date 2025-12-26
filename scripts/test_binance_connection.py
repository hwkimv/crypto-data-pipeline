"""
바이낸스 API 연결 테스트

바이낸스 거래소와의 연결 확인 및 실시간 데이터 수집 테스트
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collector import DataCollector
import pandas as pd


def test_connection():
    """바이낸스 API 연결 테스트"""

    print("=" * 80)
    print("바이낸스 API 연결 테스트")
    print("=" * 80)

    try:
        # 1. 수집기 생성
        print("\n[1단계] 데이터 수집기 생성...")
        collector = DataCollector(symbol='BTC/USDT', timeframe='1m')
        print("✓ 생성 완료")

        # 2. 최근 10개 캔들 수집
        print("\n[2단계] 최근 10개 캔들 수집...")
        df = collector.fetch_ohlcv(limit=10)
        print("✓ 수집 완료")

        # 3. 데이터 확인
        print("\n[3단계] 수집 데이터 확인:")
        print(f"  - 캔들 수: {len(df)}개")
        print(f"  - 컬럼: {list(df.columns)}")
        print(f"  - 기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")

        print("\n최근 5개:")
        print(df.tail(5).to_string())

        # 4. 검증
        print("\n[4단계] 데이터 검증...")
        is_valid = collector.validate_data(df)

        if is_valid:
            print("\n" + "=" * 80)
            print("🎉 바이낸스 API 연결 성공!")
            print("=" * 80)

            # 최신 정보
            latest = df.iloc[-1]
            print(f"\n📊 BTC/USDT 최신 (1분봉):")
            print(f"  시간: {latest['timestamp']} (UTC)")
            print(f"  시가:   ${latest['open']:,.2f}")
            print(f"  고가:   ${latest['high']:,.2f}")
            print(f"  저가:   ${latest['low']:,.2f}")
            print(f"  종가:   ${latest['close']:,.2f}")
            print(f"  거래량: {latest['volume']:,.2f} BTC")

            return True
        else:
            print("\n⚠️ 검증 실패")
            return False

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        print("\n가능한 원인:")
        print("  1. 인터넷 연결 확인")
        print("  2. 바이낸스 서버 상태")
        print("  3. 방화벽 설정")
        return False


def test_historical_data():
    """과거 데이터 수집 테스트 (1시간)"""

    print("\n\n" + "=" * 80)
    print("과거 데이터 수집 테스트 (최근 1시간)")
    print("=" * 80)

    try:
        from datetime import datetime, timedelta

        # 최근 1시간
        collector = DataCollector(symbol='BTC/USDT', timeframe='1m')

        end_date = datetime.now()
        start_date = end_date - timedelta(hours=1)

        print(f"\n기간: {start_date.strftime('%Y-%m-%d %H:%M')} ~ {end_date.strftime('%Y-%m-%d %H:%M')}")

        df = collector.fetch_all_historical_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        print(f"\n✓ {len(df)}개 캔들 수집 완료")
        print(f"  기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")

        # 통계
        print(f"\n📈 가격 통계:")
        print(f"  최고가: ${df['high'].max():,.2f}")
        print(f"  최저가: ${df['low'].min():,.2f}")
        print(f"  평균가: ${df['close'].mean():,.2f}")
        print(f"  현재가: ${df['close'].iloc[-1]:,.2f}")

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False


if __name__ == "__main__":
    # 기본 연결 테스트
    success = test_connection()

    # 연결 성공 시 과거 데이터 테스트
    if success:
        test_historical_data()

    print("\n\n테스트 완료!")

