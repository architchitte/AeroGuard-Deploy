# 🌍 AeroGuard — AI-Powered Air Quality Intelligence

AeroGuard is a **cinematic, AI-driven atmospheric intelligence platform** designed to transform invisible air pollution data into actionable health insights. Built for the **AIColegion Hackathon 2026 (VESIT)**, it combines real-time sensory data with machine learning to predict, explain, and guard against environmental threats across India.

---

## 🚀 Core Features

### 🔮 Predictive Intelligence
- **6-Hour AQI Forecast**: Uses machine learning to predict atmospheric trajectory.
- **Explainable AI (X-AI)**: Transparently shows which pollutants (PM2.5, NO₂, etc.) are driving the forecast using feature importance scores.

### 🛡️ Personalized Health Guard
- **Persona-Aware Assessments**: Tailored health logic for the General Public, Children/Elderly, and Athletes.
- **AI Briefings**: Human-readable explanations of current conditions and protective protocols.

### 🗺️ Cinematic Live Heatmap
- **Nationwide Coverage**: Real-time AQI visualization across **45+ major Indian cities** and a high-density **10x10 regional grid scan**.
- **Smooth Gradient Rendering**: Advanced Heatmap implementation for a professional, "vibrant" aesthetic.
- **Geographically Bounded**: Precisely calibrated for the Indian subcontinent.

### 📊 Professional Analytics
- **Historical Deep-Dives**: 7-to-30 day trend analysis for multi-pollutant tracking.
- **Intelligent Search**: Fuzzy location matching with geometric bounding for India-only results.

---

## 🔮 Future Scope & "Student Scale" Reality

### Limitations (The Student Scale)
- **API Constraints**: Currently relies on the WAQI API standard tier which has rate limits (2,000 requests/minute). Full-scale commercial deployment would require a professional tier.
- **Hosting**: Designed as a local-first development project; scalable cloud hosting (AWS/GCP) for the ML models and data ingestion is planned for post-competition.
- **Sensor Density**: While we use 250+ official stations, hyper-local street-level data is currently limited by public station availability.

### Future Roadmap
- **📍 DIY IoT Integration**: Support for low-cost PM2.5 sensors (ESP32/Arduinos) for community-driven data.
- **📱 Mobile Ecosystem**: Cross-platform Flutter/React Native app with "High Pollution" push alerts based on live location.
- **🌦️ Met-AI Sync**: Integrating real-time wind speed and humidity from OpenWeatherMap to improve 24h forecasting.

---

## 📁 File Structure

```text
AeroGuard/
├── Backend/                 # Flask / FastAPI Architecture
│   ├── app/
│   │   ├── routes/          # API Blueprints (AI, AQI, Forecast, Risk)
│   │   ├── services/        # Business Logic & ML Service Layer
│   │   └── utils/           # Shared helpers & Error Handlers
│   └── run.py               # Main Entry Point
├── frontend/                # React / Vite Infrastructure
│   ├── src/
│   │   ├── Components/      # Complex UI (Heatmap, Analytics, Search)
│   │   ├── pages/           # High-level Views (Dashboard, Risk, Landing)
│   │   └── api/             # Frontend API Utilities
│   └── package.json
└── Readme.md
```

---

## 🔌 API Documentation

### Real-time AQI
- `GET /api/v1/realtime-aqi/city/<city_name>`: Fetch live data for a city.
- `GET /api/v1/realtime-aqi/nationwide`: High-density data points for the heatmap.
- `GET /api/v1/realtime-aqi/token`: Securely proxy WAQI tokens to the frontend.

### AI Intelligence
- `GET /api/v1/ai/briefing?city=...&persona=...`: Generate personalized AI health advice.
- `POST /api/v1/ai/explain-forecast`: ML feature importance explanation.

### Health & Risk
- `GET /api/v1/health-risk`: Multi-factor persona-based risk assessment.

---

## ⚙️ How to Run

### 1. Backend Setup
```bash
cd Backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Dependencies
pip install -r requirements-fixed.txt
# Run
python run.py
```
*Note: Ensure `REALTIME_WAQI_API_KEY` is set in your `.env`.*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🤝 Collaborators

Built with ❤️ by **Team 70 — CultBoyz** for **AIColegion 2026** @ **VESIT (Vivekanand Education Society's Institute of Technology)**.

<table align="center">
  <tr>
    <td align="center">
      <img src="https://github.com/anshul.png" width="100px;" alt="Anshul Patil"/><br />
      <sub><b>Anshul Patil</b></sub><br />
      <sub>Frontend Design &<br/>API Integration</sub>
    </td>
    <td align="center">
      <img src="https://github.com/archit.png" width="100px;" alt="Archit Chitte"/><br />
      <sub><b>Archit Chitte</b></sub><br />
      <sub>Backend, ML Models &<br/>Model Integration</sub>
    </td>
  </tr>
</table>

---
*© 2026 AeroGuard Intelligence. Part of the CultBoyz hackathon suite.*
