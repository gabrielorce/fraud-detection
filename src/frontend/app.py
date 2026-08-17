import os
import requests
import streamlit as st

st.set_page_config(page_title="Fraud Detection Portal", layout="wide")

# Read K8s service endpoint from environment variable. if not provided, 
# it will have the "http://ml-service:8000" value.
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml-service:8000")

st.title("Real-Time Fraud Detection Engine")
st.write("Enter transaction metrics below to evaluate risk using the ML microservice.")

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("Transaction Amount ($)", min_value=1.0, value=150.0)
    location_score = st.slider("Geolocation Anomaly Score", 0.0, 1.0, 0.1)
    device_velocity = st.number_input("Devices Used in 24h", min_value=1, value=1)

with col2:
    st.subheader("Risk Analysis")
    if st.button("Evaluate Transaction", type="primary"):
        payload = {
            "amount": amount,
            "location_score": location_score,
            "device_velocity": device_velocity,
        }
        try:
            res = requests.post(
                f"{ML_SERVICE_URL}/predict", json=payload, timeout=5
            )
            data = res.json()

            prob = data["fraud_probability"] * 100
            flagged = data["flagged"]

            st.metric("Fraud Probability", f"{prob:.1f}%")

            if flagged:
                st.error("HIGH RISK: Transaction Flagged for Review")
            else:
                st.success("LOW RISK: Transaction Approved")

        except Exception as e:
            st.error(f"Could not connect to ML Microservice at {ML_SERVICE_URL}: {e}")