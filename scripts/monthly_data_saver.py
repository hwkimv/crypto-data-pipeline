"""
월 단위 암호화폐 가격 데이터 저장 스크립트

바이낸스에서 분봉 데이터를 월 단위로 수집하여
parquet 및 csv 형식으로 저장합니다.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from src.data_collector import DataCollector


class MonthlyDataSaver:
    """월 단위 데이터 저장 관리자"""

    def __init__(self, symbol: str = 'BTC/USDT', timeframe: str = '1m', data_dir: str = None):
        """
        초기화

        매개변수:
            symbol: 거래쌍 (예: 'BTC/USDT')
            timeframe: 캔들 간격 (예: '1m' - 1분봉)
            data_dir: 데이터 저장 디렉토리 (기본: 프로젝트/data)
        """
        self.symbol = symbol
        self.timeframe = timeframe

        # data_dir이 없으면 프로젝트 루트의 data 폴더 사용
        if data_dir is None:
            data_dir = project_root / 'data'
        self.data_dir = Path(data_dir)
        self.collector = DataCollector(symbol=symbol, timeframe=timeframe)

        # 데이터 저장 디렉토리 생성
        self.parquet_dir = self.data_dir / 'parquet'
        self.csv_dir = self.data_dir / 'csv'
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        self.csv_dir.mkdir(parents=True, exist_ok=True)

    def get_month_range(self, year: int, month: int) -> tuple:
        """
        특정 월의 시작일과 종료일을 반환

        매개변수:
            year: 연도
            month: 월 (1-12)

        반환값:
            (시작일, 종료일) 튜플
        """
        start_date = datetime(year, month, 1)

        # 다음 달 첫날을 구한 후 하루 빼기
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        return start_date, end_date

    def save_month_data(self, year: int, month: int, save_csv: bool = True, save_parquet: bool = True):
        """
        특정 월의 데이터를 수집하여 저장

        매개변수:
            year: 연도
            month: 월 (1-12)
            save_csv: CSV 파일로 저장 여부
            save_parquet: Parquet 파일로 저장 여부
        """
        # 월 범위 계산
        start_date, end_date = self.get_month_range(year, month)

        # 심볼에서 / 제거 (파일명용)
        symbol_safe = self.symbol.replace('/', '_')

        # 파일명 생성 (예: BTC_USDT_2024_01_1m)
        file_base = f"{symbol_safe}_{year}_{month:02d}_{self.timeframe}"

        print("=" * 80)
        print(f"📅 {year}년 {month}월 데이터 수집 시작")
        print("=" * 80)
        print(f"심볼: {self.symbol}")
        print(f"타임프레임: {self.timeframe}")
        print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        print("")

        try:
            # 데이터 수집
            print("바이낸스에서 데이터 수집 중...")
            df = self.collector.fetch_all_historical_data(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )

            if df.empty:
                print("⚠️  수집된 데이터가 없습니다")
                return None

            print(f"✓ 총 {len(df):,}개 캔들 수집 완료")

            # 데이터 검증
            print("\n데이터 검증 중...")
            if self.collector.validate_data(df):
                print("✓ 데이터 검증 완료")
            else:
                print("⚠️  데이터 검증 실패 (그래도 저장은 진행합니다)")

            # 통계
            print(f"\n📊 데이터 통계:")
            print(f"  - 시작: {df['timestamp'].min()} (UTC)")
            print(f"  - 종료: {df['timestamp'].max()} (UTC)")
            print(f"  - 최고가: ${df['high'].max():,.2f}")
            print(f"  - 최저가: ${df['low'].min():,.2f}")
            print(f"  - 평균 종가: ${df['close'].mean():,.2f}")
            print(f"  - 총 거래량: {df['volume'].sum():,.2f}")

            saved_files = []

            # CSV 저장
            if save_csv:
                csv_path = self.csv_dir / f"{file_base}.csv"
                print(f"\n💾 CSV 파일 저장 중: {csv_path}")
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                file_size_mb = csv_path.stat().st_size / (1024 * 1024)
                print(f"✓ CSV 저장 완료 (크기: {file_size_mb:.2f} MB)")
                saved_files.append(str(csv_path))

            # Parquet 저장
            if save_parquet:
                parquet_path = self.parquet_dir / f"{file_base}.parquet"
                print(f"\n💾 Parquet 파일 저장 중: {parquet_path}")
                df.to_parquet(parquet_path, index=False, compression='snappy')
                file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
                print(f"✓ Parquet 저장 완료 (크기: {file_size_mb:.2f} MB)")
                saved_files.append(str(parquet_path))

            print("\n" + "=" * 80)
            print(f"🎉 {year}년 {month}월 데이터 저장 완료!")
            print("=" * 80)

            return df

        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_multiple_months(self, start_year: int, start_month: int,
                           end_year: int, end_month: int,
                           save_csv: bool = True, save_parquet: bool = True):
        """
        여러 월 데이터 일괄 저장

        매개변수:
            start_year: 시작 연도
            start_month: 시작 월
            end_year: 종료 연도
            end_month: 종료 월
            save_csv: CSV 저장 여부
            save_parquet: Parquet 저장 여부
        """
        current_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1)

        success_count = 0
        fail_count = 0

        print("\n" + "🔄" * 40)
        print(f"여러 월 저장 시작: {start_year}/{start_month} ~ {end_year}/{end_month}")
        print("🔄" * 40 + "\n")

        while current_date <= end_date:
            result = self.save_month_data(
                current_date.year,
                current_date.month,
                save_csv=save_csv,
                save_parquet=save_parquet
            )

            if result is not None:
                success_count += 1
            else:
                fail_count += 1

            # 다음 달로
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)

            print("\n")

        print("\n" + "=" * 80)
        print("📊 전체 작업 완료")
        print("=" * 80)
        print(f"성공: {success_count}개월")
        print(f"실패: {fail_count}개월")
        print(f"위치: {self.data_dir.absolute()}")


def main():
    """메인 실행 함수"""

    print("=" * 80)
    print("월 단위 암호화폐 데이터 저장 프로그램")
    print("=" * 80)
    print("")

    # 설정
    symbol = 'BTC/USDT'
    timeframe = '1m'

    # 저장 객체 생성
    saver = MonthlyDataSaver(symbol=symbol, timeframe=timeframe, data_dir='data')

    # 예제: 2024년 12월 저장
    print("📌 2024년 12월 데이터 저장\n")
    saver.save_month_data(year=2024, month=12, save_csv=True, save_parquet=True)

    # 여러 월 저장 예제 (주석 해제하여 사용)
    # print("\n📌 2024년 10~12월 저장\n")
    # saver.save_multiple_months(
    #     start_year=2024, start_month=10,
    #     end_year=2024, end_month=12,
    #     save_csv=True, save_parquet=True
    # )


if __name__ == "__main__":
    main()

