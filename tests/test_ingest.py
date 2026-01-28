from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_ingest_persists_and_returns_ok(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    payload = {
        "device_id": "room-sensor-01",
        "timestamp": "2026-01-19T12:34:56Z",
        "metrics": {"temp_c": 25.4, "humidity_pct": 56.1},
    }

    with TestClient(app) as client:
        r = client.post("/ingest", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["device_id"] == "room-sensor-01"
        assert "received_at" in body


def test_ingest_rejects_empty_metrics(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    payload = {"device_id": "room-sensor-01", "metrics": {}}

    with TestClient(app) as client:
        r = client.post("/ingest", json=payload)
        assert r.status_code == 422

def test_ingest_rejects_humidity_out_of_range(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    payload = {
        "device_id": "room-sensor-01",
        "metrics": {"humidity_pct": 150.0},
    }

    with TestClient(app) as client:
        r = client.post("/ingest", json=payload)
        assert r.status_code == 422


def test_ingest_rejects_temp_out_of_range(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    payload = {
        "device_id": "room-sensor-01",
        "metrics": {"temp_c": -999.0},
    }

    with TestClient(app) as client:
        r = client.post("/ingest", json=payload)
        assert r.status_code == 422


def test_ingest_allows_unknown_metric_if_numeric(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path=db_path)

    payload = {
        "device_id": "room-sensor-01",
        "metrics": {"pressure_hpa": 1013.2},
    }

    with TestClient(app) as client:
        r = client.post("/ingest", json=payload)
        assert r.status_code == 200

