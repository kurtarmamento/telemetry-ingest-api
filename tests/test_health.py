from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_ok(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}
