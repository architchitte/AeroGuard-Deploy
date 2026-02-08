# 🌍 AeroGuard — AI-Powered Air Quality Intelligence Platform

AeroGuard is a **full-stack, AI-driven air quality monitoring and intelligence platform** that delivers **real-time AQI data, pollutant breakdowns, predictive analytics, interactive heatmaps, and AI-generated health insights** with a modern, cinematic UI.

This project demonstrates **real-world system design**, **API integration**, **data normalization**, and **advanced frontend visualization**.

---

## 🚀 Key Features

### 🌫️ Real-Time Air Quality Monitoring
- Live AQI data via **WAQI (World Air Quality Index) API**
- City-based and coordinate-based AQI lookup
- Automatic fallback to **realistic mock data**

### 🧪 Pollutant Analysis
- PM2.5, PM10, NO₂, O₃, SO₂, CO
- Safe-limit comparison with severity indicators
- Backend → Frontend key normalization handled safely

### 🗺️ Interactive Pollution Heatmap
- City-level AQI heatmap
- AQI-based color scaling
- Optimized layering (no click-blocking UI bugs)

### 📈 Predictive Analytics
- **6-hour AQI forecast**
- Smooth Recharts visualization
- Dynamic theming based on AQI severity

### 🤖 AI Intelligence
- AI-generated AQI briefings
- Risk interpretation based on pollution levels
- Persona-aware messaging (General / Vulnerable / Outdoor)

### ❤️ Personalized Health Advice
- AQI-aware health guidance
- Clear non-medical disclaimer
- Designed for real-world usability

### 🎨 Premium UI / UX
- Glassmorphism design
- Animated gradients & glow effects
- Framer Motion animations
- Fully responsive layout

---


---

## 🛠️ Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS
- Framer Motion
- Recharts
- Lucide Icons
- Axios

### Backend
- Python (Flask)
- Requests
- WAQI API
- Environment-based configuration

---

## 🔌 API Endpoints

### Get AQI by City

---

## 🛠️ Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS
- Framer Motion
- Recharts
- Lucide Icons
- Axios

### Backend
- Python (Flask)
- Requests
- WAQI API
- Environment-based configuration

---

## 🔌 API Endpoints

### Get AQI by City
GET /api/v1/realtime-aqi/city/<city_name>


### Get AQI by Coordinates
GET /api/v1/realtime-aqi/coordinates?latitude=..&longitude=..


### Popular Indian Cities
GET /api/v1/realtime-aqi/popular-cities


### Health Check
GET /api/v1/realtime-aqi/health

---

## 🔁 Data Normalization Strategy

Backend responses may return pollutants in **multiple formats**:

```json
{
  "pm25": 78,
  "pm10": 120
}
{
  "PM2.5": 78,
  "PM10": 120
}

value: typeof val === "object" ? val.value : val

⚙️ Environment Variables

Backend (.env)

REALTIME_AQI_API_KEY=your_waqi_api_key_here
REALTIME_AQI_BASE_URL=https://api.waqi.info

Frontend (.env)

VITE_API_BASE_URL=http://localhost:5000


**How to Run the Project**

1️⃣ Clone the Repository

git clone https://github.com/your-username/aeroguard.git
cd aeroguard

2️⃣ Backend Setup

cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py


Backend will run on:

http://localhost:5000

3️⃣ Frontend Setup

cd frontend
npm install
npm run dev


Frontend will run on:

http://localhost:5173
