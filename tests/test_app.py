from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_home(): assert client.get("/").status_code==200
def test_weather():
    d=client.get("/api/weather").json()
    assert d["realtime"] is False
    assert d["facts"]["observation_count"]==168
def test_observations():
    d=client.get("/api/observations?limit=24").json()
    assert d["total"]==168 and len(d["rows"])==24
def test_invalid_limit(): assert client.get("/api/observations?limit=500").status_code==422
def test_review(): assert client.get("/api/review").json()["published"] is False
def test_article(): assert client.get("/api/article").status_code in (200,403)
