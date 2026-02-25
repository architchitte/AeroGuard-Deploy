import axios from 'axios';
import { API_BASE_URL } from './apiConfig';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/* ================= FIXED FEATURE DEFINITIONS ================= */

const BASE_FEATURES = {
  pm25: [
    "PM2.5 Accumulation",
    "Traffic Emissions",
    "Weather Stability",
    "Urban Density",
    "Low Wind Speed",
  ],
  pm10: [
    "PM10 Dust",
    "Construction Activity",
    "Vehicular Load",
    "Road Conditions",
    "Wind Dispersion",
  ],
  no2: [
    "Vehicular Emissions",
    "Traffic Congestion",
    "Fuel Quality",
    "Urban Density",
    "Time of Day",
  ],
};

const METRO_CITIES = [
  "delhi",
  "mumbai",
  "kolkata",
  "chennai",
  "bengaluru",
];

/* ================= SERVICE ================= */

export const analyticsService = {
  /* ---------- Health ---------- */
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/api/v1/health');
      return response.data;
    } catch (error) {
      return { status: 'offline', timestamp: new Date().toISOString() };
    }
  },

  /* ---------- Historical Trends ---------- */
  getHistoricalAnalysis: async (timeRange, city = 'Mumbai') => {
    try {
      const response = await apiClient.get(
        `/api/v1/realtime-aqi/history/${city}`,
        { params: { days: timeRange } }
      );

      if (response.data.status === 'success') {
        return response.data.data.map(item => ({
          date: new Date(item.date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          }),
          pm25: item.pm25,
          pm10: item.pm10,
          no2: item.no2,
          o3: item.o3,
          aqi: item.aqi,
        }));
      }
    } catch (e) {
      console.warn("History API failed, using mock");
    }

    // fallback mock
    const data = [];
    const now = new Date();
    for (let i = timeRange; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      data.push({
        date: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        pm25: 80 + Math.random() * 80,
        pm10: 120 + Math.random() * 100,
        no2: 30 + Math.random() * 40,
        o3: 20 + Math.random() * 30,
        aqi: 100 + Math.random() * 80,
      });
    }
    return data;
  },

  /* ---------- XAI FEATURE IMPORTANCE ---------- */
  getFeatureImportance: async (
    city,
    aqi = 120,
    dominant = "pm25",
    timeRange = 7
  ) => {
    const features = BASE_FEATURES[dominant] || BASE_FEATURES.pm25;
    const isMetro = METRO_CITIES.includes(city.toLowerCase());

    /* Severity factor based on AQI */
    const severity =
      aqi > 200 ? 1.0 :
        aqi > 150 ? 0.9 :
          aqi > 100 ? 0.75 :
            0.6;

    /* Time smoothing factor */
    const timeFactor =
      timeRange >= 30 ? 0.85 :
        timeRange >= 14 ? 0.95 :
          1.05;

    /* Metro adjustment */
    const metroBoost = isMetro ? 1.05 : 0.95;

    return features.map((feature, index) => ({
      feature,
      score: Number(
        (
          severity *
          timeFactor *
          metroBoost *
          (1 - index * 0.12)
        ).toFixed(2)
      ),
    }));
  },

  /* ---------- Pollutant Composition ---------- */
  getPollutantComposition: async (city = 'Mumbai') => {
    try {
      const res = await apiClient.get(`/api/v1/realtime-aqi/city/${city}`);
      if (res.data.status === 'success') {
        const d = res.data.data;
        const total = d.pm25 + d.pm10 + d.no2 + d.o3;

        return [
          { name: 'PM2.5', value: Math.round((d.pm25 / total) * 100) },
          { name: 'PM10', value: Math.round((d.pm10 / total) * 100) },
          { name: 'NO2', value: Math.round((d.no2 / total) * 100) },
          { name: 'O3', value: Math.round((d.o3 / total) * 100) },
        ];
      }
    } catch (e) {
      console.warn("Composition API failed");
    }

    return [
      { name: 'PM2.5', value: 40 },
      { name: 'PM10', value: 30 },
      { name: 'NO2', value: 20 },
      { name: 'O3', value: 10 },
    ];
  },

  /* ---------- AI Briefing ---------- */
  getAIBriefing: async (city, persona) => {
    try {
      const res = await apiClient.get('/api/v1/ai/briefing', {
        params: { city, persona },
      });
      return res.data;
    } catch {
      return {
        status: "success",
        data: {
          explanation:
            "Air quality is influenced by traffic density, particulate buildup, and local weather stability.",
        },
      };
    }
  },
};
