import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="드론 운용 기상정보 뉴스")

@app.get("/", response_class=HTMLResponse)
def home():
    path = ROOT / "data" / "processed" / "01_drone_weather_fact_sheet.json"
    facts = json.loads(path.read_text(encoding="utf-8"))["verified_facts"]
    return (f"<html lang='ko'><meta charset='utf-8'><h1>드론 운용 기상정보 뉴스</h1>"
            f"<p>서울 ASOS 108 · 과거 관측</p><p>관측 {facts['observation_count']}건, "
            f"평균 풍속 {facts['average_wind_speed_ms']} m/s, 최대 풍속 {facts['maximum_wind_speed_ms']} m/s</p>"
            "<p>교육용 분석이며 비행 안전·허가 기준이 아닙니다.</p></html>")
