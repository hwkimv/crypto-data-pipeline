"""
비트코인 전체 과거 데이터 저장

바이낸스 BTC/USDT 상장일(2017년 8월)부터 현재까지 모든 1분봉 데이터를 월 단위로 저장
"""

import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.monthly_data_saver import MonthlyDataSaver


def save_all_btc_history():
    """
    BTC/USDT 전체 과거 데이터를 월 단위로 저장

    바이낸스 BTC/USDT는 2017년 8월부터 거래가 시작되었습니다.
    현재(2025년 12월)까지 모든 데이터를 저장합니다.
    """

    print("=" * 80)
    print("🚀 비트코인 전체 과거 데이터 저장 시작")
    print("=" * 80)
    print("")
    print("📅 저장 기간: 2017년 8월 ~ 2025년 12월")
    print("💰 심볼: BTC/USDT")
    print("⏱️  타임프레임: 1분봉")
    print("💾 저장 형식: CSV + Parquet")
    print("")
    print("⚠️  주의: 전체 기간 데이터 수집에는 상당한 시간이 소요됩니다.")
    print("   (약 100개월 × 평균 43,000개 캔들 = 약 430만개 데이터)")
    print("")

    # 사용자 확인
    response = input("계속 진행하시겠습니까? (y/n): ").lower().strip()
    if response != 'y':
        print("\n작업이 취소되었습니다.")
        return

    # 데이터 저장 객체 생성
    saver = MonthlyDataSaver(
        symbol='BTC/USDT',
        timeframe='1m',
        data_dir='data'
    )

    # 바이낸스 BTC/USDT 상장일: 2017년 8월
    start_year = 2017
    start_month = 8

    # 현재 날짜
    now = datetime.now()
    end_year = now.year
    end_month = now.month

    print(f"\n📊 총 저장 기간: {start_year}년 {start_month}월 ~ {end_year}년 {end_month}월")

    # 총 월 수 계산
    total_months = (end_year - start_year) * 12 + (end_month - start_month) + 1
    print(f"📈 총 저장할 월: {total_months}개월")
    print("")

    # 시작 시간 기록
    start_time = datetime.now()

    # 전체 기간 데이터 저장
    saver.save_multiple_months(
        start_year=start_year,
        start_month=start_month,
        end_year=end_year,
        end_month=end_month,
        save_csv=True,
        save_parquet=True
    )

    # 소요 시간 계산
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 80)
    print("🎉 전체 데이터 저장 완료!")
    print("=" * 80)
    print(f"⏱️  소요 시간: {duration}")
    print(f"📁 저장 위치: data/csv/ 및 data/parquet/")
    print("")
    print("💡 저장된 데이터 확인:")
    print("   python check_saved_data.py")
    print("")


def save_recent_years(years: int = 1):
    """
    최근 N년 데이터만 저장 (빠른 테스트용)

    매개변수:
        years: 저장할 년 수 (기본: 1년)
    """

    print("=" * 80)
    print(f"📅 최근 {years}년 데이터 저장")
    print("=" * 80)

    saver = MonthlyDataSaver(symbol='BTC/USDT', timeframe='1m')

    now = datetime.now()
    end_year = now.year
    end_month = now.month

    # 시작 날짜 계산
    start_year = end_year - years
    start_month = end_month

    # 월 음수 처리
    if start_month <= 0:
        start_month += 12
        start_year -= 1

    print(f"\n기간: {start_year}년 {start_month}월 ~ {end_year}년 {end_month}월")
    print("")

    saver.save_multiple_months(
        start_year=start_year,
        start_month=start_month,
        end_year=end_year,
        end_month=end_month,
        save_csv=True,
        save_parquet=True
    )


def main():
    """메인 실행 함수"""

    print("\n" + "🔥" * 40)
    print("비트코인 전체 과거 데이터 저장")
    print("🔥" * 40 + "\n")

    print("옵션 선택:")
    print("  1. 전체 과거 데이터 (2017년 8월 ~ 현재)")
    print("  2. 최근 1년")
    print("  3. 최근 2년")
    print("  4. 특정 기간")
    print("")

    choice = input("선택 (1-4): ").strip()

    if choice == '1':
        save_all_btc_history()
    elif choice == '2':
        save_recent_years(years=1)
    elif choice == '3':
        save_recent_years(years=2)
    elif choice == '4':
        print("\n특정 기간 설정:")
        start_year = int(input("  시작 연도: "))
        start_month = int(input("  시작 월 (1-12): "))
        end_year = int(input("  종료 연도: "))
        end_month = int(input("  종료 월 (1-12): "))

        saver = MonthlyDataSaver(symbol='BTC/USDT', timeframe='1m')
        saver.save_multiple_months(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
            save_csv=True,
            save_parquet=True
        )
    else:
        print("❌ 잘못된 선택")


if __name__ == "__main__":
    main()

