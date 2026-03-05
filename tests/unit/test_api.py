from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_birds_api_has_five():
    r = client.get("/api/birds")
    assert r.status_code == 200
    assert len(r.json()["birds"]) == 5