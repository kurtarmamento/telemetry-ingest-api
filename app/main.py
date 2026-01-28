from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .db import get_connection, init_db
from .models import IngestRequest, IngestResponse, LatestResponse
from .repo import fetch_latest, fetch_all_latest, upsert_latest



def now_utc_iso() -> str:
    """Return current UTC time as ISO-8601 string with 'Z' suffix (seconds precision)."""
    dt = datetime.now(timezone.utc).replace(microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")


def create_app(db_path: str | None = None) -> FastAPI:
    """
    Application factory.

    db_path resolution order:
      1) explicit argument
      2) env var TELEMETRY_DB_PATH
      3) default: data/telemetry.db
    """
    resolved_db_path = db_path or os.getenv("TELEMETRY_DB_PATH") or os.path.join("data", "telemetry.db")

    app = FastAPI(
        title="Telemetry Ingest API",
        version="0.1.0",
        description="Minimal ingest API for IoT-style telemetry with SQLite persistence (latest-per-device).",
    )

    app.state.db_path = resolved_db_path

    @app.on_event("startup")
    def _startup() -> None:
        init_db(app.state.db_path)

    def db_conn():
        # Per-request connection; keeps code simple and avoids cross-thread issues.
        with get_connection(app.state.db_path) as conn:
            yield conn

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/ingest", response_model=IngestResponse)
    def ingest(payload: IngestRequest, conn=Depends(db_conn)) -> IngestResponse:
        # If timestamp is omitted, assign server time in UTC.
        ts = payload.timestamp or datetime.now(timezone.utc)
        ts_iso = ts.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        received_at = now_utc_iso()

        upsert_latest(
            conn=conn,
            device_id=payload.device_id,
            timestamp_iso=ts_iso,
            metrics=payload.metrics,
            received_at_iso=received_at,
        )

        return IngestResponse(status="ok", device_id=payload.device_id, received_at=received_at)

    @app.get("/latest/{device_id}", response_model=LatestResponse)
    def latest(device_id: str, conn=Depends(db_conn)) -> LatestResponse:
        row = fetch_latest(conn=conn, device_id=device_id)
        if row is None:
            raise HTTPException(status_code=404, detail="device_id not found")

        return LatestResponse(
            device_id=row["device_id"],
            timestamp=row["timestamp"],
            received_at=row["received_at"],
            metrics=row["metrics"],
        )

    @app.get("/devices", response_model=list[LatestResponse])
    def devices(conn=Depends(db_conn)) -> list[LatestResponse]:
        rows = fetch_all_latest(conn=conn)
        return [
            LatestResponse(
                device_id=r["device_id"],
                timestamp=r["timestamp"],
                received_at=r["received_at"],
                metrics=r["metrics"],
            )
            for r in rows
        ]

    @app.exception_handler(HTTPException)
    def http_exception_handler(_, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


app = create_app()

