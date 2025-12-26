# 암호화폐 데이터 수집 파이프라인 🚀

바이낸스 거래소에서 암호화폐 OHLCV 데이터를 수집하고 기술 지표를 계산하는 파이프라인

## 📋 주요 기능

- **실시간 데이터 수집**: 바이낸스 API를 통한 암호화폐 가격 데이터 수집
- **월 단위 저장**: 분봉 데이터를 월 단위로 CSV 및 Parquet 형식으로 저장
- **기술 지표 계산**: EMA, MACD, RSI, 볼린저 밴드 등 주요 기술 지표 자동 계산
- **데이터 검증**: 수집된 데이터의 무결성 자동 검증
- **UTC 타임존**: 모든 타임스탬프는 UTC 기준 (한국시간 = UTC+9)

## 🛠️ 설치 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 필수 라이브러리

- ccxt >= 4.0.0 (바이낸스 API 연동)
- pandas >= 2.0.0 (데이터 처리)
- numpy >= 1.24.0 (수치 계산)
- pyarrow >= 22.0.0 (Parquet 파일 저장)

## 🚀 사용 방법

### 바이낸스 연결 테스트

```bash
python scripts/test_binance_connection.py
```

### 월 단위 데이터 저장

```bash
python scripts/monthly_data_saver.py
```

### 전체 과거 데이터 저장

```bash
python scripts/save_all_historical_data.py
```

옵션:
1. 전체 과거 데이터 (2017년 8월 ~ 현재)
2. 최근 1년
3. 최근 2년
4. 특정 기간 지정

### 저장된 데이터 확인

```bash
python scripts/check_saved_data.py
```

### 파이프라인 실행 (데이터 수집 + 기술지표 계산)

```bash
# 기본 사용 (2017-01-01 ~ 현재)
python src/pipeline.py

# 특정 기간 지정
python src/pipeline.py --start-date 2024-01-01 --end-date 2024-12-31

# 출력 파일 지정
python src/pipeline.py --output my_data.csv

# 다른 거래쌍 및 타임프레임
python src/pipeline.py --symbol ETH/USDT --timeframe 5m
```

## 📂 프로젝트 구조

```
crypto-data-pipeline/
├── src/
│   ├── data_collector.py      # 바이낸스 데이터 수집기
│   ├── indicators.py           # 기술 지표 계산
│   └── pipeline.py             # 전체 파이프라인
├── data/
│   ├── csv/                    # CSV 파일 저장 위치
│   └── parquet/                # Parquet 파일 저장 위치
├── monthly_data_saver.py       # 월 단위 데이터 저장
├── save_all_historical_data.py # 전체 과거 데이터 저장
├── check_saved_data.py         # 저장된 데이터 확인
├── test_binance_connection.py  # API 연결 테스트
└── requirements.txt            # 필수 패키지 목록
```

## 📊 데이터 형식

### OHLCV 컬럼
- `timestamp`: 시간 (UTC, 타임존 제거)
- `open`: 시가
- `high`: 고가
- `low`: 저가
- `close`: 종가
- `volume`: 거래량

### 기술 지표 컬럼
- `ema_12`, `ema_26`, `ema_50`, `ema_200`: 지수 이동 평균
- `macd`, `macd_signal`, `macd_histogram`: MACD 지표
- `rsi`: 상대 강도 지수
- `bb_upper`, `bb_middle`, `bb_lower`: 볼린저 밴드

## ⚠️ 중요 사항

### 타임존 정보
- **모든 타임스탬프는 UTC 기준**으로 저장됩니다
- 한국 시간으로 변환 필요시: `timestamp + 9시간 = KST`
- 예시: `2024-12-01 00:00:00 (UTC) = 2024-12-01 09:00:00 (KST)`

### 월 단위 데이터
- 월 시작: 매월 1일 00:00:00 UTC
- 월 종료: 매월 마지막 날 23:59:59 UTC
- 파일명 형식: `BTC_USDT_YYYY_MM_1m.csv` (또는 .parquet)
- 완전한 월 데이터: 31일 × 24시간 × 60분 = 44,640개 캔들

### 데이터 압축
- CSV: 원본 데이터 (약 2.8 MB/월)
- Parquet: Snappy 압축 (약 1.85 MB/월, 약 34% 압축)

### 데이터 압축
- CSV: 원본 데이터 (약 2.5 MB/월)
- Parquet: Snappy 압축 (약 1.4 MB/월, 약 45% 압축)

## 💡 예제

### 특정 월 데이터 수집

```python
from monthly_data_saver import MonthlyDataSaver

# 저장 객체 생성
saver = MonthlyDataSaver(symbol='BTC/USDT', timeframe='1m')

# 2024년 12월 데이터 저장
saver.save_month_data(year=2024, month=12)

# 여러 월 한번에 저장
saver.save_multiple_months(
    start_year=2024, start_month=1,
    end_year=2024, end_month=12
)
```

### 데이터 불러오기

```python
import pandas as pd

# CSV 불러오기
df = pd.read_csv('data/csv/BTC_USDT_2024_12_1m.csv')

# Parquet 불러오기 (더 빠름)
df = pd.read_parquet('data/parquet/BTC_USDT_2024_12_1m.parquet')

# 타임스탬프를 datetime으로 변환
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 한국 시간으로 변환 (필요시)
df['timestamp_kst'] = df['timestamp'] + pd.Timedelta(hours=9)

# 또는 타임존 명시
df['timestamp_utc'] = df['timestamp'].dt.tz_localize('UTC')
df['timestamp_kst'] = df['timestamp_utc'].dt.tz_convert('Asia/Seoul')
```

## 🔧 문제 해결

### API 연결 오류
1. 인터넷 연결 확인
2. 방화벽 설정 확인
3. 바이낸스 서버 상태 확인

### 데이터 수집 오류
1. `test_binance_connection.py`로 연결 확인
2. API 요청 제한 확인 (자동으로 처리됨)
3. 날짜 형식 확인 (YYYY-MM-DD)

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 자유롭게 사용할 수 있습니다.

## 🤝 기여

버그 리포트나 기능 제안은 언제든지 환영합니다!

---

**⚡ 빠른 시작**

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 연결 테스트
python scripts/test_binance_connection.py

# 3. 데이터 수집
python scripts/monthly_data_saver.py
```

**즐거운 트레이딩 되세요! 🚀📈**

