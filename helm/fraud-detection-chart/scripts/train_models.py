import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def generate_synthetic_data(num_samples=5000):
    """Generates synthetic credit card transaction data for model training."""
    np.random.seed(42)

    # Feature 1: Transaction Amount ($1 to $2000)
    amount = np.random.exponential(scale=100, size=num_samples) + 1.0

    # Feature 2: Geolocation Anomaly Score (0.0 to 1.0)
    location_score = np.random.beta(a=1, b=5, size=num_samples)

    # Feature 3: Device Velocity (Number of transactions from device in last 24h)
    device_velocity = np.random.poisson(lam=2, size=num_samples) + 1

    # Heuristic ground truth target for synthetic training
    fraud_condition = (
        (amount > 800)
        | ((location_score > 0.7) & (amount > 200))
        | (device_velocity > 6)
    )

    is_fraud = np.where(
        fraud_condition,
        np.random.choice([1, 0], p=[0.85, 0.15], size=num_samples),
        np.random.choice([0, 1], p=[0.97, 0.03], size=num_samples),
    )

    df = pd.DataFrame(
        {
            "amount": amount,
            "location_score": location_score,
            "device_velocity": device_velocity,
            "is_fraud": is_fraud,
        }
    )
    return df


def train_and_save():
    print("=== [InitContainer] Step 1: Generating Synthetic Fraud Dataset ===")
    df = generate_synthetic_data()

    X = df[["amount", "location_score", "device_velocity"]]
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("=== [InitContainer] Step 2: Training RandomForest Model ===")
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"=== [InitContainer] Model Accuracy: {acc:.4f} ===")
    print(classification_report(y_test, preds))

    # Output directory handling
    output_dir = os.getenv("MODEL_OUTPUT_DIR", "/mnt/data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fraud_model.pkl")

    print(f"=== [InitContainer] Step 3: Serializing Model to {output_path} ===")
    joblib.dump(clf, output_path)
    print("=== [InitContainer] Model Training & Export Succeeded! ===")


if __name__ == "__main__":
    train_and_save()