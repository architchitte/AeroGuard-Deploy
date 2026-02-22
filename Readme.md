# 🌍 AeroGuard — AI-Powered Air Quality Intelligence Platform

AeroGuard is a **full-stack, AI-driven air quality monitoring and intelligence platform** that delivers **real-time AQI data, pollutant breakdowns, predictive analytics, interactive heatmaps, and AI-generated health insights** with a modern, cinematic UI.

This project demonstrates **real-world system design**, **API integration**, **data normalization**, and **advanced frontend visualization**.

---

## 🚀 Key Features

### 🌫️ Real-Time Air Quality Monitoring
- Live AQI data via **WAQI (World Air Quality Index) API**
- Support for **100+ major Indian cities** and towns
- Automatic fallback to **realistic mock data** for development

### 🧪 Pollutant Analysis
- PM2.5, PM10, NO₂, O₃, SO₂, CO
- Safe-limit comparison with severity indicators
- Dynamic data normalization across diverse sensory inputs

### 🗺️ Interactive Pollution Heatmap
- **India-Bounded Visualization**: Data points are geographically restricted to the Indian subcontinent.
- **Smooth Gradient Mapping**: Replaces cluttered markers with a clean, cinematic heatmap gradient.
- **Optimized Rendering**: Fine-tuned radius and blur settings prevent visual artifacts and ensure smooth blending.

### 📈 Predictive Analytics
- **Short-term AQI forecasting** using integrated sensory trends.
- Smooth Recharts visualization for trend analysis.

### 🤖 AI Intelligence
- AI-generated AQI briefings and risk interpretation.
- Persona-aware messaging (General / Vulnerable / Outdoor).

---

## 🛠️ How it Works Right Now

1.  **Data Ingestion**: The backend serves as a proxy to the WAQI API, fetching data for a curated list of over 100 high-traffic locations across India.
2.  **Normalization**: Raw data is parsed and mapped to a standard US-EPA AQI scale (0-500) to ensure consistent interpretation across the UI.
3.  **Heatmap Generation**: The frontend map component periodically polls for nationwide updates and uses a high-performance Leaflet Heatmap layer to render intensity without the visual clutter of individual markers.
4.  **Geographic Gating**: Points are filtered against a specific latitude/longitude bounding box to focus exclusively on the Indian region.

---

## 🔮 Future Scope

- **📍 Hyper-Local Sensor Integration**: Supporting low-cost IoT sensor networks for street-level granularity beyond official stations.
- **📅 Historical Deep-Dives**: Long-term data storage to analyze seasonal pollution trends and policy impact.
- **📱 Native Mobile Ecosystem**: Cross-platform mobile apps with push-notifications for high-pollution alerts.
- **🌦️ Meteorological Correlation**: Integrating weather patterns (wind speed, humidity) to improve forecasting accuracy.
- **🩺 Health Integration**: Connecting with health wearables to provide proactive advice based on real-time exposure.
---

## 🔌 API Endpoints

### Get AQI by City
GET `/api/v1/realtime-aqi/city/<city_name>`

### Get AQI by Coordinates
GET `/api/v1/realtime-aqi/coordinates?latitude=..&longitude=..`

### Nationwide Data (Heatmap)
GET `/api/v1/realtime-aqi/nationwide`

---

## ⚙️ Environment Variables

### Backend (`.env`)
```env
REALTIME_WAQI_API_KEY=your_waqi_api_key_here
REALTIME_WAQI_BASE_URL=https://api.waqi.info 
```

### Frontend (`.env`)
```env
VITE_API_BASE_URL=http://localhost:5000
```

---

## 🚀 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/aeroguard.git
   cd aeroguard
   ```

2. **Backend Setup**
   ```bash
   cd Backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-fixed.txt
   python run.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
