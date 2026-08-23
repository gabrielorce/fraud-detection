import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Fraud Detection Inference API")

# Initialize standard HTTP request & latency metrics
instrumentator = Instrumentator()
instrumentator.instrument(app)

# Custom Prometheus Counter for ML prediction tracking
PREDICTION_COUNTER = Counter(
    "fraud_predictions_total",
    "Total count of transaction fraud evaluations",
    ["result_label"]  # labels: 'flagged' or 'cleared'
)

# Load model mounted from external Volume
MODEL_PATH = os.getenv("MODEL_PATH", "/mnt/data/fraud_model.pkl")

# Load model dynamically at startup and expose /metrics
@app.on_event("startup")
def load_model():
    # Expose the /metrics endpoint
    instrumentator.expose(app, endpoint="/metrics")

    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"Loaded model successfully from {MODEL_PATH}")
    else:
        print(f"Warning: {MODEL_PATH} not found. Fallback mode enabled.")
        model = None


class Transaction(BaseModel):
    amount: float
    location_score: float
    device_velocity: int


@app.get("/health")
def healthcheck():
    return {"status": "ok", "model_loaded": model is not None}


import pandas as pd

@app.post("/predict")
def predict_fraud(txn: Transaction):
    if not model:
        prob = 0.90 if txn.amount > 1000 else 0.05
        is_flagged = prob > 0.70
        PREDICTION_COUNTER.labels(result_label="flagged" if is_flagged else "cleared").inc()
        return {"fraud_probability": prob, "flagged": is_flagged}

    # Cap features to training ranges so extreme values don't hit empty leaf nodes
    amount_capped = min(max(txn.amount, 0.0), 5000.0)
    location_capped = min(max(txn.location_score, 0.0), 1.0)
    velocity_capped = min(max(txn.device_velocity, 1), 12)  # Cap velocity at 12

    df_features = pd.DataFrame([{
        "amount": amount_capped,
        "location_score": location_capped,
        "device_velocity": velocity_capped
    }])

    probability = float(model.predict_proba(df_features)[0][1])
    is_flagged = probability > 0.70

    PREDICTION_COUNTER.labels(result_label="flagged" if is_flagged else "cleared").inc()

    return {
        "fraud_probability": round(probability, 4),
        "flagged": is_flagged,
    }