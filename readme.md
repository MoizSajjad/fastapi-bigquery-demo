# FastAPI + BigQuery + Cloud Run Demo

This project demonstrates how to build and deploy a serverless API with FastAPI, Google BigQuery, and Google Cloud Run. The service exposes endpoints to insert and query data in a BigQuery table.

---

## Overview

- **Backend Framework**: FastAPI  
- **Database**: Google BigQuery  
- **Containerization**: Docker, built and pushed via Google Cloud Build  
- **Deployment**: Google Cloud Run (serverless)  

---

## Data Model

**Dataset**: `demo_asia`  
**Table**: `voxels`  

Schema:

| Column | Type      | Description             |
|--------|-----------|-------------------------|
| ts     | TIMESTAMP | Record timestamp        |
| x      | INT64     | X coordinate            |
| y      | INT64     | Y coordinate            |
| z      | INT64     | Z coordinate (slice)    |
| value  | FLOAT64   | Example numeric reading |

---

## Project Structure

```

fast-api-bq/
│── app.py              # FastAPI app with insert/query endpoints
│── bq\_sample.py        # Local BigQuery insert/query test script
│── requirements.txt    # Python dependencies
│── Dockerfile          # Container build instructions
│── README.md           # Documentation

````

---

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/MoizSajjad/fastapi-bigquery-demo.git
   cd fastapi-bigquery-demo
````

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate      # On Windows
   source venv/bin/activate   # On Linux/Mac
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Authenticate with Google Cloud:

   ```bash
   gcloud auth application-default login
   ```

5. Run locally:

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8086
   ```

6. Access locally:

   * Swagger UI: [http://localhost:8086/docs](http://localhost:8086/docs)
   * Health check: [http://localhost:8086/health](http://localhost:8086/health)

---

## Deployment to Google Cloud Run

1. Set variables:

   ```bash
   REGION="asia-south1"
   REPO="fastapi-repo"
   ```

2. Create Artifact Registry repository:

   ```bash
   gcloud artifacts repositories create $REPO \
     --repository-format=docker --location=$REGION
   ```

3. Build and push image:

   ```bash
   gcloud builds submit \
     --tag "$REGION-docker.pkg.dev/<PROJECT_ID>/$REPO/voxels-api:v1"
   ```

4. Deploy to Cloud Run:

   ```bash
   gcloud run deploy voxels-api \
     --image="$REGION-docker.pkg.dev/<PROJECT_ID>/$REPO/voxels-api:v1" \
     --region=$REGION \
     --allow-unauthenticated \
     --set-env-vars="BQ_DATASET=demo_asia,BQ_TABLE=voxels"
   ```

---

## Live Service

Deployed URL (Cloud Run):

```
https://voxels-api-178398688763.asia-south1.run.app
```

### Endpoints

* `GET /health` → Health check
* `POST /voxels/insert` → Insert rows into BigQuery
* `GET /voxels/slice?z=<int>&days=<int>` → Query rows

### Example Requests

Insert:

```bash
curl -X POST "https://voxels-api-178398688763.asia-south1.run.app/voxels/insert" \
-H "Content-Type: application/json" \
-d '[{"x":1,"y":2,"z":5,"value":0.55}]'
```

Query:

```bash
curl "https://voxels-api-178398688763.asia-south1.run.app/voxels/slice?z=5&days=7"
```

---

## Learning Objectives

* Connect FastAPI with BigQuery for programmatic read/write.
* Containerize an application with Docker and Cloud Build.
* Deploy a serverless API on Cloud Run.
* Expose clean REST endpoints on top of a data warehouse.


---

Would you like me to also prepare a **shorter README.md (one-page max)** for your mentor submission (summary style), or keep this full professional version only?
```
