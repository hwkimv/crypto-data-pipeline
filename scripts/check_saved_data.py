"""
저장된 데이터 확인

월 단위로 저장된 parquet 및 csv 파일을 읽어서 확인
"""

import pandas as pd
from pathlib import Path


def check_saved_data():
    """저장된 데이터 확인"""

    print("=" * 80)
    print("💾 저장된 데이터 확인")
    print("=" * 80)

    # CSV 파일
    csv_file = Path('data/csv/BTC_USDT_2024_12_1m.csv')
    if csv_file.exists():
        print(f"\n📄 CSV: {csv_file}")
        df_csv = pd.read_csv(csv_file)
        df_csv['timestamp'] = pd.to_datetime(df_csv['timestamp'])

        print(f"  - 행: {len(df_csv):,}개")
        print(f"  - 크기: {csv_file.stat().st_size / (1024*1024):.2f} MB")
        print(f"  - 컬럼: {list(df_csv.columns)}")
        print(f"\n  최근 5개:")
        print(df_csv.tail(5).to_string(index=False))
    else:
        print(f"\n⚠️  CSV 파일 없음: {csv_file}")

    # Parquet 파일
    parquet_file = project_root / 'data/parquet/BTC_USDT_2024_12_1m.parquet'
    if parquet_file.exists():
        print(f"\n\n📦 Parquet: {parquet_file}")
        df_parquet = pd.read_parquet(parquet_file)

        print(f"  - 행: {len(df_parquet):,}개")
        print(f"  - 크기: {parquet_file.stat().st_size / (1024*1024):.2f} MB")
        print(f"  - 압축률: {(1 - parquet_file.stat().st_size / csv_file.stat().st_size) * 100:.1f}% 절감")
        print(f"  - 컬럼: {list(df_parquet.columns)}")
        print(f"\n  최근 5개:")
        print(df_parquet.tail(5).to_string(index=False))
    else:
        print(f"\n⚠️  Parquet 파일 없음: {parquet_file}")

    # 무결성 확인
    if csv_file.exists() and parquet_file.exists():
        print("\n\n🔍 데이터 무결성:")
        print(f"  CSV 행: {len(df_csv):,}")
        print(f"  Parquet 행: {len(df_parquet):,}")

        if len(df_csv) == len(df_parquet):
            print("  ✓ 행 수 일치")
        else:
            print("  ❌ 행 수 불일치!")

        # 가격 비교
        if df_csv['close'].iloc[-1] == df_parquet['close'].iloc[-1]:
            print("  ✓ 마지막 종가 일치")
        else:
            print("  ❌ 마지막 종가 불일치!")

    print("\n" + "=" * 80)
    print("✅ 확인 완료!")
    print("=" * 80)

    # 통계
    print("\n📊 2024년 12월 BTC/USDT:")
    print(f"  시작: {df_parquet['timestamp'].min()} (UTC)")
    print(f"  종료: {df_parquet['timestamp'].max()} (UTC)")
    print(f"  기간: {(df_parquet['timestamp'].max() - df_parquet['timestamp'].min()).days}일")
    print(f"  최고가: ${df_parquet['high'].max():,.2f}")
    print(f"  최저가: ${df_parquet['low'].min():,.2f}")
    print(f"  시작가: ${df_parquet['open'].iloc[0]:,.2f}")
    print(f"  종료가: ${df_parquet['close'].iloc[-1]:,.2f}")
    print(f"  변화율: {((df_parquet['close'].iloc[-1] / df_parquet['open'].iloc[0] - 1) * 100):+.2f}%")
    print(f"  총 거래량: {df_parquet['volume'].sum():,.2f} BTC")
    print(f"  평균 거래량: {df_parquet['volume'].mean():,.2f} BTC/분")


if __name__ == "__main__":
    check_saved_data()

