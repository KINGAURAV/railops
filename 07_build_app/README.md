# 🖥️ Step 7 — Build App (Realtime Dashboard)

**RailOps** › **Realtime Inference** · `07_build_app/`

| [← Previous — Step 6 — Deploy Model](../06_deploy_model/) | [Next — Step 8 — Deploy →](../08_deploy/) |
|:---|---:|

Run the real-time pipeline locally — ingest API plus dashboard — then continue to [Step 8](../08_deploy/) to deploy both as Vayu ML Services.

---

<details>
<summary><h3>🗺️ Pipeline flow</h3></summary>

```text
Start Simulation (app.py replays 01_dataset/railway_telemetry.csv)
        │  POST /ingest
        ▼
ingestion_api.py — FastAPI, port 5000
        │
        ▼
Vayu Kafka topic: railway_telemetry
        │  consumer thread in app.py
        ▼
Vayu Model Serving — POST :predict (Step 6)
        │
        ▼
Dashboard — Streamlit, port 8501
        │  HIGH / CRITICAL risk, or operator command
        ▼
Vayu Kafka topic: railway_commands
```

</details>

---

<details>
<summary><h3>🧩 Files</h3></summary>

| File | Purpose |
|------|---------|
| `ingestion_api.py` | FastAPI gateway — validates sensor readings and publishes them to Kafka. No ML, no UI. |
| `app.py` | Streamlit dashboard — simulator, Kafka consumer, Model Serving client, command publisher |
| `kafka_config.py` | Shared Kafka connection settings (loads the root `.env`) |
| `Dockerfile.ingest` | Image for the ingest API (port 5000) |
| `Dockerfile.dashboard` | Image for the dashboard (port 8501), includes the simulator dataset |

#### Ingest API endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /ingest` | Accept one sensor reading and publish it to `KAFKA_TOPIC` |
| `GET /health` | Health check (broker and topic) |
| `GET /docs` | Swagger UI |

Example payload (`timestamp` is optional):

```json
{
  "track_id": "TRK-049",
  "section": "East",
  "vibration_hz": 84.2,
  "acoustic_emission_db": 53.4,
  "rail_strain_mu": 180.7,
  "track_temperature_c": 61.7,
  "alignment_deviation_mm": 4.75,
  "assigned_team": "Team Charlie",
  "last_maintenance_days": 127,
  "action_taken": "No"
}
```

#### Dashboard

- **KPIs** — live vibration, estimated remaining useful life, failure risk, crew dispatch status
- **Operator command** — send `EMERGENCY_SHUTDOWN`, `SPEED_RESTRICTION` or `DISPATCH_INSPECTION` for a segment
- **Track network map** — segments colored by risk (positions are synthetic)
- **Failure probability trend** and **sensor load indicators**
- **Incident & command log** and the full live telemetry table

For each reading the model's output is mapped to a risk level (`< 0.30` LOW, `< 0.60` MEDIUM, `< 0.85` HIGH, otherwise CRITICAL). `HIGH` and `CRITICAL` readings automatically publish a command to `KAFKA_COMMAND_TOPIC`.

</details>

---

<details>
<summary><h3>📋 Prerequisites</h3></summary>

- Steps 0–6 complete ([overview](../README.md))
- Kafka topics created ([Step 3](../03_vayu_kafka/))
- Model Serving predict URL ([Step 6](../06_deploy_model/))
- Root `.env` filled in from [`.env.example`](../.env.example) — both apps read Kafka settings (and `PREDICT_URL`) from it via `kafka_config.py`

</details>

---

<details>
<summary><h3>🚀 Run locally (two terminals)</h3></summary>

**Terminal 1 — Ingest API**

```bash
cd /home/jovyan/move-it/07_build_app
source /home/jovyan/.venv/bin/activate
python ingestion_api.py
```

Inside a Vayu AI Studio workspace, the API is reached through the workspace proxy. Start it with `ROOT_PATH` so the docs and routes resolve correctly:

```bash
ROOT_PATH=/proxy/5000 python ingestion_api.py
```

Verify: `curl http://127.0.0.1:5000/health`

**Terminal 2 — Dashboard**

```bash
cd /home/jovyan/move-it/07_build_app
source /home/jovyan/.venv/bin/activate
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`) and click **Start Simulation**.

**Predict endpoint** — choose one:

- Set `PREDICT_URL` in `.env` (or `export` it) — e.g. `https://<MODEL_SERVING_ENDPOINT>/v1/models/<MODEL_ID>:predict`. This overrides the sidebar.
- Or enter **Predict host base URL** (without `/v1`) and **Model name** in the sidebar.

The sidebar shows the resolved URL under **Predict endpoint ready**.

</details>

---

<details>
<summary><h3>🔑 Environment variables</h3></summary>

| Variable | Required | Default | Used by | Purpose |
|----------|----------|---------|---------|---------|
| `KAFKA_BROKER` | Yes | — | both | Kafka bootstrap server (`<ip>:<port>`) |
| `KAFKA_USERNAME` | Yes | — | both | Kafka SASL username |
| `KAFKA_PASSWORD` | Yes | — | both | Kafka SASL password |
| `KAFKA_TOPIC` | No | `railway_telemetry` | both | Telemetry topic |
| `KAFKA_COMMAND_TOPIC` | No | `railway_commands` | dashboard | Command topic |
| `KAFKA_GROUP_ID` | No | `railops_dashboard` | dashboard | Consumer group |
| `PREDICT_URL` | Yes* | — | dashboard | Full Model Serving predict URL |
| `VAYU_PREDICT_HOST`, `VAYU_MODEL_NAME` | No | —, `model` | dashboard | Pre-fill the sidebar instead of `PREDICT_URL` |
| `VAYU_BEARER_TOKEN`, `VAYU_HOST_HEADER` | No | — | dashboard | Optional auth / host header for Model Serving |
| `PREDICT_TIMEOUT` | No | `30` | dashboard | Predict request timeout (seconds) |
| `INGEST_API_URL` | No | `http://127.0.0.1:5000/ingest` | dashboard | Where the simulator posts readings |
| `PORT` | No | `5000` | ingest | Listen port when run with `python ingestion_api.py` |
| `ROOT_PATH` | No | — | ingest | Set to `/proxy/5000` behind the workspace proxy |

\* Or set the predict host and model name in the sidebar.

</details>

---

<details>
<summary><h3>🛠️ Troubleshooting</h3></summary>

| Symptom | Fix |
|---------|-----|
| Sidebar shows **Kafka: Disconnected** | Check `KAFKA_BROKER` / `KAFKA_USERNAME` / `KAFKA_PASSWORD`; confirm the topics exist |
| **Set the predict host (or PREDICT_URL)** | Set `PREDICT_URL` or fill in the sidebar |
| **Prediction error** in the sidebar | Confirm Model Serving is **Ready** and the predict URL is correct |
| Simulation errors / JSON parse failures | Check `INGEST_API_URL`; in a workspace, start the API with `ROOT_PATH=/proxy/5000` |
| Dashboard stuck on **Waiting** | Start the ingest API first, then click **Start Simulation** |
| **Dataset not found** | `01_dataset/railway_telemetry.csv` must exist (included in the dashboard image) |
| Commands not sent | Confirm `KAFKA_COMMAND_TOPIC` exists (`create_topic.py` creates it) |

</details>

---

| [← Previous — Step 6 — Deploy Model](../06_deploy_model/) | [Overview](../README.md) | [Next — Step 8 — Deploy →](../08_deploy/) |
|:---|:---:|---:|
