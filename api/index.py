import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS: Access-Control-Allow-Origin: * for POST (and the OPTIONS preflight)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Put the telemetry file next to this script (e.g. api/telemetry.json)
DATA = json.loads((Path(__file__).parent / "telemetry.json").read_text())


class Query(BaseModel):
    regions: list[str]
    threshold_ms: float


def pick(rec, *names):
    for n in names:
        if n in rec:
            return rec[n]
    raise KeyError(names)


@app.post("/")
@app.post("/api")
def metrics(q: Query):
    out = {}
    for region in q.regions:
        rows = [r for r in DATA if pick(r, "region") == region]
        if not rows:
            continue
        lat = np.array([pick(r, "latency_ms", "latency") for r in rows], dtype=float)
        up = np.array([pick(r, "uptime_pct", "uptime") for r in rows], dtype=float)
        out[region] = {
            "avg_latency": float(lat.mean()),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(up.mean()),
            "breaches": int((lat > q.threshold_ms).sum()),
        }
    return out
