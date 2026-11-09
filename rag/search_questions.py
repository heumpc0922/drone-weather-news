import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FACT_FILE = BASE_DIR / "fact_sheet" / "drone_weather_safety_facts.json"

with open(FACT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

facts = data["facts"]

# 질문에서 찾을 핵심 단어와 사실ID 연결
keywords = {
    "F-1": ["평균 풍속", "평균 바람"],
    "F-2": ["최대 풍속", "가장 강한 바람"],
    "F-3": ["5m/s 초과", "5m/s 넘"],
    "F-4": ["육안", "눈으로 확인", "가시거리"],
    "F-5": ["DJI", "Mini 4 Pro", "강풍", "악천후"],
    "F-6": ["비행승인", "비행금지구역", "관제권", "150m"]
}

print("=== 드론 기상안전 자연어 검색 ===")

question = input("질문을 입력하세요: ").strip().lower()

matched_ids = []

for fact_id, words in keywords.items():
    if any(word.lower() in question for word in words):
        matched_ids.append(fact_id)

if matched_ids:
    for fact in facts:
        if fact["fact_id"] in matched_ids:
            print("\n[검색 결과]")
            print("사실ID:", fact["fact_id"])
            print("내용:", fact["claim"])
            print("출처:", fact["source"])
            print("근거 파일:", fact["source_file"])
            if "source_page" in fact:
                print("근거 페이지:", fact["source_page"])
else:
    print("\n제공된 자료로는 확인할 수 없습니다.")