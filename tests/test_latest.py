from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_latest_404_when_missing(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        r = client.get("/latest/unknown-device")
        assert r.status_code == 404


def test_latest_returns_last_ingest(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    payload = {
        "device_id": "room-sensor-01",
        "timestamp": "2026-01-19T12:34:56Z",
        "metrics": {"temp_c": 25.4, "humidity_pct": 56.1},
    }

    with TestClient(app) as client:
        r1 = client.post("/ingest", json=payload)
        assert r1.status_code == 200

        r2 = client.get("/latest/room-sensor-01")
        assert r2.status_code == 200
        body = r2.json()
        assert body["device_id"] == "room-sensor-01"
        assert body["timestamp"] == "2026-01-19T12:34:56Z"
        assert body["metrics"]["temp_c"] == 25.4
        assert body["metrics"]["humidity_pct"] == 56.1
        assert "received_at" in body
