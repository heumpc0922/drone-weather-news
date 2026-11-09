import json
from pathlib import Path

# 현재 Python 파일을 기준으로 사실표 위치 지정
BASE_DIR = Path(__file__).resolve().parent
FACT_FILE = BASE_DIR / "fact_sheet" / "drone_weather_safety_facts.json"

# JSON 사실표 읽기
with open(FACT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

facts = data["facts"]

print("=== 드론 기상안전 사실표 검색 ===")

# 사실ID 입력받기
fact_id = input("검색할 사실ID를 입력하세요 (예: F-5): ").strip().upper()

# 사실ID 검색
result = next(
    (fact for fact in facts if fact["fact_id"] == fact_id),
    None
)

if result:
    print("\n[검색 결과]")
    print("사실ID:", result["fact_id"])
    print("내용:", result["claim"])
    print("출처:", result["source"])
    print("근거 파일:", result["source_file"])
    print("검증 상태:", result["verification"])

    if "source_page" in result:
        print("근거 페이지:", result["source_page"])

else:
    print("\n해당 사실ID를 찾을 수 없습니다.")
    print("제공된 자료로는 확인할 수 없습니다.")