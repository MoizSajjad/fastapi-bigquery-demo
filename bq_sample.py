from google.cloud import bigquery
from datetime import datetime, timezone

PROJECT = "erudite-mote-472009-r1"
DATASET = "demo_asia"
TABLE   = "voxels"
TABLE_ID = f"{PROJECT}.{DATASET}.{TABLE}"

def seed():
    """Inserting a couple of rows into BigQuery to verify write access."""
    client = bigquery.Client(project=PROJECT)
    rows = [
        {"ts": datetime.now(timezone.utc).isoformat(), "x": 9, "y": 9, "z": 9, "value": 27.1},
        {"ts": datetime.now(timezone.utc).isoformat(), "x": 2, "y": 1, "z": 0, "value": 25.6},
    ]
    errors = client.insert_rows_json(TABLE_ID, rows)
    print("Insert result:", errors)  # [] = success

def query(z=1):
    """Read back some rows to verify read access."""
    client = bigquery.Client(project=PROJECT)
    q = f"""
    SELECT ts, x, y, z, value
    FROM `{TABLE_ID}`
    WHERE z = @z
    ORDER BY ts DESC
    LIMIT 10
    """
    job = client.query(q, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("z", "INT64", z)]
    ))
    return [dict(r) for r in job.result()]

if __name__ == "__main__":
    seed()
    print(query(1))
