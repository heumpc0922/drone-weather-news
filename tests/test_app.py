from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_home():
    assert client.get("/").status_code==200
def test_weather():
    data=client.get("/api/weather").json()
    assert data["realtime"] is False
    assert data["facts"]["observation_count"]==168
def test_review():
    assert client.get("/api/review").json()["published"] is False
def test_article():
    r=client.get("/api/article")
    assert r.status_code in (200,403)
    if r.status_code==200:
        assert r.json()["body"].strip()
