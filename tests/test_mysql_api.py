"""실측자료 쓰기 방지 정책: 실제 DB에 접속하지 않고 확인."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
def test_write_disabled(monkeypatch):
    monkeypatch.delenv("ENABLE_DEMO_CRUD", raising=False)
    assert client.post("/api/mysql/demo", json={
        "observed_at": "2026-10-20T16:00:00", "wind_speed_ms": 2.1
    }).status_code == 403
    assert client.patch("/api/mysql/demo/1", json={"wind_speed_ms": 2.1}).status_code == 403
    assert client.delete("/api/mysql/demo/1").status_code == 403

def test_invalid_wind_speed():
    assert client.post("/api/mysql/demo", json={
        "observed_at": "2026-10-20T16:00:00", "wind_speed_ms": -1
    }).status_code == 422

def test_api_registered():
    paths = {r.path for r in app.routes}
    assert "/api/mysql/observations" in paths
    assert "/api/mysql/demo" in paths
