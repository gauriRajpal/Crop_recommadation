import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import json


# Load model and columns
model = joblib.load("crop_yield_model.pkl")
input_columns = joblib.load("model_input_columns.pkl")

st.set_page_config(layout="wide")
st.title("🌾 Crop Yield Prediction App")

# Crop selection
crop = st.selectbox("Select Crop", ["chickpea", "cotton", "maize", "rice"])

# Input features
st.subheader("🧪 Soil and Weather Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    N = st.number_input("Nitrogen (kg/ha)", 0, 200, 90)
    P = st.number_input("Phosphorus (kg/ha)", 0, 200, 40)
    K = st.number_input("Potassium (kg/ha)", 0, 200, 40)
with col2:
    pH = st.number_input("Soil pH", 0.0, 14.0, 6.5)
    rainfall = st.number_input("Rainfall (mm)", 0, 3000, 1000)
    temperature = st.number_input("Temperature (°C)", 0.0, 50.0, 27.0)
with col3:
    humidity = st.number_input("Humidity (%)", 0.0, 100.0, 75.0)
    wind = st.number_input("Wind Speed (m/s)", 0.0, 10.0, 2.5)
    radiation = st.number_input("Solar Radiation (MJ/m²/day)", 0.0, 30.0, 18.0)

# One-hot encoding of crop
crop_features = {col: 0 for col in input_columns if col.startswith("Crop_")}
crop_features[f"Crop_{crop}"] = 1

# Combine all features
features = {
    'N': N, 'P': P, 'K': K,
    'pH': pH, 'Rainfall_mm': rainfall,
    'temp': temperature, 'humidity': humidity,
    'wind': wind, 'radiation': radiation,'Area_ha':1.0,
    **crop_features
}

# Predict button
if st.button("🌾 Predict Yield"):
    input_df = pd.DataFrame([features])[input_columns]
    prediction = model.predict(input_df)[0]
    st.success(f"🌱 Expected Yield: **{prediction:.2f} kg/hectare**")

# Optional: Map view
st.markdown("---")
st.subheader("🗺️ Predicted Crop Yield by State")

# Example dummy data (replace this with real state-wise predictions if available)
# You can precompute average yield per crop per state from your dataset
# -----------------------------------------------
# 🗺️ Dynamic Crop-Wise Yield Map from Training Data
# -----------------------------------------------

# Load training dataset
@st.cache_data
def load_training_data():
    df = pd.read_csv("../Data/cleaned.csv")  # Replace with your actual file name
    return df

df = load_training_data()

# Clean and prepare data
df = df[['State Name', 'Crop', 'yield']]
df.dropna(inplace=True)

# Group by Crop and State to get average yields
avg_yield_df = df.groupby(['Crop', 'State Name'], as_index=False).mean()

# Filter only for selected crop
selected_crop_df = avg_yield_df[avg_yield_df['Crop'].str.lower() == crop.lower()]

# Get all state names from GeoJSON
with open("india_states.json", "r", encoding="utf-8") as f:
    geojson = json.load(f)

all_states = [f["properties"]["name"] for f in geojson["features"]]

# Merge with full state list to show all states on map
map_df = pd.DataFrame({"State Name": all_states})
map_df = map_df.merge(selected_crop_df, on="State Name", how="left")
map_df["yield"] = map_df["yield"].fillna(0)

# Plot map
fig = px.choropleth(
    map_df,
    geojson=geojson,
    locations="State Name",
    color="yield",
    featureidkey="properties.name",
    color_continuous_scale="YlGn",
    title=f"State-wise Average Yield for {crop.title()}"
)

fig.update_traces(marker_line_width=0.5, marker_line_color="black")

fig.update_geos(
    fitbounds="locations",
    visible=True,
    showland=True,
    landcolor="white",
    showocean=False,
    showcountries=False,
    projection_type="mercator"
)

fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)
