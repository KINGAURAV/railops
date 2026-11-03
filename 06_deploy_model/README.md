# 🚀 Step 6 — Deploy Model

**RailOps** › **Vayu Model Serving** · `06_deploy_model/`

| [← Previous — Step 5 — Model Registry](../05_model_registry/) | [Next — Step 7 — Build App →](../07_build_app/) |
|:---|---:|

Deploy **`04_starter-kit/model.joblib`** for **online sklearn inference** via **Vayu Model Serving**.

---

<details>
<summary><h3>🧩 What's in this step?</h3></summary>

Deploy the trained sklearn model so the [Step 7 Streamlit UI](../07_build_app/) can call a **predict HTTP endpoint** (not local `joblib` loading).

</details>

---

<details>
<summary><h3>📋 Prerequisites</h3></summary>

- [Step 4 — Starter Kit](../04_starter-kit/) — `model.joblib` generated
- [Step 5 — Vayu Model Registry](../05_model_registry/) — artifact registered

</details>

---

<details>
<summary><h3>🔗 Open Model Serving</h3></summary>

Go to [Vayu Model Serving](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-serving-list).

For the full create wizard (Start → Infrastructure → Predictor Configuration → Configure Compute and Storage → Review), see the [Creating Model Serving guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-serving/#creating-model-serving).

For the complete product documentation, see the [Model Serving guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-serving/).

</details>

---

<details>
<summary><h3>🚀 Deploy in Vayu Model Serving</h3></summary>

1. **Confirm artifact** — `04_starter-kit/model.joblib` exists.
2. **Register** via [Step 5](../05_model_registry/) if not already done.
3. **Create deployment** on [Vayu Model Serving](https://ipcloud.tatacommunications.com/aistudio/#/deploy/model-serving-list). Follow the [Creating Model Serving guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-serving/#creating-model-serving) for step-by-step wizard details:
   - **Model type:** **Predictive AI**
   - **Public access:** Enable the **Public Access** toggle in the deployment wizard.
   - **Framework:** **sklearn**
   - **Model and version:** Select the model and version you registered in [Step 5](../05_model_registry/).
   - **Configure compute and storage (recommended):** On the **Configure Compute and Storage** step:
     - **Flavor:** Select **8 vCPU / 32GB RAM / cpu** from the **General Purpose** flavors (choose **cpu** from the dropdown).
     - **Billing Mode:** **Hourly**
     - **Storage Flavor:** **SSD1-Persistent Storage**
     - **Billing Mode for Storage:** **Monthly**
     - **Size:** **50 GiB**
     - **Volume Mode:** **Dedicated** (replicas are set to **1** automatically when you select this)

     Change these if your workload needs more resources.

> **Note:** For any other wizard configurations not listed above, leave them as they are.

4. **Wait for Ready:** Submit the deployment and wait until the status shows **Ready**.

5. **Firewall rules:** After the deployment is **Ready**, configure firewall rules. Follow **`Port 443 FW Rule.pdf`** shared with your team.

6. **Note the predict endpoint** — open the **Connect** tab on the Model Serving detail page and **copy** the **Public Endpoint**. The UI typically copies only the base URL through `/v1` (for example, `https://<MODEL_SERVING_ENDPOINT>/v1`).

7. **Get `<MODEL_ID>` and test the endpoint** (after firewall rules are applied):

   ```bash
   curl -X GET "<MODEL_SERVING_ENDPOINT>/v1/models"
   ```

   Sample output `{"models":["model"]}` — the id here is `model`.

   Append `/models/<MODEL_ID>:predict` to the base URL to form the full predict URL:

   `https://<MODEL_SERVING_ENDPOINT>/v1/models/<MODEL_ID>:predict`

   For sidebar configuration in [Step 7](../07_build_app/), see the [Step 7 README](../07_build_app/).

   **Test predict with curl:**

   Each instance is a list of the six features in training order: `vibration_hz`, `acoustic_emission_db`, `rail_strain_mu`, `track_temperature_c`, `alignment_deviation_mm`, `last_maintenance_days`.

   ```bash
   curl -X POST \
     "https://<MODEL_SERVING_ENDPOINT>/v1/models/<MODEL_ID>:predict" \
     -H "Content-Type: application/json" \
     -d '{"instances": [[50.2, 40.1, 118.5, 31.0, 0.3, 20], [86.0, 64.5, 178.0, 63.0, 4.6, 150]]}'
   ```

   Example response: `{"predictions": [0, 1]}` — `0` = normal, `1` = at risk of failure.

</details>

---

<details>
<summary><h3>💡 Pro tips and notes</h3></summary>

- **Model name** (`<MODEL_ID>`) — must match between the Vayu deployment, predict URL path, and Streamlit sidebar.
- **Retrain** — re-run `train_model.ipynb` and redeploy after notebook changes.

</details>

---

#### Resources

- [Creating Model Serving guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-serving/#creating-model-serving)
- [Model Serving guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/model-serving/)
- **`Port 443 FW Rule.pdf`**

---

| [← Previous — Step 5 — Model Registry](../05_model_registry/) | [Overview](../README.md) | [Next — Step 7 — Build App →](../07_build_app/) |
|:---|:---:|---:|
