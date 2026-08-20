# Standalone Python script to generate synthetic training data, train a 
#   Random Forest Classifier using scikit-learn, evaluate it,
#   and export the serialized model to fraud_model.pkl using joblib
#   the execution is shown in ml-configmap.yaml

# Ensemble learning works by aggregating the predictions of a group of predictors,
# the results will be best than the best predictor alone, this group of predictors
# called ensemble and the technique called ensemble learning .
# https://www.kaggle.com/discussions/general/253592


import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


def generate_synthetic_data(num_samples=10000, seed=42):
    """Generates synthetic transactions matching the schema expected by the FastAPI service:

    - amount: Transaction amount in USD
    - location_score: Geolocation anomaly score (0.0 = safe, 1.0 = suspicious)
    - device_velocity: Number of distinct devices used in the last 24h
    """
    np.random.seed(seed)

    # Legitimate transactions (95% of data)
    num_legit = int(num_samples * 0.95)
    legit_amount = np.random.exponential(scale=50, size=num_legit) + 5
    legit_location = np.random.beta(a=1, b=5, size=num_legit)  # Biased toward 0
    legit_velocity = np.random.poisson(lam=1, size=num_legit) + 1
    legit_labels = np.zeros(num_legit, dtype=int)

    # Fraudulent transactions (5% of data)
    num_fraud = num_samples - num_legit
    fraud_amount = np.random.exponential(scale=400, size=num_fraud) + 200
    fraud_location = np.random.beta(a=5, b=1, size=num_fraud)  # Biased toward 1
    fraud_velocity = np.random.poisson(lam=5, size=num_fraud) + 2
    fraud_labels = np.ones(num_fraud, dtype=int)

    # Combine into DataFrame
    df = pd.DataFrame(
        {
            "amount": np.concatenate([legit_amount, fraud_amount]),
            "location_score": np.concatenate([legit_location, fraud_location]),
            "device_velocity": np.concatenate([legit_velocity, fraud_velocity]),
            "is_fraud": np.concatenate([legit_labels, fraud_labels]),
        }
    )

    # Shuffle rows
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def main():
    print("1. Generating synthetic transaction dataset...")
    data = generate_synthetic_data(num_samples=20000)

    # Split features and target
    X = data[["amount", "location_score", "device_velocity"]]
    y = data["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("2. Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, class_weight="balanced"
    )
    model.fit(X_train, y_train)

    print("\n3. Model Evaluation:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))

    # Output directory handling
    output_dir = os.getenv("MODEL_OUTPUT_DIR", "./")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fraud_model.pkl")

    print(f"4. Saving serialized model to: {output_path}")
    joblib.dump(model, output_path)
    print("Done! Model generated successfully.")


if __name__ == "__main__":
    main()