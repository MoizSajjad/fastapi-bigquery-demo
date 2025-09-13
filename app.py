import os, json, logging, sys
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from google.cloud import bigquery

PROJECT = os.getenv("GCP_PROJECT", "erudite-mote-472009-r1")
DATASET = os.getenv("BQ_DATASET", "demo_asia")
TABLE   = os.getenv("BQ_TABLE",   "voxels")
TABLE_ID = f"{PROJECT}.{DATASET}.{TABLE}"

h = logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.INFO, handlers=[h], format="%(message)s")
def log(sev, msg, **kw): logging.info(json.dumps({"severity": sev, "message": msg, **kw}))

bq_client = bigquery.Client(project=PROJECT)
app = FastAPI(title="Voxels API", version="1.0")

class Voxel(BaseModel):
    # Let client omit ts; we will set/normalize it
    ts: Optional[datetime] = Field(default=None)
    x: int
    y: int
    z: int
    value: float

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/voxels/insert")
def insert_voxels(items: List[Voxel]):
    rows = []
    now_iso = datetime.now(timezone.utc).isoformat()
    for item in items:
        d = item.model_dump()
        # ensure ts is an ISO8601 string (no raw datetime objects)
        if d.get("ts") is None:
            d["ts"] = now_iso
        elif isinstance(d["ts"], datetime):
            d["ts"] = d["ts"].astimezone(timezone.utc).isoformat()
        rows.append(d)

    err = bq_client.insert_rows_json(TABLE_ID, rows)
    if err:
        log("ERROR", "insert_failed", errors=err)
        raise HTTPException(status_code=500, detail=err)
    log("INFO", "insert_ok", count=len(rows))
    return {"inserted": len(rows)}

@app.get("/voxels/slice")
def read_slice(
    z: int = Query(..., description="Z plane to filter"),
    days: int = Query(7, ge=1, le=365, description="How many days back")
):
    q = f"""
    SELECT ts, x, y, z, value
    FROM `{TABLE_ID}`
    WHERE z = @z AND ts >= @since
    ORDER BY ts DESC
    LIMIT 1000
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    job = bq_client.query(q, job_config=bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("z","INT64", z),
            bigquery.ScalarQueryParameter("since","TIMESTAMP", since),
        ]
    ))
    rows = [dict(r) for r in job.result()]
    log("INFO", "query_ok", z=z, rows=len(rows))
    return {"rows": rows}
