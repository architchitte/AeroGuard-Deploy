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
- **API Constraints**: Currently relies on the WAQI API which has a default programmatic quota of **1,000 requests per minute** (with bursts up to 60 requests). Full-scale commercial deployment would require a dedicated institutional agreement.
- **Hosting**: Designed as a local-first development project; scalable cloud hosting (AWS/GCP) for the ML models and data ingestion is planned for post-competition.
- **Sensor Density**: While we use 250+ official stations, hyper-local street-level data is currently limited by public station availability.

### Future Roadmap
- **📍 DIY IoT Integration**: Support for low-cost PM2.5 sensors (ESP32/Arduinos) for community-driven data.
- **📱 Mobile Ecosystem**: Cross-platform Flutter/React Native app with "High Pollution" push alerts based on live location.
- **🌦️ Met-AI Sync**: Integrating real-time wind speed and humidity from OpenWeatherMap to improve 24h forecasting.

---

## 📁 File Structure

```text
AeroGuard-Deploy/
├── AeroGuard-Backend/       # FastAPI service (deployed to Render)
│   ├── app/
│   │   ├── api/routers/     # API routes (AI, AQI, Forecast, Risk, Analytics)
│   │   ├── core/config.py   # Env-driven settings
│   │   ├── ml/              # Inference engine + trained artifacts
│   │   ├── schemas/         # Pydantic models
│   │   ├── services/        # Business logic & external API clients
│   │   └── main.py          # FastAPI entry point
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # React / Vite app (deployed to Vercel)
│   ├── src/
│   │   ├── Components/      # Complex UI (Heatmap, Analytics, Search)
│   │   ├── pages/           # High-level Views (Dashboard, Risk, Landing)
│   │   └── api/             # Frontend API Utilities
│   ├── vercel.json
│   └── .env.example
├── render.yaml              # Render Blueprint for the backend
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

### 1. Backend Setup (Python 3.11)
```bash
cd AeroGuard-Backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
# Dependencies
pip install -r requirements.txt
# Configure (then fill in your API keys)
cp .env.example .env
# Run
uvicorn app.main:app --reload --port 8000
```
*Note: `REALTIME_AQI_API_KEY` and `NVIDIA_QWEN_API_KEY` are required — the server will not start without them.* Interactive docs are served at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
On `localhost` the frontend talks to `http://localhost:8000` automatically.

---

## 🚀 Deployment

### Backend → Render
1. In Render, choose **New → Blueprint** and select this repository. `render.yaml` configures the service (`rootDir: AeroGuard-Backend`, Python 3.11, health check on `/`).
2. Fill in the secret environment variables when prompted:
   - `REALTIME_AQI_API_KEY` — WAQI token
   - `NVIDIA_QWEN_API_KEY` — NVIDIA NIM key
   - `CORS_ORIGINS` — comma-separated frontend origins, e.g. `https://your-app.vercel.app`
3. Deploy. `SECRET_KEY` / `JWT_SECRET_KEY` are generated automatically.

> TensorFlow + XGBoost need roughly 1 GB of RAM at runtime; Render's free 512 MB instance may run out of memory. Use the *Starter* plan or larger if you see OOM restarts.

**Docker alternative** (Railway, Fly.io, Cloud Run, etc.):
```bash
cd AeroGuard-Backend
docker build -t aeroguard-api .
docker run -p 8000:8000 --env-file .env aeroguard-api
```

### Frontend → Vercel
1. Import the repository in Vercel and set **Root Directory** to `frontend` (framework preset: Vite).
2. Set `VITE_API_BASE_URL` to your backend URL (defaults to `https://aeroguard-deploy.onrender.com` if unset).
3. Deploy. `vercel.json` rewrites all routes to `index.html` for client-side routing.
4. Add the resulting Vercel URL to the backend's `CORS_ORIGINS`.

---

## 🤝 Collaborators

Built with ❤️ by **Team 70 — CultBoyz** for **AIColegion 2026** @ **VESIT (Vivekanand Education Society's Institute of Technology)**.

<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/anshulpdev10">
        <img src="https://avatars.githubusercontent.com/anshulpdev10?v=4" width="100px;" alt="Anshul Patil"/><br />
        <sub><b>Anshul Patil</b></sub>
      </a><br />
      <sub>Frontend Design &<br/>API Integration</sub>
    </td>
    <td align="center">
      <a href="https://github.com/architchitte">
        <img src="https://avatars.githubusercontent.com/architchitte?v=4" width="100px;" alt="Archit Chitte"/><br />
        <sub><b>Archit Chitte</b></sub>
      </a><br />
      <sub>Backend, ML Models &<br/>Model Integration</sub>
    </td>
  </tr>
</table>

---
*© 2026 AeroGuard Intelligence. Part of the CultBoyz hackathon suite.*
