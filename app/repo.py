from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, Optional, List


UPSERT_SQL = """
INSERT INTO latest_readings (device_id, timestamp, metrics_json, received_at)
VALUES (?, ?, ?, ?)
ON CONFLICT(device_id) DO UPDATE SET
    timestamp=excluded.timestamp,
    metrics_json=excluded.metrics_json,
    received_at=excluded.received_at;
"""

SELECT_SQL = """
SELECT device_id, timestamp, metrics_json, received_at
FROM latest_readings
WHERE device_id = ?;
"""

SELECT_ALL_SQL = """
SELECT device_id, timestamp, metrics_json, received_at
FROM latest_readings
ORDER BY device_id ASC;
"""



def upsert_latest(
    conn: sqlite3.Connection,
    device_id: str,
    timestamp_iso: str,
    metrics: Dict[str, float],
    received_at_iso: str,
) -> None:
    metrics_json = json.dumps(metrics, separators=(",", ":"), sort_keys=True)
    conn.execute(UPSERT_SQL, (device_id, timestamp_iso, metrics_json, received_at_iso))


def fetch_latest(conn: sqlite3.Connection, device_id: str) -> Optional[Dict[str, Any]]:
    row = conn.execute(SELECT_SQL, (device_id,)).fetchone()
    if row is None:
        return None

    metrics = json.loads(row["metrics_json"])
    metrics = {str(k): float(v) for k, v in metrics.items()}

    return {
        "device_id": row["device_id"],
        "timestamp": row["timestamp"],
        "received_at": row["received_at"],
        "metrics": metrics,
    }


def fetch_all_latest(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(SELECT_ALL_SQL).fetchall()
    result: List[Dict[str, Any]] = []

    for row in rows:
        metrics = json.loads(row["metrics_json"])
        metrics = {str(k): float(v) for k, v in metrics.items()}

        result.append({
            "device_id": row["device_id"],
            "timestamp": row["timestamp"],
            "received_at": row["received_at"],
            "metrics": metrics,
        })

    return result
