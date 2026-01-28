from __future__ import annotations

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field, field_validator

import math


class IngestRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    timestamp: datetime | None = None
    metrics: Dict[str, float]

    @field_validator("metrics")
    @classmethod
    def _metrics_validate(cls, v: Dict[str, float]) -> Dict[str, float]:
        # 1) Basic shape checks
        if not isinstance(v, dict) or len(v) == 0:
            raise ValueError("metrics must contain at least one key/value pair")

        for k in v.keys():
            if not isinstance(k, str) or not k.strip():
                raise ValueError("metrics keys must be non-empty strings")

        # 2) Finite numeric checks (reject NaN/Inf)
        for k, val in v.items():
            try:
                f = float(val)
            except (TypeError, ValueError):
                raise ValueError(f"metrics['{k}'] must be numeric")

            if not math.isfinite(f):
                raise ValueError(f"metrics['{k}'] must be a finite number")

            # store back as float (ensures consistent type)
            v[k] = f

        # 3) Range checks for known metrics
        ranges = {
            "temp_c": (-20.0, 80.0),
            "humidity_pct": (0.0, 100.0),
        }

        for key, (lo, hi) in ranges.items():
            if key in v:
                if not (lo <= v[key] <= hi):
                    raise ValueError(f"metrics['{key}'] must be in range [{lo}, {hi}]")

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
