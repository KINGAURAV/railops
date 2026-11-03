# 🚆 RailOps — Real-Time Railway Predictive Maintenance

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Gateway-FastAPI-009688?logo=fastapi&logoColor=white)
![Kafka](https://img.shields.io/badge/Streaming-Kafka-231F20?logo=apachekafka&logoColor=white)
![scikit-learn](https://img.shields.io/badge/Model-scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![MLflow](https://img.shields.io/badge/Tracking-MLflow-0194E2?logo=mlflow&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)

RailOps is an end-to-end IoT-to-ML streaming pipeline that monitors railway track health in real time, predicts which track segments are at risk of failure, and closes the loop by publishing maintenance commands back over Kafka. It runs on the **Vayu AI cloud platform** (Tata Communications) and was built for the **Vayu Hackathon**.

---

## Table of contents

- [The problem](#the-problem)
- [What RailOps does](#what-railops-does)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Repository structure](#repository-structure)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Model](#model)
- [Ingest API](#ingest-api)
- [Deployment](#deployment)
- [Limitations and future work](#limitations-and-future-work)

---

## The problem

Track defects — misalignment, excessive wear, rail cracks, structural stress — are usually found through periodic manual inspection. Faults that develop between inspections can force emergency speed restrictions, disrupt service or, in the worst case, cause derailments. Continuous sensor data from the track is available, but it is rarely turned into timely, actionable decisions.

## What RailOps does

- **Streams trackside telemetry** — vibration, acoustic emission, rail strain, track temperature and alignment deviation — through an HTTP ingest API into Kafka.
- **Scores every reading** with a Random Forest model served behind a REST endpoint.
- **Turns predictions into decisions** — risk level (`LOW` → `CRITICAL`), likely fault type, recommended action, estimated remaining useful life and crew dispatch status.
- **Acts automatically** — `HIGH` and `CRITICAL` segments trigger a `SPEED_RESTRICTION` or `EMERGENCY_SHUTDOWN` command on a Kafka command topic; operators can also send commands manually.
- **Visualizes everything live** — KPIs, a risk-colored network map, failure-probability trends, an incident/command log and the raw telemetry stream.
- **Tracks experiments** in MLflow and versions the model in a model registry.

A built-in simulator replays the dataset through the full pipeline, so the system can be demonstrated without physical sensors.

## Architecture

```text
 ┌──────────────────────┐   HTTP POST    ┌──────────────────────┐
 │ Sensors / simulator  │ ─────────────▶ │  Ingest API          │
 └──────────────────────┘    /ingest     │  FastAPI · :5000     │
                                         └──────────┬───────────┘
                                                    │ produce
                                                    ▼
                                         ┌──────────────────────┐
                                         │ Kafka                │
                                         │ topic: railway_      │
                                         │        telemetry     │
                                         └──────────┬───────────┘
                                                    │ consume
                                                    ▼
 ┌──────────────────────┐   :predict     ┌──────────────────────┐
 │ Model Serving        │ ◀───────────── │  Dashboard           │
 │ Random Forest        │ ─────────────▶ │  Streamlit · :8501   │
 └──────────────────────┘   prediction   └──────────┬───────────┘
                                                    │ HIGH / CRITICAL
                                                    ▼
                                         ┌──────────────────────┐
                                         │ Kafka                │
                                         │ topic: railway_      │
                                         │        commands      │
                                         └──────────────────────┘

 Offline:  dataset (S3) ──▶ training notebook ──▶ MLflow ──▶ model registry ──▶ Model Serving
```

## Tech stack

| Layer | Technology |
|-------|------------|
| Ingestion | FastAPI, Uvicorn, Pydantic |
| Streaming | Apache Kafka (`kafka-python`, SASL/SCRAM) |
| ML | scikit-learn (Random Forest), pandas, NumPy |
| Experiment tracking | MLflow |
| Storage | S3-compatible object storage (boto3) |
| Dashboard | Streamlit, pydeck |
| Packaging | Docker (two images), cosign image signing |
| Platform | Vayu AI Studio — Workspace, Object Storage, MLflow, Kafka, Model Registry, Model Serving, ML Service |

## Repository structure

The repository is organized as a numbered, step-by-step pipeline. Each folder has its own README.

```text
.
├── .env.example              # Template for every credential and setting
├── requirements.txt
├── 00_vayu_workspaces/       # Workspace setup
├── 01_dataset/               # railway_telemetry.csv + generator / S3 sync notebook
├── 02_vayu_mlflow/           # MLflow deployment
├── 03_vayu_kafka/            # create_topic.py — telemetry + command topics
├── 04_starter-kit/           # train_model.ipynb → model.joblib
├── 05_model_registry/        # upload_model.py → S3 + registry
├── 06_deploy_model/          # Model Serving deployment
├── 07_build_app/             # ingestion_api.py, app.py, kafka_config.py, Dockerfiles
├── 08_deploy/                # Build, sign, push and deploy both services
└── assets/                   # Screenshots used in the guides
```

| Step | Folder | Outcome |
|------|--------|---------|
| 0 | [`00_vayu_workspaces`](00_vayu_workspaces/) | Workspace with Docker enabled, repo cloned, dependencies installed |
| 1 | [`01_dataset`](01_dataset/) | `railway_telemetry.csv` generated and synced to S3 |
| 2 | [`02_vayu_mlflow`](02_vayu_mlflow/) | Managed MLflow tracking server |
| 3 | [`03_vayu_kafka`](03_vayu_kafka/) | Kafka cluster with telemetry and command topics |
| 4 | [`04_starter-kit`](04_starter-kit/) | Trained model logged and registered in MLflow, `model.joblib` saved |
| 5 | [`05_model_registry`](05_model_registry/) | Model uploaded to S3 and registered |
| 6 | [`06_deploy_model`](06_deploy_model/) | Live predict endpoint |
| 7 | [`07_build_app`](07_build_app/) | Ingest API and dashboard running locally |
| 8 | [`08_deploy`](08_deploy/) | Both services deployed with public endpoints |

## Getting started

### Prerequisites

- Python 3.11+
- Access to a Kafka cluster, an MLflow server, S3-compatible storage and a model-serving endpoint (on Vayu, credentials come from the hackathon **Access Guide**)
- Docker (only for deployment)

### Install

```bash
git clone <this-repo-url> railops
cd railops
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then fill in every <...> value
```

### Run the pipeline

```bash
# 1. Dataset — included; optionally regenerate / sync with S3
jupyter notebook 01_dataset/01_dataset.ipynb

# 2. Kafka topics
python 03_vayu_kafka/create_topic.py

# 3. Train, log to MLflow and save model.joblib
jupyter notebook 04_starter-kit/train_model.ipynb

# 4. Upload the model, then register and deploy it (Steps 5–6), and set PREDICT_URL in .env
python 05_model_registry/upload_model.py

# 5. Realtime app — two terminals
cd 07_build_app && python ingestion_api.py     # terminal 1 → http://localhost:5000/docs
cd 07_build_app && streamlit run app.py        # terminal 2 → http://localhost:8501
```

In the dashboard sidebar, confirm **Predict endpoint ready** and **Kafka: Connected**, then click **Start Simulation**.

## Configuration

All components read the root `.env` (see [`.env.example`](.env.example)). It is excluded from git and from Docker images.

| Variable | Used by | Description |
|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_ENDPOINT`, `S3_BUCKET_NAME` | dataset, training, upload | Object storage |
| `S3_DATASET_KEY`, `S3_MODEL_KEY` | dataset, upload | Object paths |
| `MLFLOW_TRACKING_URL`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD` | training | MLflow server |
| `KAFKA_BROKER`, `KAFKA_USERNAME`, `KAFKA_PASSWORD` | topics, ingest, dashboard | Kafka connection (`<ip>:<port>`, SASL/SCRAM-SHA-512) |
| `KAFKA_TOPIC`, `KAFKA_COMMAND_TOPIC` | topics, ingest, dashboard | Default `railway_telemetry`, `railway_commands` |
| `PREDICT_URL` | dashboard | `https://<host>/v1/models/<model-id>:predict` |
| `INGEST_API_URL` | dashboard | Default `http://127.0.0.1:5000/ingest` |
| `ROOT_PATH` | ingest | Set to `/proxy/5000` behind the Vayu workspace proxy |
| `IMAGE_REGISTRY`, `REGISTRY_PROJECT`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`, `VAYU_USERNAME` | deployment | Container registry |

See [`07_build_app/README.md`](07_build_app/README.md) for the full list of dashboard options.

## Model

| | |
|---|---|
| Algorithm | `RandomForestClassifier(n_estimators=100, max_depth=6)` |
| Features (in order) | `vibration_hz`, `acoustic_emission_db`, `rail_strain_mu`, `track_temperature_c`, `alignment_deviation_mm`, `last_maintenance_days` |
| Target | `failure_probability > 0.5` → at risk |
| Tracking | MLflow experiment `railops_predictive_maintenance`, registered model `RailOps_Maintenance_Model` |

The dashboard maps the model output to risk bands — `< 0.30` LOW, `< 0.60` MEDIUM, `< 0.85` HIGH, otherwise CRITICAL — and derives the recommended action, fault type and remaining-useful-life estimate from it.

**Dataset.** `01_dataset/railway_telemetry.csv` contains 2,000 synthetic readings across 50 track segments, simulating normal operation (75%), high wear (15%) and emergency conditions (10%). See [`01_dataset/README.md`](01_dataset/README.md) for the schema.

## Ingest API

| Endpoint | Description |
|----------|-------------|
| `POST /ingest` | Validate a sensor reading and publish it to Kafka |
| `GET /health` | Broker and topic status |
| `GET /docs` | Interactive Swagger UI |

```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "track_id": "TRK-049", "section": "East",
        "vibration_hz": 84.2, "acoustic_emission_db": 53.4, "rail_strain_mu": 180.7,
        "track_temperature_c": 61.7, "alignment_deviation_mm": 4.75,
        "assigned_team": "Team Charlie", "last_maintenance_days": 127, "action_taken": "No"
      }'
```

## Deployment

The ingest API and dashboard ship as two Docker images, built from the repository root:

```bash
docker build -f 07_build_app/Dockerfile.ingest    -t $IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest    --push .
docker build -f 07_build_app/Dockerfile.dashboard -t $IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-dashboard:latest --push .
```

Images are signed with cosign and deployed as two Vayu ML Services (ingest first, then the dashboard pointed at it). Full instructions: [`08_deploy/README.md`](08_deploy/README.md).

## Limitations and future work

- **Synthetic data.** `failure_probability` is computed from the same sensor readings used as features, so model accuracy is not representative of real-world performance. Real labelled failure and inspection data is the next step.
- **Binary model output.** The serving endpoint returns class labels, so the dashboard currently sees only low or critical risk. Serving `predict_proba` would enable the full four-level risk scale.
- **Heuristic downstream logic.** Remaining useful life, fault type and dispatch status are rule-based and derived from the predicted risk.
- **Synthetic map positions.** The dataset has no coordinates; map positions are derived from track IDs.

## License

Developed for the Vayu Hackathon. Use and modify for hackathon submissions unless your team specifies otherwise.
