import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Fraud Detection Inference API")


# Load model mounted from external Volume
MODEL_PATH = os.getenv("MODEL_PATH", "/mnt/data/fraud_model.pkl")

# Load model dynamically at startup
@app.on_event("startup")
def load_model():
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


# This is a FastAPI endpoint that receives a POST request
# and converts the incoming JSON into a Transaction object.
@app.post("/predict")
def predict_fraud(txn: Transaction):
    if not model:
        # Fallback heuristic if model file isn't present
        prob = 0.90 if txn.amount > 1000 else 0.05
        return {"fraud_probability": prob, "flagged": prob > 0.70}

    features = [[txn.amount, txn.location_score, txn.device_velocity]]
    probability = float(model.predict_proba(features)[0][1])

    return {
        "fraud_probability": round(probability, 4),
        "flagged": probability > 0.70,
    }