
# Voxels API (FastAPI + BigQuery + Cloud Run)

This project demonstrates a **serverless FastAPI service** deployed on **Google Cloud Run** that writes and reads data from **BigQuery**.

---

##  Architecture
- **FastAPI** REST API  
- **Google BigQuery** dataset & table for storage  
- **Artifact Registry** to store container images  
- **Cloud Run** to deploy the service (scales to zero)  

---

##  Project Structure
```

fast-api-bq/
├── app.py              # FastAPI app (insert + query endpoints)
├── bq\_sample.py        # Local test script for BigQuery
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition
└── README.md           # This file

````

---

##  Setup

### 1. Clone repo & create virtual env
```bash
git clone <repo-url>
cd fast-api-bq
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
````

### 2. Authenticate with Google Cloud

```bash
gcloud init
gcloud auth application-default login
```

### 3. BigQuery dataset & table

Dataset: `demo_asia`
Table: `voxels`

Schema:

| Column | Type      |
| ------ | --------- |
| ts     | TIMESTAMP |
| x      | INT64     |
| y      | INT64     |
| z      | INT64     |
| value  | FLOAT64   |

---

##  Local Run

### Run FastAPI app

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8086
```

### Test endpoints

* Health check: [http://localhost:8086/health](http://localhost:8086/health)
* API docs (Swagger UI): [http://localhost:8086/docs](http://localhost:8086/docs)

Example `POST`:

```json
[
  {"x": 1, "y": 2, "z": 5, "value": 0.55}
]
```

---

## ☁️ Deployment on GCP

### 1. Build and push Docker image

```bash
REGION="asia-south1"
REPO="fastapi-repo"
gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION
gcloud builds submit --tag "$REGION-docker.pkg.dev/<PROJECT_ID>/$REPO/voxels-api:v1"
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy voxels-api \
  --image="$REGION-docker.pkg.dev/<PROJECT_ID>/$REPO/voxels-api:v1" \
  --region=$REGION \
  --allow-unauthenticated \
  --service-account="voxels-sa@<PROJECT_ID>.iam.gserviceaccount.com" \
  --set-env-vars="BQ_DATASET=demo_asia,BQ_TABLE=voxels"
```

---

##  Public URL

After deploy, Cloud Run prints a URL like:

```
https://voxels-api-<PROJECT_NUMBER>.asia-south1.run.app
```

* Health check: `GET /health`
* Insert data: `POST /voxels/insert`
* Query data: `GET /voxels/slice?z=5&days=7`

---

##  Example

### Insert

```bash
curl -X POST "https://<SERVICE_URL>/voxels/insert" \
-H "Content-Type: application/json" \
-d '[{"x":1,"y":2,"z":5,"value":0.55}]'
```

Response:

```json
{"inserted": 1}
```

### Query

```bash
curl "https://<SERVICE_URL>/voxels/slice?z=5&days=7"
```

Response:

```json
{
  "rows": [
    {"ts": "2025-09-13T14:30:52Z", "x": 1, "y": 2, "z": 5, "value": 0.55}
  ]
}
```

---

##  Notes

* Service Account `voxels-sa` needs **BigQuery Data Editor** role.
* Cloud Run scales to zero → no idle cost.
* Billing budget recommended to avoid surprises.

---

##  Screenshots to include (for report/demo)

* Swagger UI `/docs`
* Successful POST/GET
* BigQuery table with inserted rows
* Cloud Run service page

---

## 📝 Next Improvements

* Input validation (bounds for x,y,z,value)
* CORS for frontend use
* Bulk inserts
* CI/CD pipeline with Cloud Build

```

---

Do you want me to also create a **shorter "student submission style" README** (1-page max, no fluff, just what you did + how to test), or should I leave this detailed one as-is?
```
