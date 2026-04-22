import axios from 'axios';
import { API_BASE_URL } from './apiConfig';

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
                const endpoint = (lat != null && lon != null)
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
            let components = null;
            let modelsWarmingUp = false;
            try {
                // Generate a dummy 7x11 feature payload for the ML ensemble
                const dummyFeatures = Array.from({ length: 7 }, () => Array(11).fill(0.5));
                const forecastResponse = await apiClient.post(`/api/v1/forecast/`, {
                    features: dummyFeatures
                });
                if (forecastResponse.data) {
                    // Extract predictions based on new response schema
                    const aqiForecast = forecastResponse.data.forecasts?.AQI || 100;
                    components = forecastResponse.data.components;
                    
                    // The dashboard expects an hourly array (forecast_8h), we mock it using the ensemble output
                    forecastData = Array.from({ length: 8 }, (_, i) => ({
                        time: new Date(Date.now() + i * 3600000).getHours() + ":00",
                        aqi: Math.max(0, Math.round(aqiForecast + (Math.random() * 10 - 5))),
                        risk: getRiskLevel(aqiForecast).level
                    }));
                }
            } catch (e) {
                if (e.response && e.response.status === 503) {
                    console.warn("ML Models are warming up (Cold Start). Showing loading state...");
                    modelsWarmingUp = true;
                } else {
                    console.warn('Forecast API failed, using mock forecast', e);
                }
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
                    city: (typeof aqiData?.city === 'object' ? aqiData?.city?.name : aqiData?.city) || aqiData?.station || city,
                    lat: aqiData?.lat || lat || 28.7,
                    lon: aqiData?.lon || lon || 77.1
                },
                current_aqi: {
                    value: currentVal,
                    category: aqiData?.category || risk.level,
                    updated_at: aqiData?.timestamp || new Date().toISOString()
                },
                pollutants: Object.fromEntries(Object.entries(aqiData?.iaqi || {}).map(([key, val]) => [
                    key,
                    { value: val.v ?? val, trend: "flat" }
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
                })) : [],
                models_warming_up: modelsWarmingUp,
                model_components: components
            };

        } catch (error) {
            console.error('Data flow failed:', error);
            throw error; // Let the hook/UI handle the actual error state
        }
    },
};
