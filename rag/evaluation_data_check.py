import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

csv_path = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "OBS_ASOS_TIM_20261019111228.csv"
)

df = pd.read_csv(csv_path, encoding="cp949")

wind = pd.to_numeric(df["풍속(m/s)"], errors="coerce")

print("=" * 45)
print("5차 자동 팩트체킹 - 드론 기상뉴스")
print("=" * 45)

print("\n[1] 데이터 기본 정보")
print("전체 행:", df.shape[0])
print("전체 열:", df.shape[1])

print("\n[2] 열별 결측치")
print(df.isna().sum().to_string())

print("\n[3] 풍속 계산")
print("평균 풍속:", round(wind.mean(), 2), "m/s")
print("최대 풍속:", wind.max(), "m/s")
print("5m/s 초과:", (wind > 5).sum(), "건")

import json

print("\n[4] 사실표 자동 검증")

fact_path = (
    PROJECT_DIR
    / "rag"
    / "fact_sheet"
    / "drone_weather_safety_facts.json"
)

with open(fact_path, "r", encoding="utf-8") as file:
    facts = json.load(file)["facts"]

fact_values = {
    fact["fact_id"]: fact["value"]
    for fact in facts
    if fact["fact_id"] in ["F-1", "F-2", "F-3"]
}

calculated_values = {
    "F-1": round(float(wind.mean()), 2),
    "F-2": float(wind.max()),
    "F-3": int((wind > 5).sum())
}

for fact_id, calculated in calculated_values.items():
    recorded = fact_values.get(fact_id)

    if recorded == calculated:
        print(f"{fact_id}: 일치 ✅ (계산값: {calculated}, 사실표: {recorded})")
    else:
        print(f"{fact_id}: 불일치 ❌ (계산값: {calculated}, 사실표: {recorded})")

print("\n주의: 5m/s는 교육용 분석 기준입니다.")
print("강수량 결측치는 무강수를 의미하지 않습니다.")