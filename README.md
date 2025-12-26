# crypto-data-pipeline
바이낸스 비트코인 차트 데이터 수집 & 지표

## 개요 (Overview)

바이낸스에서 BTC/USDT 1분봉 전체 과거 데이터를 수집하고 AI 트레이딩용 기술 지표를 계산하는 Python 파이프라인입니다.

A Python pipeline to collect complete historical BTC/USDT 1-minute candle data from Binance and calculate technical indicators for AI trading.

## 주요 기능 (Features)

1. **데이터 수집 (Data Collection)**
   - ccxt 라이브러리를 사용하여 바이낸스에서 BTC/USDT 1분봉 데이터 수집
   - 2017년부터 현재까지의 전체 과거 데이터 지원
   - 대용량 데이터 처리 및 검증

2. **기술 지표 계산 (Technical Indicators)**
   - MACD (Moving Average Convergence Divergence)
   - RSI (Relative Strength Index)
   - EMA (Exponential Moving Average): 12, 26, 50, 200
   - 볼린저 밴드 (Bollinger Bands)

3. **데이터 저장 (Data Storage)**
   - OHLCV + 기술 지표를 CSV 파일로 저장
   - Parquet 형식 지원 (압축률 34% 절감, 빠른 읽기/쓰기)
   - 월 단위 자동 데이터 저장 기능
   - 타임스탬프, 가격, 거래량, 모든 지표 포함

## 설치 (Installation)

```bash
# Clone the repository
git clone https://github.com/hwkimv/crypto-data-pipeline.git
cd crypto-data-pipeline

# Install dependencies
pip install -r requirements.txt
```

## 사용법 (Usage)

### 기본 실행 (Basic Usage)

```bash
# 바이낸스 연결 테스트
python test_binance_connection.py

# 월 단위 데이터 저장 (2024년 12월)
python monthly_data_saver.py

# 전체 과거 데이터 수집 (2017-01-01부터 현재까지)
python src/pipeline.py

# 특정 기간 데이터 수집
python src/pipeline.py --start-date 2024-01-01 --end-date 2024-12-31

# 출력 파일명 지정
python src/pipeline.py --output my_btc_data.csv

# 저장된 데이터 확인
python check_saved_data.py
```

### 고급 옵션 (Advanced Options)

```bash
# 다른 심볼과 타임프레임 사용
python src/pipeline.py --symbol ETH/USDT --timeframe 5m

# 모든 옵션 함께 사용
python src/pipeline.py \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --output btc_2024.csv \
  --symbol BTC/USDT \
  --timeframe 1m
```

### Python 코드에서 사용 (Using in Python Code)

#### 1. 월 단위 데이터 저장

```python
from monthly_data_saver import MonthlyDataSaver

# 데이터 저장 객체 생성
saver = MonthlyDataSaver(
    symbol='BTC/USDT',
    timeframe='1m',
    data_dir='data'
)

# 2024년 12월 데이터 저장
saver.save_month_data(
    year=2024,
    month=12,
    save_csv=True,      # CSV 저장
    save_parquet=True   # Parquet 저장
)

# 여러 월 데이터 한 번에 저장 (2024년 10월~12월)
saver.save_multiple_months(
    start_year=2024, start_month=10,
    end_year=2024, end_month=12,
    save_csv=True,
    save_parquet=True
)
```

#### 2. 전체 파이프라인 실행

```python
from src.pipeline import CryptoDataPipeline

# 파이프라인 생성
pipeline = CryptoDataPipeline(symbol='BTC/USDT', timeframe='1m')

# 파이프라인 실행
df = pipeline.run(
    start_date='2024-01-01',
    end_date='2024-12-31',
    output_file='btc_data.csv'
)

# 데이터 확인
print(df.head())
print(df.columns)
```

#### 3. 저장된 데이터 읽기

```python
import pandas as pd

# CSV 파일 읽기
df_csv = pd.read_csv('data/csv/BTC_USDT_2024_12_1m.csv')
df_csv['timestamp'] = pd.to_datetime(df_csv['timestamp'])

# Parquet 파일 읽기 (더 빠르고 용량 효율적)
df_parquet = pd.read_parquet('data/parquet/BTC_USDT_2024_12_1m.parquet')

print(f"총 데이터: {len(df_parquet):,}개")
print(df_parquet.tail(5))
```

## 프로젝트 구조 (Project Structure)

```
crypto-data-pipeline/
├── src/
│   ├── __init__.py              # 패키지 초기화
│   ├── data_collector.py        # 바이낸스 데이터 수집 모듈
│   ├── indicators.py            # 기술 지표 계산
│   └── pipeline.py              # 메인 파이프라인 실행
├── data/
│   ├── csv/                     # CSV 형식 데이터 저장소
│   │   └── BTC_USDT_2024_12_1m.csv
│   └── parquet/                 # Parquet 형식 데이터 저장소
│       └── BTC_USDT_2024_12_1m.parquet
├── monthly_data_saver.py        # 월 단위 데이터 저장 스크립트
├── check_saved_data.py          # 저장된 데이터 확인 스크립트
├── test_binance_connection.py  # 바이낸스 연결 테스트
├── example_usage.py             # 사용 예제 모음
├── requirements.txt             # Python 의존성 패키지
├── .gitignore                   # Git 제외 규칙
└── README.md                    # 이 파일
```

## 출력 데이터 형식 (Output Data Format)

CSV 파일에는 다음 컬럼이 포함됩니다:

### OHLCV 데이터
- `timestamp`: 캔들 시간
- `open`: 시가
- `high`: 고가
- `low`: 저가
- `close`: 종가
- `volume`: 거래량

### 기술 지표
- `ema_12`, `ema_26`, `ema_50`, `ema_200`: EMA 지표
- `macd`: MACD 라인
- `macd_signal`: MACD 시그널 라인
- `macd_histogram`: MACD 히스토그램
- `rsi`: RSI 지표
- `bb_upper`: 볼린저 밴드 상단
- `bb_middle`: 볼린저 밴드 중간 (이동평균)
- `bb_lower`: 볼린저 밴드 하단

## 기술 스택 (Technology Stack)

- **Python 3.12+**
- **ccxt**: 암호화폐 거래소 API 라이브러리
- **pandas**: 데이터 처리 및 분석
- **numpy**: 수치 계산
- **pyarrow**: Parquet 파일 형식 지원 (빠르고 효율적인 데이터 저장)

## 데이터 검증 (Data Validation)

파이프라인은 다음 검증을 수행합니다:

1. **원본 데이터 검증**
   - 필수 컬럼 존재 확인
   - Null 값 검사
   - 가격 데이터 유효성 검증 (음수, 0 검사)
   - OHLC 관계 검증 (high >= low 등)
   - 중복 타임스탬프 검사

2. **지표 데이터 검증**
   - 모든 지표 계산 완료 확인
   - RSI 범위 검증 (0-100)
   - 볼린저 밴드 순서 검증
   - NaN 값 분석 및 리포트

## 주의사항 (Notes)

- API 요청 제한을 고려하여 적절한 딜레이가 포함되어 있습니다
- 대용량 데이터 수집 시 시간이 오래 걸릴 수 있습니다
- 인터넷 연결이 필요합니다
- 생성된 CSV 파일은 `.gitignore`에 포함되어 있습니다

## 라이선스 (License)

MIT License
