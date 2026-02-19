/**
 * Historical Analysis Service
 * 
 * Integrates with the SARIMA-based historical AQI analysis API
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Get AQI forecast for specified hours
 * @param {string} location - Location name
 * @param {number} hours - Number of hours to forecast (default: 24)
 * @returns {Promise<Object>} Forecast data
 */
export const getForecast = async (location, hours = 24) => {
    try {
        const response = await apiClient.get('/api/v1/historical-analysis/forecast', {
            params: { location, hours }
        });
        return response.data;
    } catch (error) {
        console.error('Forecast API failed:', error);
        return getFallbackForecast(location, hours);
    }
};

/**
 * Get historical trend analysis
 * @param {string} location - Location name
 * @param {number} days - Number of days to analyze (default: 7)
 * @returns {Promise<Object>} Historical analysis data
 */
export const getHistoricalTrends = async (location, days = 7) => {
    try {
        const response = await apiClient.get('/api/v1/historical-analysis/trends', {
            params: { location, days }
        });
        return response.data;
    } catch (error) {
        console.error('Historical trends API failed:', error);
        return getFallbackTrends(location, days);
    }
};

/**
 * Get pattern analysis
 * @param {string} location - Location name
 * @returns {Promise<Object>} Pattern analysis data
 */
export const getPatternAnalysis = async (location) => {
    try {
        const response = await apiClient.get('/api/v1/historical-analysis/patterns', {
            params: { location }
        });
        return response.data;
    } catch (error) {
        console.error('Pattern analysis API failed:', error);
        return getFallbackPatterns(location);
    }
};

/**
 * Fallback forecast when API unavailable
 */
const getFallbackForecast = (location, hours) => {
    const now = new Date();
    const forecast = [];
    
    for (let i = 0; i < hours; i++) {
        const timestamp = new Date(now.getTime() + (i + 1) * 3600000);
        const baseAqi = 100 + Math.sin(i / 4) * 20;
        const variation = Math.random() * 10 - 5;
        const aqi = Math.max(0, baseAqi + variation);
        
        forecast.push({
            timestamp: timestamp.toISOString(),
            hour_offset: i + 1,
            aqi_forecast: Math.round(aqi * 10) / 10,
            lower_bound: Math.round((aqi * 0.8) * 10) / 10,
            upper_bound: Math.round((aqi * 1.2) * 10) / 10
        });
    }
    
    const aqiValues = forecast.map(f => f.aqi_forecast);
    
    return {
        location,
        forecast_hours: hours,
        generated_at: now.toISOString(),
        model_type: 'fallback',
        confidence_level: 0.5,
        forecast,
        summary: {
            average_aqi: Math.round((aqiValues.reduce((a, b) => a + b, 0) / aqiValues.length) * 10) / 10,
            max_aqi: Math.round(Math.max(...aqiValues) * 10) / 10,
            min_aqi: Math.round(Math.min(...aqiValues) * 10) / 10,
            trend: 'stable'
        },
        note: 'Using fallback forecast - API not available'
    };
};

/**
 * Fallback trends when API unavailable
 */
const getFallbackTrends = (location, days) => {
    return {
        location,
        analysis_period: `${days} days`,
        analyzed_at: new Date().toISOString(),
        statistics: {
            mean_aqi: 100.0,
            std_deviation: 20.0,
            min_aqi: 60.0,
            max_aqi: 180.0,
            recent_average: 105.0
        },
        trends: {
            overall_trend: 'stable',
            volatility: 15.0,
            peak_hours: [8, 18, 20]
        },
        insights: [
            'Historical analysis unavailable - using default values',
            'Connect to backend for real-time analysis'
        ],
        note: 'Using fallback analysis - API not available'
    };
};

/**
 * Fallback patterns when API unavailable
 */
const getFallbackPatterns = (location) => {
    return {
        location,
        analyzed_at: new Date().toISOString(),
        daily_patterns: {
            peak_hour: 18,
            lowest_hour: 5,
            peak_aqi: 150.0,
            lowest_aqi: 80.0,
            hourly_variation: 20.0
        },
        weekly_patterns: {
            highest_day: 'Monday',
            lowest_day: 'Sunday',
            weekend_avg: 90.0,
            weekday_avg: 120.0
        },
        seasonal_indicators: {
            detected: false,
            daily_cycle_strength: 0.0,
            interpretation: 'Unknown'
        },
        note: 'Using fallback patterns - API not available'
    };
};

export const historicalAnalysisService = {
    getForecast,
    getHistoricalTrends,
    getPatternAnalysis
};

export default historicalAnalysisService;

