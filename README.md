# 드론 운용 기상정보 뉴스

서울 ASOS 108 기상자료 분석·MySQL·AI 뉴스 생성과 사람 검수 교육용 프로젝트입니다.

- `docs/`: PRD, 기능정의서, 화면설계서, DB 설계서
- `scripts/`: Python 분석, MySQL 적재, OpenAI 기사 생성 및 승인 프로그램
- `database/`: MySQL SQL
- `data/raw/`: 기상청 원본 CSV; `data/processed/`: 검증 Fact Sheet
- `articles/`: 기사 초안, 검수 보고서, 수정 기사, 승인 기록
- `app/`: FastAPI 서버와 향후 웹 디자인
- `tests/`: 자동 테스트 예정

## 실행

1. `py -m pip install -r requirements.txt`
2. `.env.example`을 복사하여 로컬에 `.env`를 만들고 개인 접속 정보를 입력합니다. `.env`는 절대 공개하지 않습니다.
3. 기상 데이터 분석: `py scripts/02_analyze_seoul_asos.py`
4. FastAPI: `py -m uvicorn app.main:app --reload`
5. 로컬 페이지: http://127.0.0.1:8000

OpenAI API 호출에는 비용이 발생할 수 있습니다. 데이터는 과거 지상 관측으로 드론 비행 안전 판정·허가 기준이 아닙니다. 현재 FastAPI는 기본 데이터 확인용 페이지이며 기존 로컬 웹 디자인은 이후 반영합니다.
