from __future__ import annotations

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field, field_validator


class IngestRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=128, description="Device identifier, e.g. room-sensor-01")
    timestamp: datetime | None = Field(
        default=None,
        description="Optional ISO-8601 timestamp. If omitted, the server assigns current UTC time.",
    )
    metrics: Dict[str, float] = Field(
        description="Map of metric name to numeric value, e.g. {'temp_c': 25.4, 'humidity_pct': 56.1}"
    )

    @field_validator("metrics")
    @classmethod
    def _metrics_not_empty(cls, v: Dict[str, float]) -> Dict[str, float]:
        if not isinstance(v, dict) or len(v) == 0:
            raise ValueError("metrics must contain at least one key/value pair")
        for k in v.keys():
            if not isinstance(k, str) or not k.strip():
                raise ValueError("metrics keys must be non-empty strings")
        return v


class IngestResponse(BaseModel):
    status: str
    device_id: str
    received_at: str  # ISO-8601 UTC string with Z suffix


class LatestResponse(BaseModel):
    device_id: str
    timestamp: str     # ISO-8601 UTC string with Z suffix
    received_at: str   # ISO-8601 UTC string with Z suffix
    metrics: Dict[str, float]
