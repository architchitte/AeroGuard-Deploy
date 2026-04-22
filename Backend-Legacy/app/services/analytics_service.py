from datetime import datetime
import random

URBAN_CITIES = ["Delhi", "Gurgaon", "Noida", "Mumbai", "Bangalore", "Chennai"]
COASTAL_CITIES = ["Mumbai", "Chennai", "Kochi"]
INDUSTRIAL_CITIES = ["Bhiwadi", "Ankleshwar", "Panipat"]

def get_location_type(city: str):
    if city in COASTAL_CITIES:
        return "coastal"
    if city in INDUSTRIAL_CITIES:
        return "industrial"
    return "urban"

def generate_xai(city: str, current_aqi: int):
    """
    Rule-based Explainable AI (XAI)
    Dynamically changes by city, AQI & time
    """

    hour = datetime.now().hour
    location_type = get_location_type(city)

    # ---- Base weights ----
    weights = {
        "Prev AQI (t-1)": 0.30,
        "PM Load": 0.25,
        "Wind Dispersion": 0.20,
        "Relative Humidity": 0.15,
        "Time of Day": 0.10,
    }

    # ---- AQI severity rules ----
    if current_aqi > 200:
        weights["Prev AQI (t-1)"] += 0.15
        weights["PM Load"] += 0.15
        weights["Wind Dispersion"] -= 0.10

    elif current_aqi < 80:
        weights["Wind Dispersion"] += 0.15
        weights["Time of Day"] += 0.10

    # ---- Location rules ----
    if location_type == "coastal":
        weights["Wind Dispersion"] += 0.15
        weights["Relative Humidity"] += 0.10

    if location_type == "industrial":
        weights["PM Load"] += 0.20
        weights["Prev AQI (t-1)"] += 0.10

    # ---- Time of day rules ----
    if 6 <= hour <= 10:  # Morning traffic
        weights["PM Load"] += 0.15

    if 19 <= hour <= 23:  # Night inversion
        weights["Prev AQI (t-1)"] += 0.15

    # ---- Normalize ----
    total = sum(weights.values())
    xai = [
        {
            "feature": k,
            "score": round(v / total, 3)
        }
        for k, v in weights.items()
    ]

    return sorted(xai, key=lambda x: x["score"], reverse=True)