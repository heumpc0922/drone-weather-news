
# 드론 운용 기상정보 뉴스 - OpenAI 기사 초안 생성
# Fact Sheet에 있는 검증된 사실만 사용합니다.
# AI 결과는 사람이 검수하기 전까지 공개하지 않습니다.

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 1. 현재 파일이 있는 폴더를 확인합니다.
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 같은 폴더의 .env에서 API 키를 읽습니다.
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key == "여기에_본인의_OpenAI_API_키":
    raise SystemExit(
        "OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요."
    )

# 3. Fact Sheet JSON 파일을 읽습니다.
fact_path = BASE_DIR / "data" / "processed" / "01_drone_weather_fact_sheet.json"

with open(fact_path, "r", encoding="utf-8") as f:
    facts = json.load(f)

# 4. OpenAI에 전달할 기사 작성 규칙입니다.
instructions = """
당신은 데이터 저널리즘을 담당하는 한국어 뉴스 기자입니다.

다음 규칙을 반드시 지키세요.

1. 제공된 Fact Sheet에 확인된 사실만 기사에 사용하세요.
2. 숫자, 날짜, 단위, 관측지점, 출처를 정확하게 표시하세요.
3. 제목 1개, 리드 2문장, 본문 3문단, 출처와 한계 순서로 작성하세요.
4. 기상청 서울 ASOS 108번 지점의 지상 관측자료임을 명확히 밝히세요.
5. 평균 풍속, 최대 풍속, 5m/s 초과 횟수를 구분하세요.
6. 강수량 결측값을 비가 오지 않았다는 의미로 해석하지 마세요.
7. 관측된 5m/s 초과 횟수는 연구용 분류 기준이며
   드론 비행 허가나 법적 제한 기준이 아님을 명시하세요.
8. 기상 관측자료만으로 실제 드론 비행 가능 여부를 단정하지 마세요.
9. 사고 발생, 원인, 정책 변화, 장기 추세를 근거 없이 만들지 마세요.
10. 이 기사는 사람이 검수해야 하는 'AI 생성 초안'입니다.
"""

# 5. AI에 보낼 Fact Sheet를 JSON 문자열로 만듭니다.
fact_text = json.dumps(
    facts,
    ensure_ascii=False,
    indent=2,
)

# 6. OpenAI API를 호출합니다. 여기서 비용이 발생할 수 있습니다.
client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-5-mini",
    instructions=instructions,
    input=(
        "다음 Fact Sheet만 근거로 드론 운용 기상정보 "
        "뉴스 초안을 한국어로 작성하세요.\n\n"
        + fact_text
    ),
    max_output_tokens=1800,
)

# 7. AI가 작성한 결과를 가져옵니다.
article = response.output_text

if not article or not article.strip():
    raise SystemExit("AI 응답에 기사 내용이 없습니다.")

# 8. 기사 초안을 TXT 파일로 저장합니다.
output_path = BASE_DIR / "articles" / "04_ai_news_draft.txt"

output_path.write_text(
    article,
    encoding="utf-8",
)

print("=== OpenAI 뉴스 생성 결과 ===")
print("모델:", response.model)
print("저장 파일:", output_path.name)
print("AI 뉴스 초안 생성 성공!")
print("주의: 사람의 검수가 끝나기 전에는 공개하지 마세요.")
