import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}


@app.middleware("http")
async def add_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    response = await call_next(request)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response


DATA = json.loads((Path(__file__).parent / "telemetry.json").read_text())


class Query(BaseModel):
    regions: list[str]
    threshold_ms: float


@app.get("/")
@app.get("/api")
def health():
    return {"status": "ok", "usage": "POST {regions: [...], threshold_ms: 180}"}


@app.post("/")
@app.post("/api")
def metrics(q: Query):
    out = {}
    for region in q.regions:
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            continue
        lat = np.array([r["latency_ms"] for r in rows], dtype=float)
        up = np.array([r["uptime_pct"] for r in rows], dtype=float)
        out[region] = {
            "region": region,
            "avg_latency": float(lat.mean()),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(up.mean()),
            "breaches": int((lat > q.threshold_ms).sum()),
        }
    return {"regions": out}
