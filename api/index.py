import json
import math
import statistics
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).resolve().parent.parent / "telemetry.json"
with DATA_PATH.open("r", encoding="utf-8") as f:
    TELEMETRY = json.load(f)

def percentile_95(values):
    # Linear interpolation, equivalent to the common inclusive percentile.
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = 0.95 * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction

@app.post("/api/latency")
async def latency_metrics(request: Request):
    try:
        payload = await request.json()
        regions = payload.get("regions", [])
        threshold = float(payload.get("threshold_ms", 180))
        if not isinstance(regions, list) or not all(isinstance(r, str) for r in regions):
            return JSONResponse(
                {"error": "'regions' must be a list of strings"},
                status_code=400,
            )
    except (ValueError, TypeError, AttributeError):
        return JSONResponse({"error": "Invalid JSON request body"}, status_code=400)

    response = {}
    for region in regions:
        records = [row for row in TELEMETRY if row.get("region") == region]
        if not records:
            response[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
            }
            continue

        latencies = [float(row["latency_ms"]) for row in records]
        uptimes = [float(row["uptime_pct"]) for row in records]
        response[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": percentile_95(latencies),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(value > threshold for value in latencies),
        }

    return response
