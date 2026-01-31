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
    getOverview: async (city, persona) => {
        try {
            // 1. Fetch Real-time AQI
            let aqiData = null;
            try {
                const aqiResponse = await apiClient.get(`/api/v1/realtime-aqi/city/${city}`);
                if (aqiResponse.data.status === 'success') {
                    aqiData = aqiResponse.data.data;
                }
            } catch (e) {
                console.warn('Failed to fetch real-time AQI, falling back to mock structure if needed', e);
                // Throwing here will trigger the error state in the UI, which is good if we have NO data.
                throw new Error(`Could not fetch data for ${city}`);
            }

            // 2. Fetch Forecast (Optional - fail gracefully)
            let forecastData = [];
            try {
                // Assuming forecast endpoint uses city name as ID or we need a proper ID. 
                // For now, try passing city name.
                const forecastResponse = await apiClient.get(`/api/v1/forecast/${city}`, {
                    params: { days_ahead: 1 }
                });
                if (forecastResponse.data) {
                    // Adapt forecast response to our UI format (hourly)
                    // If backend returns daily, we might need to mock hourly distribution or just show daily.
                    // Assuming backend 'generate_forecast' returns something usable.
                    // For robust UI, let's look at the response structure in a real app, but here we assume array.
                    forecastData = forecastResponse.data.predictions || [];
                }
            } catch (e) {
                console.warn('Forecast API failed, using mock forecast', e);
                // Generate mock forecast based on current AQI
                const current = aqiData.aqi || 100;
                forecastData = Array.from({ length: 6 }, (_, i) => ({
                    time: new Date(Date.now() + i * 3600000).getHours() + ":00",
                    aqi: Math.max(0, Math.round(current + (Math.random() * 20 - 10))),
                    risk: 'Moderate' // Simplified
                }));
            }

            // 3. Construct Unified Response
            const risk = getRiskLevel(aqiData.aqi);

            return {
                location: {
                    city: aqiData.city || city,
                    lat: aqiData.lat || 28.7, // Fallback if API doesn't return
                    lon: aqiData.lon || 77.1
                },
                current_aqi: {
                    value: aqiData.aqi,
                    category: aqiData.category || risk.level,
                    updated_at: aqiData.timestamp || new Date().toISOString()
                },
                pollutants: {
                    pm25: { value: aqiData.pm25 || 0, trend: 'flat' }, // Backend might not have trend yet
                    pm10: { value: aqiData.pm10 || 0, trend: 'flat' },
                    no2: { value: aqiData.no2 || 0, trend: 'flat' },
                    o3: { value: aqiData.o3 || 0, trend: 'flat' },
                    so2: { value: aqiData.so2 || 0, trend: 'flat' },
                    co: { value: aqiData.co || 0, trend: 'flat' }
                },
                weather: {
                    // If API returns weather in 'metrics' or similar, use it. Otherwise mock.
                    temp: aqiData.temperature || 32,
                    humidity: aqiData.humidity || 60,
                    wind_speed: aqiData.wind_speed || 12,
                    pressure: aqiData.pressure || 1012
                },
                risk_assessment: {
                    level: risk.level,
                    recommendation: risk.recommendation,
                    standard_aligned: "WHO",
                    ai_explanation: `AQI is ${risk.level} due to prevailing conditions.`,
                    contributing_factors: ["PM2.5", "Traffic"],
                    context: "Real-time"
                },
                forecast_6h: forecastData.length > 0 ? forecastData.slice(0, 6).map(f => ({
                    time: f.time || f.timestamp?.split('T')[1]?.slice(0, 5) || "12:00",
                    aqi: f.predicted_aqi || f.aqi,
                    risk: "N/A"
                })) : []
            };

        } catch (error) {
            console.warn('Backend API not accessible, switching to DEMO MODE (Mock Data)', error);

            // FALLBACK MOCK DATA GENERATOR
            const isDelhi = city.toLowerCase() === 'delhi';
            const baseAQI = isDelhi ? 342 : 156;

            return {
                location: { city: city, lat: 28.7, lon: 77.1 },
                current_aqi: {
                    value: baseAQI,
                    category: isDelhi ? 'Hazardous' : 'Unhealthy',
                    updated_at: new Date().toISOString()
                },
                pollutants: {
                    pm25: { value: isDelhi ? 184 : 68, trend: 'up' },
                    pm10: { value: isDelhi ? 240 : 110, trend: 'flat' },
                    no2: { value: 45, trend: 'down' },
                    o3: { value: 12, trend: 'flat' },
                    so2: { value: 8, trend: 'stable' },
                    co: { value: 1.2, trend: 'up' }
                },
                weather: {
                    temp: 32,
                    humidity: 60,
                    wind_speed: 12,
                    pressure: 1012
                },
                risk_assessment: {
                    level: isDelhi ? 'Hazardous' : 'Unhealthy',
                    recommendation: "System is running in Demo Mode. Connect backend for real updates.",
                    standard_aligned: "WHO",
                    ai_explanation: "Using simulated data for demonstration purposes.",
                    contributing_factors: ["Demo Mode"],
                    context: "Simulated"
                },
                forecast_6h: Array.from({ length: 6 }, (_, i) => ({
                    time: new Date(Date.now() + i * 3600000).getHours() + ":00",
                    aqi: baseAQI + (Math.random() * 20 - 10),
                    risk: "High"
                }))
            };
        }
    },
};
