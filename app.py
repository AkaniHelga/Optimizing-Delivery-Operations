import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Load the saved model and features
model = joblib.load("tree_ensemble_model.pkl")
model_features = joblib.load("model_features.pkl")

st.title("Operations: Delivery Time Optimizer")
st.markdown(
    "Predict delivery ETAs and forecast unit economics for dispatch operations."
)

# SIDEBAR INPUTS
st.sidebar.header("Order Parameters")

agent_age = st.sidebar.slider("Agent Age", 20, 50, 30)
agent_rating = st.sidebar.slider("Agent Rating", 3.0, 5.0, 4.5, 0.1)
distance_km = st.sidebar.number_input(
    "Distance (km)", min_value=0.5, max_value=30.0, value=5.0, step=0.5
)

# Categorical inputs matching training data structure
traffic = st.sidebar.selectbox("Traffic Condition", ["Low", "Medium", "Jam"])
weather = st.sidebar.selectbox(
    "Weather", ["Sunny", "Fog", "Windy", "Stormy", "Sandstorms"]
)
vehicle = st.sidebar.selectbox("Vehicle Type", ["scooter", "van"])
area = st.sidebar.selectbox("Area Type", ["Urban", "Semi-Urban", "Other"])

# PREDICTION LOGIC
if st.button("Predict Delivery & Calculate Economics"):
  # 1. Create a blank input row matching all expected feature columns
  input_data = pd.DataFrame(0, index=[0], columns=model_features)

  # Fill numeric features
  if "Agent_Age" in input_data.columns:
    input_data["Agent_Age"] = agent_age
  if "Agent_Rating" in input_data.columns:
    input_data["Agent_Rating"] = agent_rating
  if "Distance(km)" in input_data.columns:
    input_data["Distance(km)"] = distance_km

  # Fill encoded categorical dummies dynamically
  traffic_col = f"Traffic_{traffic}"
  if traffic_col in input_data.columns:
    input_data[traffic_col] = 1

  weather_col = f"Weather_{weather}"
  if weather_col in input_data.columns:
    input_data[weather_col] = 1

  vehicle_col = f"Vehicle_{vehicle}"
  if vehicle_col in input_data.columns:
    input_data[vehicle_col] = 1

  area_col = f"Area_{area}"
  if area_col in input_data.columns:
    input_data[area_col] = 1

  # 2. Predict Delivery Time using Tree Ensemble Model
  predicted_time = model.predict(input_data)[0]

  # 3. Downstream Fleet Economics Calculation
  base_fare = 100
  time_rate = 4
  distance_rate = 20
  surge = 1.35 if traffic == "Jam" else 1.0

  estimated_earnings = (
      base_fare + (predicted_time * time_rate) + (distance_km * distance_rate)
  ) * surge

  # DISPLAY RESULTS 
  col1, col2 = st.columns(2)

  with col1:
    st.metric(
        label="Estimated Delivery Time", value=f"{predicted_time:.1f} mins"
    )

  with col2:
    st.metric(
        label="Forecasted Courier Payout", value=f"KES {estimated_earnings:.2f}"
    )

  if traffic == "Jam":
    st.warning(
        "⚠️ High Traffic Surge Active: Payout adjusted dynamically to ensure"
        " courier retention."
    )
  else:
    st.success("✅ Normal operating conditions.")