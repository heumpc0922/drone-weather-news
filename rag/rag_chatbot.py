import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

load_dotenv(PROJECT_DIR / ".env")

fact_path = BASE_DIR / "fact_sheet" / "drone_weather_safety_facts.json"

with open(fact_path, "r", encoding="utf-8") as file:
    facts = json.load(file)["facts"]

# 질문과 사실표를 연결하는 검색 규칙
keywords = {
    "F-1": ["평균 풍속", "평균 바람"],
    "F-2": ["최대 풍속", "가장 강한 바람"],
    "F-3": ["5m/s 초과", "5m/s 넘"],
    "F-4": ["육안", "눈으로 확인", "가시거리"],
    "F-5": ["dji", "mini 4 pro", "강풍", "악천후"],
    "F-6": ["비행승인", "비행금지구역", "관제권", "150m"]
}

question = input("드론 관련 질문을 입력하세요: ").strip()

matched_ids = [
    fact_id
    for fact_id, words in keywords.items()
    if any(word in question.lower() for word in words)
]

matched_facts = [
    fact for fact in facts
    if fact["fact_id"] in matched_ids
]

if not matched_facts:
    print("\n제공된 자료로는 확인할 수 없습니다.")

elif not os.getenv("OPENAI_API_KEY"):
    print("\n오류: OPENAI_API_KEY가 설정되지 않았습니다.")

else:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    evidence = json.dumps(
        matched_facts,
        ensure_ascii=False,
        indent=2
    )

    instructions = """
당신은 드론 기상뉴스 팩트체킹 보조 AI입니다.

규칙:
1. 제공된 사실표에 있는 근거만 사용하세요.
2. 사실표에 없는 내용은 추측하지 마세요.
3. 답변마다 실제로 사용한 사실ID를 표시하세요.
4. 근거가 부족하면 '제공된 자료로는 확인할 수 없습니다'라고 답하세요.
5. 기상 관측자료만으로 실제 드론 비행 가능 여부를 판단하지 마세요.
6. 제조사 안전기준과 법적 비행 제한 기준을 혼동하지 마세요.
7. 답변은 초보자가 이해하기 쉽게 작성하세요.
"""

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=instructions,
            input=(
                f"질문:\n{question}\n\n"
                f"검색된 근거자료:\n{evidence}"
            ),
            max_output_tokens=2000
        )

        print("\n=== RAG 챗봇 답변 ===")
        print(response.output_text)
        print("\n=== API 응답 진단 ===")
        print("응답 상태:", response.status)
        print("미완료 사유:", response.incomplete_details)
        print("토큰 사용량:", response.usage)
        print("\n=== 검색된 근거ID ===")
        print(", ".join(matched_ids))

    except Exception as error:
        print("\nOpenAI API 호출 중 오류가 발생했습니다.")
        print("오류 유형:", type(error).__name__)
        print("오류 내용:", str(error))
    