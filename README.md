# 드론 운용 기상정보 뉴스

서울 ASOS 108 기상자료 분석 → MySQL 저장 → OpenAI 뉴스 생성 → 사람이 검수·승인하는 교육용 프로젝트입니다.

## 프로젝트 폴더

- `docs/` — 기획서·기능정의서·화면설계서·DB 설계서
- `scripts/` — 분석, MySQL 연결·적재, Fact Sheet 확인, AI 기사 생성, 승인
- `database/` — MySQL 스키마·등록·조회 SQL
- `data/raw/` — 기상청 원본 CSV (CP949 인코딩)
- `data/processed/` — 검증된 Fact Sheet JSON
- `articles/` — AI 뉴스 초안·수정 기사·검수 및 승인 기록
- `app/` — FastAPI 서버 (현재 기본 데이터 확인용 페이지)
- `tests/` — 향후 자동 테스트

## 빠른 실행 — 복사해서 순서대로 실행 (Windows PowerShell)

VS Code에서 프로젝트 최상위 폴더 `drone-weather-news`를 열고 **터미널 → 새 터미널**을 실행하세요.

```powershell
# 1. 가상환경 생성 (최초 1회)
py -m venv .venv

# 2. 가상환경 활성화 (새 터미널을 열 때마다)
.\.venv\Scripts\Activate.ps1

# 3. 패키지 설치 (최초 1회 / requirements 변경 시)
python -m pip install -r requirements.txt

# 4. 환경변수 파일 생성 (최초 1회)
Copy-Item .env.example .env

# 5. .env에 본인의 MySQL 정보 및 OpenAI API 키를 입력한 후 실행
python -m uvicorn app.main:app --reload
```

4번 실행 후 **`.env` 파일을 열어서 예시 비밀번호와 API 키를 본인 값으로 변경**하세요. 이미 `.env`가 있다면 `Copy-Item` 명령을 다시 실행하지 마세요(기존 설정을 보존하기 위해서입니다).

가상환경 활성화가 차단된다면 현재 PowerShell 터미널에서 다음 두 줄을 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

성공하면 `(.venv)`가 표시되고, 브라우저에서 **http://127.0.0.1:8000** 으로 접속할 수 있습니다. 종료: 서버는 `Ctrl+C`, 가상환경은 `deactivate`. `.env`는 **절대로 GitHub에 업로드하지 마세요.**

---

## 1. 실행 환경: Windows 11 + VS Code + PowerShell

필요한 프로그램: **Python**, **VS Code**, **MySQL Server** (DB 연동 시). 아래 명령어는 **GitHub 저장소 최상위 폴더**에서 실행합니다.

```powershell
# Git 저장소를 처음 내려받는 경우
git clone https://github.com/heumpc0922/drone-weather-news.git
cd drone-weather-news

# 구조 변경 PR을 검토 중인 경우, 새 구조가 있는 브랜치 선택
git switch chore/reorganize-docs-and-source
```

이미 프로젝트를 다운로드했다면 VS Code의 [파일 → 폴더 열기]에서 `drone-weather-news` 폴더를 열고 [터미널 → 새 터미널]을 사용하세요. `git clone`은 한 번만 합니다.

### 2. 가상환경(venv) 생성·활성화

```powershell
# 가상환경 생성 — 프로젝트 최초 1회
py -m venv .venv

# PowerShell에서 활성화 — VS Code 터미널을 새로 열 때마다 실행
.\.venv\Scripts\Activate.ps1

# 가상환경 안에 의존 패키지 설치
python -m pip install -r requirements.txt
```

터미널 맨 앞에 `(.venv)`가 나타나면 활성화된 것입니다. VS Code에서 Python 인터프리터를 선택할 때는 `.venv\Scripts\python.exe`를 고릅니다.

PowerShell에 *스크립트 실행이 차단되었습니다*라고 표시될 경우, **현재 터미널에 한해서만** 허용한 후 다시 활성화하세요.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

가상환경을 종료하려면 `deactivate`를 입력합니다.

### 3. .env 파일 만들기

프로젝트 루트에서 다음 명령을 실행합니다.

```powershell
Copy-Item .env.example .env
```

이제 VS Code에서 **루트의 `.env`** 파일을 열고, 아래 형식으로 로컬 MySQL 접속정보와 OpenAI API 키를 **본인 값으로** 바꾸세요.

```dotenv
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=여기에_본인_MySQL_비밀번호
MYSQL_DATABASE=drone_weather_news
OPENAI_API_KEY=여기에_본인_OpenAI_API_키
```

- `.env.example`에는 예시값만 유지하고, 실제 정보는 **`.env`에만** 저장합니다.
- `.env`는 `.gitignore`에 의해 Git 추적에서 제외되도록 설정했습니다. 그래도 **GitHub 웹 업로드 시 수동으로 추가하지 마세요**.
- API 키, 비밀번호, `.env` 내용을 스크린샷이나 채팅에 공유하지 마세요.
- MySQL만 사용할 때는 OpenAI 키가 필요하지 않으며, 데이터 조회 웹페이지에는 키가 필요하지 않습니다.

### 4. 기상자료 분석

```powershell
python scripts/02_analyze_seoul_asos.py
python scripts/02_read_fact_sheet.py
```

CSV는 `data/raw/OBS_ASOS_TIM_20261019111228.csv`, Fact Sheet는 `data/processed/01_drone_weather_fact_sheet.json`에 있습니다.

### 5. MySQL 준비·연결

1. MySQL Server를 실행합니다.
2. MySQL Workbench에서 `database/01_drone_weather_schema.sql`을 실행해 DB·테이블을 만듭니다.
3. `database/02_drone_weather_data.sql`을 실행해 서울 관측소 `station_id=108` 정보를 등록합니다.
4. 프로젝트 루트의 `.env` MySQL 정보를 확인합니다.
5. 아래 명령으로 연결 확인 후 CSV를 적재합니다.

```powershell
python scripts/03_test_mysql_connection.py
python scripts/04_import_asos_mysql.py
```

조회 SQL은 `database/03_drone_weather_queries.sql`에서 확인할 수 있습니다. 같은 CSV를 여러 번 적재해도 동일 관측시각의 중복 추가를 피하도록 작성되어 있습니다.

### 6. FastAPI 웹서버 실행

가상환경이 활성화된 터미널에서:

```powershell
python -m uvicorn app.main:app --reload
```

크롬에서 http://127.0.0.1:8000 접속, API 문서는 http://127.0.0.1:8000/docs 에서 확인합니다. 서버 종료는 터미널에서 `Ctrl + C`.

현재 `app/main.py`는 기상 Fact Sheet, 승인된 수정 기사, 검수 기록을 읽기 전용 API와 웹 화면에 연결합니다. 기상 정보는 과거 데이터이며 실시간 운항 판단이 아닙니다.

### 7. OpenAI 뉴스 생성 (선택, 유료 API 호출)

```powershell
python scripts/03_generate_openai_news.py
```

- `data/processed/`의 Fact Sheet를 입력으로 사용합니다.
- 실행 시 OpenAI API 비용이 발생할 수 있습니다.
- 결과는 `articles/04_ai_news_draft.txt`에 저장됩니다. 기존 초안을 **덮어쓸 수 있으므로** 보존이 필요하면 미리 별도 복사하세요.
- AI 초안은 검수 전 공개하지 않습니다.

### 8. 기사 검수·승인 (사람이 직접 선택)

```powershell
python scripts/07_review_and_approve.py
```

`articles/06_revised_drone_weather_article.txt`를 확인하고 승인(1)·보류(2), 검수자, 의견을 입력합니다. 결과는 `articles/08_article_approval.json`에 저장되며 기존 기록을 덮어씁니다. `published` 값은 `false`로 유지됩니다.

## 주의사항

- 서울 ASOS 108, **2026-10-12 ~ 2026-10-18** 자료는 과거 지상 관측입니다. 실시간 날씨 서비스가 아닙니다.
- 강수량 결측은 무강수와 다르며, 풍속 5m/s 초과는 실습용 분류일 뿐 드론 비행 허가 기준이 아닙니다.
- 공개된 `articles/`의 검수·승인 기록에는 개인정보가 없는지 확인하세요.
- 폴더 재구성에 맞춰 파일 경로를 수정했지만 환경별 통합 실행은 추가 확인이 필요합니다.

## 대시보드 확장 (2026-10-20)

FastAPI /api/observations?limit=24 는 기상청 CSV에서 서울 관측자료를 읽어 최근 24건과 원본 테이블·풍속 그래프를 표시합니다. /api/weather, /api/article, /api/review 와 함께 관제센터 스타일 대시보드로 통합했습니다.

가상환경 활성화 후 실행: python -m uvicorn app.main:app --reload

테스트: python -m pytest -q

**주의:** 과거 기상자료 기반 교육용 서비스이며 실시간 운항 지도, 비행지수, 비행 허가·안전 판정 기능은 없습니다. 강수량 결측은 무강수가 아닙니다. 기사의 검수 승인과 실제 게시도 구분합니다.

## MySQL CRUD API (교육용, 기본 쓰기 금지)

- `GET /api/mysql/observations?limit=20` — 실제 MySQL 서울 ASOS(108) 관측 읽기 (원본 변경 안 함)
- `GET /api/mysql/demo` — 별도 실습관측소(9999)의 `CRUD_API_TEST` 자료만 조회
- `POST /api/mysql/demo` — 실습자료 등록
- `PATCH /api/mysql/demo/{observation_id}` — 실습자료 풍속만 수정
- `DELETE /api/mysql/demo/{observation_id}` — 실습자료 삭제

실습 쓰기는 **기본적으로 403 비활성화**입니다. 개인 로컬 PC에서만 `.env`에 `ENABLE_DEMO_CRUD=true`를 추가해 활성화하세요. 실제 서비스 배포 시에는 활성화하면 안 됩니다. API 인증이 추가되어 있지 않으므로 서버는 로컬(`127.0.0.1`)에서만 실행하세요.

`python -m uvicorn app.main:app --reload` 실행 후 `http://127.0.0.1:8000/docs`의 `MySQL CRUD (교육용)` 그룹에서 테스트합니다. 학원 DB에 `station_id=9999`가 등록되어 있어야 쓰기가 됩니다. 기존 서울 관측 168건은 쓰기 쿼리에서 `station_id=9999 AND source='CRUD_API_TEST'`로 격리되어 있습니다.

`python -m pytest -q`는 실제 MySQL을 변경하지 않는 API 정책 테스트를 수행합니다.
