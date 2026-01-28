from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import create_app


def test_devices_returns_empty_list_initially(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        r = client.get("/devices")
        assert r.status_code == 200
        assert r.json() == []


def test_devices_lists_multiple_devices(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        client.post("/ingest", json={"device_id": "a", "metrics": {"temp_c": 20.0}})
        client.post("/ingest", json={"device_id": "b", "metrics": {"humidity_pct": 50.0}})

        r = client.get("/devices")
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 2

        ids = {item["device_id"] for item in body}
        assert ids == {"a", "b"}
