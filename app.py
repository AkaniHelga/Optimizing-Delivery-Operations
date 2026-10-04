import time
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Load saved model and features
model = joblib.load("tree_ensemble_model.pkl")
model_features = joblib.load("model_features.pkl")

st.title("Delivery Time Optimizer")
st.markdown(
    "Predict delivery ETAs and forecast unit economics for dispatch operations."
)

# Sidebar Mode Selector
app_mode = st.sidebar.selectbox(
    "Operations Mode", ["Manual Dispatch Calculator", "Live Order Simulator"]
)
# manual slider/dropdown code here)
if app_mode == "Manual Dispatch Calculator":
  st.subheader("Manual Order Evaluation")
  agent_age = st.sidebar.slider("Agent Age", 20, 50, 30)
  agent_rating = st.sidebar.slider("Agent Rating", 3.0, 5.0, 4.5, 0.1)
  distance_km = st.sidebar.number_input(
      "Distance (km)", min_value=0.5, max_value=30.0, value=5.0, step=0.5
  )
  traffic = st.sidebar.selectbox("Traffic Condition", ["Low", "Medium", "Jam"])
  weather = st.sidebar.selectbox(
      "Weather", ["Sunny", "Fog", "Windy", "Stormy", "Sandstorms"]
  )
  vehicle = st.sidebar.selectbox("Vehicle Type", ["scooter", "van"])
  area = st.sidebar.selectbox("Area Type", ["Urban", "Semi-Urban", "Other"])

  if st.button("Predict Delivery & Calculate Economics"):
    input_data = pd.DataFrame(0, index=[0], columns=model_features)
    # Fill features 
    if "Agent_Age" in input_data.columns:
      input_data["Agent_Age"] = agent_age
    if "Agent_Rating" in input_data.columns:
      input_data["Agent_Rating"] = agent_rating
    if "Distance(km)" in input_data.columns:
      input_data["Distance(km)"] = distance_km
    if f"Traffic_{traffic}" in input_data.columns:
      input_data[f"Traffic_{traffic}"] = 1
    if f"Weather_{weather}" in input_data.columns:
      input_data[f"Weather_{weather}"] = 1
    if f"Vehicle_{vehicle}" in input_data.columns:
      input_data[f"Vehicle_{vehicle}"] = 1
    if f"Area_{area}" in input_data.columns:
      input_data[f"Area_{area}"] = 1

    predicted_time = model.predict(input_data)[0]
    base_fare, time_rate, distance_rate = 100, 4, 20
    surge = 1.35 if traffic == "Jam" else 1.0
    earnings = (
        base_fare + (predicted_time * time_rate) + (distance_km * distance_rate)
    ) * surge

    col1, col2 = st.columns(2)
    col1.metric("Estimated Delivery Time", f"{predicted_time:.1f} mins")
    col2.metric("Forecasted Courier Payout", f"KES {earnings:.2f}")

elif app_mode == "Live Order Simulator":
  st.subheader("🔴 Live Dispatch Stream (Nairobi Hub)")
  st.markdown(
      "Simulating incoming multi-zone orders and real-time fleet responses."
  )

  # Control button to run the live stream loop
  run_simulation = st.checkbox("Start Live Stream Feed")

  # Placeholder for live data table and map
  live_placeholder = st.empty()
  map_placeholder = st.empty()

  # Simulated coordinates around Nairobi (e.g., Westlands, CBD, Kilimani)
  nairobi_coords = [
      {"lat": -1.2921, "lon": 36.8219, "zone": "CBD"},
      {"lat": -1.2635, "lon": 36.8028, "zone": "Westlands"},
      {"lat": -1.2987, "lon": 36.7825, "zone": "Kilimani"},
      {"lat": -1.3032, "lon": 36.8647, "zone": "Eastlands"},
  ]

  while run_simulation:
    # Generate a mock incoming order stream
    simulated_orders = []
    for i in range(5):
      loc = np.random.choice(nairobi_coords)
      dist = np.random.uniform(2.0, 15.0)
      traf = np.random.choice(["Low", "Medium", "Jam"], p=[0.5, 0.3, 0.2])
      weath = np.random.choice(["Sunny", "Fog", "Windy"], p=[0.7, 0.2, 0.1])

      # Build input row for model
      # Build input row for model
      row = pd.DataFrame(0.0, index=[0], columns=model_features)
      if "Agent_Age" in row.columns:
        row.loc[0, "Agent_Age"] = np.random.randint(22, 45)
      if "Agent_Rating" in row.columns:
        row.loc[0, "Agent_Rating"] = np.random.uniform(4.0, 5.0)
      if "Distance(km)" in row.columns:
        row.loc[0, "Distance(km)"] = dist

      # Safe assignment
      if f"Traffic_{traf}" in row.columns:
        row.loc[0, f"Traffic_{traf}"] = 1
      if f"Weather_{weath}" in row.columns:
        row.loc[0, f"Weather_{weath}"] = 1

      # Use .values to ignore mismatched header strings
      pred_time = model.predict(row.values)[0]
      surge_mult = 1.35 if traf == "Jam" else 1.0
      payout = (100 + (pred_time * 4) + (dist * 20)) * surge_mult

      simulated_orders.append({
          "Order_ID": f"GLV-{np.random.randint(1000, 9999)}",
          "Zone": loc["zone"],
          "Distance (km)": round(dist, 1),
          "Traffic": traf,
          "Predicted ETA (mins)": round(pred_time, 1),
          "Courier Payout (KES)": round(payout, 2),
          "lat": loc["lat"] + np.random.uniform(-0.01, 0.01),
          "lon": loc["lon"] + np.random.uniform(-0.01, 0.01),
      })

    df_sim = pd.DataFrame(simulated_orders)

    # Display live feed in app
    with live_placeholder.container():
      st.dataframe(
          df_sim[
              [
                  "Order_ID",
                  "Zone",
                  "Distance (km)",
                  "Traffic",
                  "Predicted ETA (mins)",
                  "Courier Payout (KES)",
              ]
          ],
          use_container_width=True,
      )

    # Display live map tracking order locations
    with map_placeholder.container():
      st.map(df_sim[["lat", "lon"]], zoom=12)

    # Refresh interval to simulate real streaming events
    time.sleep(3)
