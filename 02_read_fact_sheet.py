
# Fact Sheet JSON을 읽는 연습 프로그램
# 검증된 기상자료를 화면에 출력합니다.

import json
from pathlib import Path

# 현재 Python 파일과 같은 폴더에서 JSON을 찾습니다.
file_path = Path(__file__).with_name(
    "01_drone_weather_fact_sheet.json"
)

# UTF-8로 파일을 열어 데이터를 읽습니다.
with open(file_path, "r", encoding="utf-8") as file:
    facts = json.load(file)

# JSON 안에서 필요한 정보를 꺼냅니다.
station = facts["data_source"]["station_name"]
start = facts["observation_period"]["start"]
end = facts["observation_period"]["end"]

verified = facts["verified_facts"]

print("=== 드론 운용 기상정보 Fact Sheet ===")
print("관측지점:", station)
print("시작 시각:", start)
print("종료 시각:", end)
print("관측자료:", verified["observation_count"], "건")
print("평균 풍속:", verified["average_wind_speed_ms"], "m/s")
print("최대 풍속:", verified["maximum_wind_speed_ms"], "m/s")
print("5m/s 초과:", verified["wind_speed_over_5ms_count"], "건")
print("강수량 결측:", verified["precipitation_missing_count"], "건")
