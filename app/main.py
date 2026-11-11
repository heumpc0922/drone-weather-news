"""서울 ASOS Fact Sheet와 사람 검수 기사를 표시하는 읽기 전용 웹서비스."""
import json
import csv
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
DIR = Path(__file__).resolve().parent
app = FastAPI(title="드론 운용 기상정보 뉴스", version="1.2.0")
app.mount("/static", StaticFiles(directory=DIR / "static"), name="static")
# Hosted demos serve only the archive; keep the database router local.
if os.getenv("VERCEL") != "1" and os.getenv("PUBLIC_DEMO") != "1":
    from app.routers.mysql_observations import router as mysql_router

    app.include_router(mysql_router)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail="데이터 파일을 읽을 수 없습니다.") from exc


@app.get("/")
def home():
    return FileResponse(DIR / "templates" / "index.html")


@app.get("/api/weather")
def weather():
    facts = load_json(ROOT / "data" / "processed" / "01_drone_weather_fact_sheet.json")
    return {"source": facts["data_source"], "period": facts["observation_period"],
            "facts": facts["verified_facts"], "cautions": facts["editorial_cautions"],
            "realtime": False}


@app.get("/api/review")
def review():
    record = load_json(ROOT / "articles" / "08_article_approval.json")
    return {"status": record.get("status", "unknown"),
            "status_ko": record.get("status_ko", "미확인"),
            "reviewed_at": record.get("reviewed_at"),
            "published": bool(record.get("published", False)),
            "comment": record.get("comment", "")}


@app.get("/api/article")
def article():
    record = load_json(ROOT / "articles" / "08_article_approval.json")
    if record.get("status") != "approved":
        raise HTTPException(status_code=403, detail="승인되지 않은 기사입니다.")
    path = ROOT / "articles" / "06_revised_drone_weather_article.txt"
    try:
        body = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail="기사 파일을 읽을 수 없습니다.") from exc
    if not body.strip():
        raise HTTPException(status_code=503, detail="기사 내용이 없습니다.")
    return {"body": body, "published": bool(record.get("published", False)),
            "notice": "사람이 승인한 기사 열람용이며, 실제 공개 여부와 다릅니다."}


@app.get("/api/observations")
def observations(limit: int = Query(24, ge=1, le=168)):
    path = ROOT / "data" / "raw" / "OBS_ASOS_TIM_20261019111228.csv"
    try:
        with path.open("r", encoding="cp949", newline="") as f:
            rows = list(csv.DictReader(f))
    except UnicodeError:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        raise HTTPException(status_code=503, detail="관측자료 CSV를 읽지 못했습니다.") from exc
    def num(value):
        return float(value) if value and value.strip() else None
    data = [{
        "observed_at": r["일시"], "station": "서울",
        "temperature_c": num(r["기온(°C)"]),
        "wind_speed_ms": num(r["풍속(m/s)"]),
        "humidity_pct": num(r["습도(%)"]),
        "precipitation_mm": num(r["강수량(mm)"])
    } for r in rows if r["지점"].strip() == "108"]
    data.sort(key=lambda x: x["observed_at"])
    return {"total": len(data), "realtime": False, "rows": data[-limit:]}

@app.get("/api/hourly-wind")
def hourly_wind():
    path = ROOT / "data" / "raw" / "OBS_ASOS_TIM_20261019111228.csv"

    try:
        with path.open("r", encoding="cp949", newline="") as f:
            rows = list(csv.DictReader(f))
    except UnicodeError:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        raise HTTPException(status_code=503, detail="관측자료 CSV를 읽지 못했습니다.") from exc

    hourly_data = {}

    for r in rows:
        if r["지점"].strip() != "108":
            continue

        observed_at = r.get("일시", "").strip()
        wind_raw = r.get("풍속(m/s)", "").strip()

        if not observed_at or not wind_raw:
            continue

        try:
            dt = datetime.strptime(observed_at, "%Y-%m-%d %H:%M")
            wind = float(wind_raw)
        except (ValueError, TypeError):
            continue

        hour = dt.hour

        if hour not in hourly_data:
            hourly_data[hour] = {"sum": 0.0, "count": 0}

        hourly_data[hour]["sum"] += wind
        hourly_data[hour]["count"] += 1

    result = []
    for hour in range(24):
        if hour in hourly_data and hourly_data[hour]["count"] > 0:
            avg = round(hourly_data[hour]["sum"] / hourly_data[hour]["count"], 2)
            count = hourly_data[hour]["count"]
        else:
            avg = None
            count = 0

        result.append({
            "hour": hour,
            "label": f"{hour:02d}시",
            "count": count,
            "average_wind_speed_ms": avg
        })

    valid_rows = [x for x in result if x["average_wind_speed_ms"] is not None]

    if valid_rows:
        strongest = max(valid_rows, key=lambda x: x["average_wind_speed_ms"])
    else:
        strongest = None

    return {
        "station": "서울 ASOS 108",
        "analysis": "서울 시간대별 평균 풍속",
        "rows": result,
        "strongest_hour": strongest
    }
