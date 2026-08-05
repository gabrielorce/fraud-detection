import os
import joblib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Load model mounted from external Volume
MODEL_PATH = os.getenv("MODEL_PATH", "/mnt/data/fraud_model.pkl")

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        model = None  # Fallback rule engine if training data hasn't rendered yet

class Transaction(BaseModel):
    amount: float
    location_score: float
    device_velocity: int

@app.post("/predict")
def predict_fraud(txn: Transaction):
    if model:
        prediction = model.predict_proba([[txn.amount, txn.location_score, txn.device_velocity]])[0][1]
    else:
        # Mock score if model file isn't uploaded yet
        prediction = 0.85 if txn.amount > 1000 else 0.05

    return {"fraud_probability": round(float(prediction), 4), "flagged": prediction > 0.7}