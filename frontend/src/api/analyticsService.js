import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const analyticsService = {
    // Check if Analytics Microservice is healthy
    checkHealth: async () => {
        try {
            const response = await apiClient.get('/api/v1/models/health');
            return response.data;
        } catch (error) {
            console.warn('Analytics Service Health Check Failed', error);
            return { status: 'offline', timestamp: new Date().toISOString() };
        }
    },

    // Get available models for comparison
    getAvailableModels: async () => {
        try {
            const response = await apiClient.get('/api/v1/models/available-models');
            return response.data.data.available_models;
        } catch (error) {
            console.warn('Failed to fetch available models', error);
            // Fallback data
            return [
                { name: 'SARIMA', type: 'Statistical', description: 'Offline Mode Estimate' },
                { name: 'XGBoost', type: 'ML', description: 'Offline Mode Estimate' }
            ];
        }
    },

    // Compare models (Quick version)
    compareModels: async (targetCol = 'PM2.5') => {
        try {
            // In a real app, we would post real historical data here.
            // For this "Connect" phase, we'll try to trigger a demo comparison if the backend supports it,
            // or just Mock it if the backend requires a huge payload we don't have handy.
            return null;
        } catch (error) {
            return null;
        }
    },

    // --- NEW METHODS FOR ADVANCED ANALYTICS ---

    // 1. Get Historical Trends
    getHistoricalAnalysis: async (timeRange) => {
        try {
            // Simulate API call for now as backend requires 'location_id' and setup
            // await apiClient.get(`/api/v1/forecast/Delhi?days_ahead=${timeRange}`);
            throw new Error("Simulate Mock");
        } catch (error) {
            // Fallback to Mock Data Generator
            const data = [];
            const now = new Date();
            for (let i = timeRange; i >= 0; i--) {
                const date = new Date(now);
                date.setDate(date.getDate() - i);
                data.push({
                    date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    pm25: Math.floor(Math.random() * 150) + 50,
                    pm10: Math.floor(Math.random() * 200) + 80,
                    no2: Math.floor(Math.random() * 80) + 20,
                    o3: Math.floor(Math.random() * 60) + 10,
                });
            }
            return new Promise(resolve => setTimeout(() => resolve(data), 600));
        }
    },

    // 2. Get Model Comparison Metrics
    getModelMetrics: async (horizon) => {
        // Mock Different metrics based on horizon
        const baseMetrics = {
            sarima: { prediction: 145, mae: 12.4, rmse: 15.2, r2: 0.82, uncertainty: 15 },
            xgboost: { prediction: 142, mae: 8.5, rmse: 10.1, r2: 0.89, uncertainty: 8 },
            hybrid: { prediction: 143, mae: 5.2, rmse: 6.8, r2: 0.94, uncertainty: 5 },
        };

        // Add variance based on horizon
        const modifier = horizon / 6;

        return new Promise(resolve => setTimeout(() => resolve({
            sarima: { ...baseMetrics.sarima, mae: (baseMetrics.sarima.mae * modifier).toFixed(1), rmse: (baseMetrics.sarima.rmse * modifier).toFixed(1) },
            xgboost: { ...baseMetrics.xgboost, mae: (baseMetrics.xgboost.mae * modifier).toFixed(1), rmse: (baseMetrics.xgboost.rmse * modifier).toFixed(1) },
            hybrid: { ...baseMetrics.hybrid, mae: (baseMetrics.hybrid.mae * modifier).toFixed(1), rmse: (baseMetrics.hybrid.rmse * modifier).toFixed(1) },
        }), 400));
    },

    // 3. Pollutant Composition
    getPollutantComposition: async () => {
        return new Promise(resolve => setTimeout(() => resolve([
            { name: 'PM2.5', value: 45, color: '#f43f5e' },
            { name: 'PM10', value: 30, color: '#f97316' },
            { name: 'NO2', value: 15, color: '#eab308' },
            { name: 'O3', value: 10, color: '#14b8a6' },
        ]), 300));
    },

    // Get Feature Importance for a parameter
    getFeatureImportance: async (parameter = 'PM2.5') => {
        try {
            const response = await apiClient.get(`/api/v1/model/${parameter}/feature-importance`);
            return response.data.importance;
        } catch (error) {
            console.warn(`Failed to fetch feature importance for ${parameter}, using fallback`, error);
            return [
                { feature: "Previous AQI (t-1)", score: 0.85 },
                { feature: "Wind Speed", score: 0.62 },
                { feature: "Traffic Density", score: 0.58 },
                { feature: "Humidity", score: 0.45 },
                { feature: "Hour of Day", score: 0.38 },
            ];
        }
    }
};
