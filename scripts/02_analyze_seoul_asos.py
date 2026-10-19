# 서울 ASOS 기상자료 분석 - 초보자용 실습
# 실행 전에 이 파일과 기상청 CSV 파일을 같은 폴더에 넣으세요.
import csv
from pathlib import Path
from datetime import datetime, timedelta

csv_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "OBS_ASOS_TIM_20261019111228.csv"

# 1. CSV 파일 읽기: 기상청 CSV는 보통 CP949(한국어 인코딩)입니다.
with csv_path.open("r", encoding="cp949", newline="") as file:
    rows = list(csv.DictReader(file))

# 2. 실제 관측 시각과 풍속을 꺼냅니다.
times = [datetime.strptime(row["일시"], "%Y-%m-%d %H:%M") for row in rows]
winds = [float(row["풍속(m/s)"]) for row in rows if row["풍속(m/s)"].strip()]
rain_texts = [row["강수량(mm)"].strip() for row in rows]
recorded_rain = [float(x) for x in rain_texts if x]

# 3. 빈 시간 기록이 있는지 확인합니다.
expected = []
current = min(times)
while current <= max(times):
    expected.append(current)
    current += timedelta(hours=1)
missing_times = sorted(set(expected) - set(times))

# 4. 계산 결과를 화면에 출력합니다.
print("=== 서울 ASOS 7일 관측자료 검사 ===")
print("관측 기록:", len(rows), "건")
print("시작 시각:", min(times))
print("종료 시각:", max(times))
print("누락된 시간:", len(missing_times), "건")
print("평균 풍속:", round(sum(winds) / len(winds), 2), "m/s")
print("최대 풍속:", max(winds), "m/s")
print("풍속 5m/s 초과:", sum(w > 5 for w in winds), "건")
print("강수량 빈칸:", sum(x == "" for x in rain_texts), "건")
print("강수량 숫자 기록:", len(recorded_rain), "건")
print("기록된 시간 강수량 합계:", round(sum(recorded_rain), 1), "mm")
print("주의: 강수량 빈칸을 0으로 바꾸지 않았습니다.")
print("주의: 풍속 기준은 교육용 분석 기준이며 드론 비행 허가 기준이 아닙니다.")
