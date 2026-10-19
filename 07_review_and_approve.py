
# AI 뉴스 기사 - 사람의 승인/보류 기록 프로그램
# 승인하지 않은 기사는 공개용으로 사용하지 않습니다.

import json
from datetime import datetime
from pathlib import Path

# 현재 Python 파일이 저장된 폴더
BASE_DIR = Path(__file__).resolve().parent

# 사람이 수정한 기사 파일
article_path = BASE_DIR / "06_revised_drone_weather_article.txt"

# 승인 결과를 저장할 파일
result_path = BASE_DIR / "08_article_approval.json"

# 수정된 기사가 존재하는지 확인
if not article_path.exists():
    raise SystemExit("수정 기사 파일이 없습니다.")

article = article_path.read_text(encoding="utf-8")

if not article.strip():
    raise SystemExit("수정 기사 내용이 비어 있습니다.")

print("=== 드론 기상정보 뉴스 기사 검수 ===")
print("수정 기사:", article_path.name)
print("기사 글자 수:", len(article))
print()
print("1. 승인")
print("2. 보류")

# 사람이 직접 결정
choice = input("검수 결과를 선택하세요 (1 또는 2): ").strip()

if choice == "1":
    status = "approved"
    status_ko = "승인"
elif choice == "2":
    status = "on_hold"
    status_ko = "보류"
else:
    raise SystemExit("잘못된 입력입니다. 1 또는 2를 입력하세요.")

# 누가, 언제, 어떤 결정을 내렸는지 기록
reviewer = input("검수자 이름 또는 별명: ").strip()

if not reviewer:
    raise SystemExit("검수자를 입력해야 합니다.")

comment = input("검수 의견을 입력하세요: ").strip()

if not comment:
    raise SystemExit("검수 의견을 입력해야 합니다.")

result = {
    "project": "드론 운용 기상정보 뉴스",
    "article_file": article_path.name,
    "reviewer": reviewer,
    "reviewed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "status": status,
    "status_ko": status_ko,
    "comment": comment,
    "published": False
}

# 승인 기록을 JSON 파일로 저장
result_path.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print()
print("=== 검수 결과 저장 완료 ===")
print("검수 결과:", status_ko)
print("저장 파일:", result_path.name)
print("공개 여부: 미공개")
