import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Helper to calculate risk
const getRiskLevel = (aqi) => {
    if (aqi <= 50) return { level: 'Good', recommendation: 'Air quality is satisfactory.' };
    if (aqi <= 100) return { level: 'Moderate', recommendation: 'Sensitive individuals should limit outdoor exertion.' };
    if (aqi <= 150) return { level: 'Unhealthy for Sensitive Groups', recommendation: 'Vulnerable groups should reduce outdoor activity.' };
    if (aqi <= 200) return { level: 'Unhealthy', recommendation: 'Everyone should avoid prolonged outdoor exertion.' };
    if (aqi <= 300) return { level: 'Very Unhealthy', recommendation: 'Avoid all outdoor activities.' };
    return { level: 'Hazardous', recommendation: 'Health warning of emergency conditions.' };
};

export const dashboardService = {
    getOverview: async (city, persona, lat = null, lon = null) => {
        try {
            // 1. Fetch Real-time AQI
            let aqiData = null;
            try {
                // If coordinates are provided, use them for consistency with the heatmap
                const endpoint = (lat && lon)
                    ? `/api/v1/realtime-aqi/coordinates?latitude=${lat}&longitude=${lon}`
                    : `/api/v1/realtime-aqi/city/${city}`;

                const aqiResponse = await apiClient.get(endpoint);
                if (aqiResponse.data.status === 'success') {
                    aqiData = aqiResponse.data.data;
                }
            } catch (e) {
                console.warn('Failed to fetch real-time AQI, falling back to mock structure if needed', e);
                throw new Error(`Could not fetch data for ${city}`);
            }

            // 2. Fetch Forecast (Optional - fail gracefully)
            let forecastData = [];
            try {
                const forecastResponse = await apiClient.get(`/api/v1/forecast/${city}`, {
                    params: { days_ahead: 1 }
                });
                if (forecastResponse.data) {
                    forecastData = forecastResponse.data.predictions || [];
                }
            } catch (e) {
                console.warn('Forecast API failed, using mock forecast', e);
                const current = aqiData?.aqi || 100;
                forecastData = Array.from({ length: 8 }, (_, i) => ({
                    time: new Date(Date.now() + i * 3600000).getHours() + ":00",
                    aqi: Math.max(0, Math.round(current + (Math.random() * 20 - 10))),
                    risk: 'Moderate'
                }));
            }

            // 3. Construct Unified Response
            const currentVal = aqiData?.aqi || 0;
            const risk = getRiskLevel(currentVal);

            return {
                location: {
                    city: aqiData?.station || aqiData?.city || city,
                    lat: aqiData?.lat || lat || 28.7,
                    lon: aqiData?.lon || lon || 77.1
                },
                current_aqi: {
                    value: currentVal,
                    category: aqiData?.category || risk.level,
                    updated_at: aqiData?.timestamp || new Date().toISOString()
                },
                pollutants: Object.fromEntries(Object.entries(aqiData?.pollutants || {}).map(([key, value]) => [
                    key,
                    { value, trend: "flat" }
                ])),
                weather: {
                    temp: aqiData?.temperature || 32,
                    humidity: aqiData?.humidity || 60,
                    wind_speed: aqiData?.wind_speed || 12,
                    pressure: aqiData?.pressure || 1012
                },
                risk_assessment: {
                    level: risk.level,
                    recommendation: risk.recommendation,
                    standard_aligned: "WHO",
                    ai_explanation: `Live station data for ${aqiData?.station || city}.`,
                    contributing_factors: ["PM2.5", "Regional Density"],
                    context: "Real-time"
                },
                forecast_8h: forecastData.length > 0 ? forecastData.slice(0, 8).map(f => ({
                    time: f.time || f.timestamp?.split('T')[1]?.slice(0, 5) || "12:00",
                    aqi: f.predicted_aqi || f.aqi,
                    risk: "N/A"
                })) : []
            };

        } catch (error) {
            console.error('Data flow failed:', error);
            throw error; // Let the hook/UI handle the actual error state
        }
    },
};
