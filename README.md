# 🚁 드론 운용 기상정보 뉴스 | Drone Weather News

**서울 ASOS 실측 168건 → MySQL 저장·검증 → Fact Sheet → OpenAI 기사 작성 → 사람 검수·승인 → FastAPI 웹 대시보드**

> **프로젝트 성격:** 기상청 과거 지상 관측자료를 분석해 드론 운용 관련 **기상정보 뉴스를 제작하는 교육용 웹 프로젝트**입니다. 실시간 관제, 비행 가능 여부 판단, 비행 허가 서비스가 아닙니다.

## 🔎 평가자용 1분 요약

| 평가 포인트 | 직접 구현·검증한 내용 | 확인 위치 |
|---|---|---|
| 기획·설계 | PRD, 기능정의서, 화면설계서, MySQL DB 설계 | [docs/](docs/) |
| 원천 데이터·정제 | 기상청 서울 ASOS **108번**, 2026-10-12~18, **168개 시간 관측** | [원본 CSV](data/raw/OBS_ASOS_TIM_20261019111228.csv), [분석 코드](scripts/02_analyze_seoul_asos.py) |
| 데이터 검증 | 평균 풍속 **2.45m/s**, 최대 **5.9m/s**, 5m/s 초과 **2건**; 강수량 결측 **139건** | [Fact Sheet](data/processed/01_drone_weather_fact_sheet.json) |
| MySQL 설계·적재 | **5개 테이블**: station, observation, article, article_source, review; 서울 관측자료 168건 | [database/](database/), [적재 코드](scripts/04_import_asos_mysql.py) |
| CRUD 구현 | MySQL 직접 CRUD 및 **FastAPI POST/PATCH/DELETE**로 실습자료 등록·수정·삭제 | [CRUD API](app/routers/mysql_observations.py), [트랜잭션 SQL](database/05_mysql_crud_transaction_test.sql) |
| 데이터 보호 | 실제 관측소 **108 읽기 전용**, 쓰기는 테스트 관측소 9999와 `CRUD_API_TEST` 출처만 허용; 기본 쓰기 비활성화 | [API 구현](app/routers/mysql_observations.py), [.env.example](.env.example) |
| AI 기사·사람 검수 | OpenAI로 기사 초안 작성 → 수치·표현 점검 → 사람이 수정 기사 승인; **게시 상태는 미게시** | [기사·검수 결과](articles/), [생성 코드](scripts/03_generate_openai_news.py) |
| 웹 디자인·시각화 | 서울 야경·드론 배경, 통계 카드 5개, 풍속 그래프, 최근 관측표, AI 뉴스·검수 결과 | [웹 HTML](app/templates/index.html), [CSS](app/static/css/style.css), [이미지](app/static/images/seoul-drone.jpg) |
| 테스트 | **pytest 9개 통과**(로컬 실행 확인); FastAPI와 MySQL 실제 5건 조회 및 CRUD 시연 | [tests/](tests/), [MySQL 최종 SQL](database/06_mysql_final_data_integrity_check.sql) |

### 실제 검증 결과 (2026-10-20, 로컬 학원 PC 실행)

| 검증 | 결과 |
|---|---|
| `python -m pytest -q` | **9 passed** |
| FastAPI `GET /api/mysql/observations?limit=5` | **200 OK**, 서울 관측자료 5건 |
| `POST /api/mysql/demo` | **201 Created**, 테스트 ID **171** |
| `PATCH /api/mysql/demo/171` | **200 OK**, 풍속 **3.0 → 4.5m/s** |
| `DELETE /api/mysql/demo/171` | **200 OK**, 테스트 자료 삭제 |
| `GET /api/mysql/demo` | **200 OK**, `{"rows":[]}` |
| MySQL 최종 SQL 조회 | 전체 **168**, 서울 **168**, 남은 API 테스트 자료 **0** |

**중요:** 위 결과는 당시 로컬 실행과 화면 캡처로 확인한 값입니다. GitHub 저장소에 학원 PC의 MySQL 데이터 자체가 들어 있는 것은 아닙니다. pytest 9개는 웹/API 정책 단위 테스트이며, 실제 DB CRUD는 별도 수동 실행으로 검증했습니다.

## 🖥️ 실행 방법 — Windows 11 / VS Code / PowerShell

GitHub에서 저장소 내려받기 (처음 한 번만):

```powershell
git clone https://github.com/heumpc0922/drone-weather-news.git
cd drone-weather-news
```

이미 내려받았다면 VS Code에서 해당 폴더를 열고 터미널에서 `git pull origin main`을 실행합니다.

```powershell
# 1. 가상환경 생성 (처음 한 번만)
py -m venv .venv

# 2. 가상환경 활성화 (새 터미널마다)
.\.venv\Scripts\Activate.ps1

# 3. 패키지 설치
python -m pip install -r requirements.txt

# 4. 환경 파일 생성 (처음 한 번만, 기존 .env가 있으면 생략!)
Copy-Item .env.example .env

# 5. .env에 MySQL 접속정보 설정 후 서버 실행
python -m uvicorn app.main:app --reload
```

> `.env`에 `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`를 로컬 DB에 맞게 설정합니다. **`ENABLE_DEMO_CRUD=false`를 유지**하세요. OpenAI API 키는 기사 생성 프로그램을 새로 실행할 때만 필요합니다. 비밀번호나 키는 절대 GitHub에 올리지 않습니다.

- **웹사이트:** http://127.0.0.1:8000
- **대화형 API 문서(Swagger):** http://127.0.0.1:8000/docs
- **자동 테스트:** `python -m pytest -q`
- **MySQL 연결 확인:** `python scripts/03_test_mysql_connection.py`
- **종료:** 서버 실행 중 터미널에서 `Ctrl+C`

MySQL이 없는 환경에서도 저장된 CSV·Fact Sheet 기반 대시보드와 기본 API는 실행 가능하지만, **`/api/mysql/*`는 별도 MySQL Server와 데이터베이스 준비가 필요**합니다. MySQL 초기화·적재는 [스키마 SQL](database/01_drone_weather_schema.sql), [기초 데이터 SQL](database/02_drone_weather_data.sql), [CSV 적재 코드](scripts/04_import_asos_mysql.py)를 참조하세요. 학원 DB를 다른 PC로 복원하려면 별도 SQL Dump가 필요합니다. 기존 데이터가 있으면 중복 적재하지 마세요.

PowerShell에서 활성화가 차단되면 현재 터미널에서만 다음을 실행합니다: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## 🧩 주요 API 및 구현 구분

| 엔드포인트 | 용도 |
|---|---|
| `GET /` | 드론 기상정보 뉴스 웹 대시보드 |
| `GET /api/weather` | 검증된 Fact Sheet 통계 |
| `GET /api/observations?limit=24` | **CSV 기반** 시간별 관측자료 (홈페이지 그래프·표) |
| `GET /api/article` | 승인된 수정 기사 열람 |
| `GET /api/review` | 사람 검수·게시 상태 |
| `GET /api/mysql/observations?limit=5` | **MySQL 기반** 서울 관측자료 조회 |
| `GET /api/mysql/demo` | 테스트 자료만 조회 |
| `POST /api/mysql/demo`, `PATCH /api/mysql/demo/{id}`, `DELETE /api/mysql/demo/{id}` | 로컬 교육용 테스트 관측자료 CRUD |

**웹 대시보드의 그래프는 CSV를 읽으며, MySQL 실측 조회는 별도 API에서 수행합니다.** 두 방식을 혼동하지 않도록 구분했습니다.

실습용 쓰기 API는 로그인·인증이 없으므로 기본적으로 **403 차단**합니다. 실습이 꼭 필요한 경우에만 로컬 `.env`에서 `ENABLE_DEMO_CRUD=true`로 잠시 열고, 실습 후 반드시 `false`로 복구합니다. 공개 서버에서는 활성화하면 안 됩니다.

## 📁 핵심 파일 찾아보기

```text
docs/                      기획서·기능·화면·DB 설계
data/raw/                  기상청 CSV 원본
data/processed/            검증 Fact Sheet JSON
database/                  MySQL 스키마·적재·조회·CRUD·최종 검증 SQL
scripts/                   Python 자료분석·MySQL 적재·OpenAI 기사·승인
articles/                  AI 기사 초안·수정본·사람 검수·승인 기록
app/main.py                FastAPI 실행 진입점
app/database.py            MySQL 연결
app/routers/mysql_observations.py  MySQL 조회·교육용 CRUD
app/templates/index.html   웹 화면
app/static/                CSS·JavaScript·드론 배경사진
tests/                     pytest 자동 테스트
.env.example               환경변수 예시 (비밀정보 없음)
requirements.txt           실행 라이브러리
```

## ✅ 제작 과정과 검수·한계

1. 기상청 ASOS(서울 108) 시간별 원본 CSV 수집 및 Python 분석.
2. MySQL 5개 테이블 설계·적재; 제약조건 검사(습도 150% 입력 거부).
3. 실제 수치만 포함한 Fact Sheet 정리 및 OpenAI로 AI 기사 초안 생성.
4. 사람이 수치·표현을 확인하고 수정 기사 승인. 승인 정보는 [08_article_approval.json](articles/08_article_approval.json)에 저장; **`published:false`**는 미게시를 뜻함.
5. FastAPI 기반 기상정보 뉴스 웹페이지와 MySQL CRUD 데모 구축, 자동 테스트 및 실제 DB CRUD 검증.

**해석 주의:** 이 데이터는 **2026-10-12~18의 과거 지상 관측자료**입니다. 비행 고도 바람·현장 기상을 보장하지 않고 비행 가능 여부나 법적 허가를 판단하지 않습니다. 5m/s는 **학습용 분석 구분값**일 뿐 일률적 비행 제한 기준이 아닙니다. 강수량 결측 **139건을 무강수로 해석하지 않았습니다.** 배경 이미지는 제작된 콘셉트 이미지이며 실제 특정 시점 촬영사진이 아닙니다.

**구현 범위 밖:** 실시간 관측 자동 갱신, 항공 안전 판정·지도, 사용자 로그인/권한 인증, 외부 공개 배포. 평가 시 완성 기능으로 오인되지 않도록 구분합니다.

---

**GitHub 제출 링크:** https://github.com/heumpc0922/drone-weather-news

**시연 순서 추천:** (1) `/` 웹디자인·그래프·AI 뉴스 → (2) `/docs`의 MySQL 조회 → (3) `python -m pytest -q` 9개 통과 → (4) `database/06_mysql_final_data_integrity_check.sql`로 **168 / 168 / 0** 확인.


## 이용 조건

이 프로젝트의 **코드, 관측자료, 분석 결과, AI 기사, 이미지에는 서로 다른 이용 조건**이 적용될 수 있습니다. 아래에 출처와 확인된 범위, 재사용 시 주의사항을 구분합니다.

| 자료 구분 | 출처 및 제작·사용 내역 | 공개·재이용 조건 |
|---|---|---|
| 프로젝트 코드 | 이 저장소에서 직접 작성했거나 배포 권한이 있는 Python·HTML·CSS 등 코드 | **MIT License** 적용. 원문은 [LICENSE](LICENSE) 참고. 제3자 자료에는 자동 적용되지 않음 |
| 기상 관측 원본 | **기상청 기상자료개방포털**, 서울 ASOS **108번**, **2026-10-12~18** 시간별 관측 168건. [원본 CSV](data/raw/OBS_ASOS_TIM_20261019111228.csv) | 자료 출처를 **기상청 기상자료개방포털**로 표시. 원본의 개별 공공누리 표시·이용 조건은 재배포 전에 확인 |
| 분석 데이터·Fact Sheet | 위 기상청 원본을 Python으로 집계·가공한 프로젝트 분석 결과. [분석 코드](scripts/02_analyze_seoul_asos.py), [Fact Sheet](data/processed/01_drone_weather_fact_sheet.json) | 분석·가공 사실과 원본 출처를 함께 표시. 가공했다고 원본 자료의 권리가 사라지는 것은 아님 |
| AI 기사 초안 | [생성 스크립트](scripts/03_generate_openai_news.py)에서 **OpenAI API / `gpt-5-mini`**를 사용하도록 지정. [AI 초안](articles/04_ai_news_draft.txt) | **AI 생성 초안**임을 표시하고 원본 수치·표현을 사람에게 검수받은 뒤 이용. 외부 인용문이 있다면 별도 출처 확인 |
| 사람 검수·수정 기사 | [검수 보고서](articles/05_article_review_report.md), [수정 기사](articles/06_revised_drone_weather_article.txt), [승인 기록](articles/08_article_approval.json) | 승인 기록상 **사람 검수일: 2026-10-19**, **미게시(`published:false`)**. 이는 AI 초안 생성일과 다르며, 생성 일시는 저장된 자료만으로 확인되지 않음 |
| 웹 배경 이미지 | [`app/static/images/seoul-drone.jpg`](app/static/images/seoul-drone.jpg). 프로젝트 설명상 **서울·드론 콘셉트 이미지**로, 실제 특정 시각의 촬영 증거가 아님 | **제작 도구·제작 날짜·원저작물·권리자의 허락 여부는 저장소에서 확인되지 않음**. 따라서 MIT 적용 대상이라고 단정하지 않으며, 제3자가 재사용하려면 별도 권리 확인이 필요 |

### 출처 및 권리 관련 참고

- 기상청 자료 제공처: [기상자료개방포털](https://data.kma.go.kr/)  
- 기상청의 공식 [저작권 보호 및 정책](https://data.kma.go.kr/cmmn/static/staticPage.do?page=pageCr): 기상청이 권리를 보유하고 **공공누리 제1유형**으로 표시한 저작물은 **출처를 밝히고 이용**할 수 있습니다. 다만 **이 CSV 파일에 어떤 유형 표시가 붙어 있는지는 별도로 확인해야 하며**, 기상청 자료 전체에 일괄적으로 제1유형을 선언하는 것은 아닙니다.
- OpenAI 모델 및 생성 방식: [생성 스크립트](scripts/03_generate_openai_news.py)를 통해 확인 가능. **AI 모델을 사용했다는 사실과 사람의 최종 책임**을 구분합니다.
- 별도로 제3자 기사 문구, 사진·로고 등을 추가할 경우 **원저작자·원문 URL·인용 범위·이용 허락**을 개별 확인하여 출처를 기록합니다.

> **윤리·법적 책임:** 이 저장소의 MIT License는 작성자가 권리를 가진 **코드**의 이용 조건입니다. **기상청 원본 데이터, 제3자 인용물, 배경 이미지에 대한 재사용 허락을 대신하지 않습니다.** 확인되지 않은 이용 권한은 허락받은 것으로 표시하지 않습니다.
