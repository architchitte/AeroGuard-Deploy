/**
 * Health Risk Service
 * 
 * Integrates with the ML-based health risk assessment API
 */

import axios from 'axios';
import { API_BASE_URL } from './apiConfig';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Get health risk assessment for given AQI value
 * @param {number} aqi - AQI value
 * @param {string} location - Location name (optional)
 * @param {string} pollutant - Primary pollutant (default: PM2.5)
 * @param {string} persona - User persona (optional)
 * @returns {Promise<Object>} Health risk assessment
 */
export const getHealthRisk = async (aqi, location = null, pollutant = 'PM2.5', persona = null) => {
    try {
        const params = {
            aqi,
            pollutant
        };

        if (location) params.location = location;
        if (persona) params.persona = persona;

        const response = await apiClient.get('/api/v1/health-risk', { params });
        return response.data;
    } catch (error) {
        console.error('Health risk API failed:', error);
        // Fallback to rule-based assessment
        return getFallbackHealthRisk(aqi, location, pollutant, persona);
    }
};

/**
 * Get health advice for multiple personas
 * @param {number} aqi - AQI value
 * @param {string} location - Location name
 * @param {Array<string>} personas - Array of persona names
 * @returns {Promise<Object>} Health advice for each persona
 */
export const getMultiPersonaAdvice = async (aqi, location, personas = ['General Public', 'Children', 'Elderly', 'Athletes']) => {
    try {
        const advicePromises = personas.map(persona =>
            getHealthRisk(aqi, location, 'PM2.5', persona)
        );

        const results = await Promise.all(advicePromises);

        return personas.reduce((acc, persona, index) => {
            acc[persona] = results[index];
            return acc;
        }, {});
    } catch (error) {
        console.error('Multi-persona advice failed:', error);
        return getFallbackMultiPersonaAdvice(aqi, location, personas);
    }
};

/**
 * Fallback health risk assessment (rule-based)
 */
const getFallbackHealthRisk = (aqi, location, pollutant, persona) => {
    const category = classifyAQI(aqi);
    const riskLevel = getRiskLevel(category);

    return {
        timestamp: new Date().toISOString(),
        location: location,
        aqi: {
            value: aqi,
            primary_pollutant: pollutant,
            category: category,
            color_code: getColorCode(category),
            risk_level: riskLevel
        },
        health_assessment: {
            description: getDescription(category),
            health_implications: getHealthImplications(category),
            cautionary_statement: getCautionaryStatement(category),
            at_risk_groups: getAtRiskGroups(category)
        },
        recommendations: {
            general_advice: getGeneralAdvice(category),
            precautions: getPrecautions(category),
            activity_recommendations: getActivityRecommendations(category)
        },
        model_source: 'fallback',
        model_confidence: 'medium'
    };
};

/**
 * Fallback multi-persona advice
 */
const getFallbackMultiPersonaAdvice = (aqi, location, personas) => {
    return personas.reduce((acc, persona) => {
        acc[persona] = getFallbackHealthRisk(aqi, location, 'PM2.5', persona);
        return acc;
    }, {});
};

/**
 * Classify AQI value into category
 */
const classifyAQI = (aqi) => {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive Groups';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
};

/**
 * Get risk level from category
 */
const getRiskLevel = (category) => {
    const mapping = {
        'Good': 'Low',
        'Moderate': 'Moderate',
        'Unhealthy for Sensitive Groups': 'Moderate',
        'Unhealthy': 'High',
        'Very Unhealthy': 'High',
        'Hazardous': 'Hazardous'
    };
    return mapping[category] || 'Moderate';
};

/**
 * Get color code for category
 */
const getColorCode = (category) => {
    const colors = {
        'Good': '#00E400',
        'Moderate': '#FFFF00',
        'Unhealthy for Sensitive Groups': '#FF7E00',
        'Unhealthy': '#FF0000',
        'Very Unhealthy': '#8F3F97',
        'Hazardous': '#7E0023'
    };
    return colors[category] || '#000000';
};

/**
 * Get description for category
 */
const getDescription = (category) => {
    const descriptions = {
        'Good': 'Air quality is satisfactory, and air pollution poses little or no risk.',
        'Moderate': 'Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.',
        'Unhealthy for Sensitive Groups': 'Members of sensitive groups may experience health effects. The general public is less likely to be affected.',
        'Unhealthy': 'Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.',
        'Very Unhealthy': 'Health alert: The risk of health effects is increased for everyone.',
        'Hazardous': 'Health warning of emergency conditions: everyone is more likely to be affected.'
    };
    return descriptions[category] || '';
};

/**
 * Get health implications for category
 */
const getHealthImplications = (category) => {
    const implications = {
        'Good': ['No health concerns', 'Air quality satisfactory'],
        'Moderate': ['Acceptable for most people', 'Sensitive individuals should be cautious'],
        'Unhealthy for Sensitive Groups': ['Sensitive groups may experience health effects', 'Respiratory symptoms possible'],
        'Unhealthy': ['Increased likelihood of health effects', 'Respiratory and cardiovascular symptoms'],
        'Very Unhealthy': ['Serious health effects for all', 'Significant respiratory distress possible'],
        'Hazardous': ['Emergency health conditions', 'Severe health effects expected']
    };
    return implications[category] || [];
};

/**
 * Get cautionary statement for category
 */
const getCautionaryStatement = (category) => {
    const statements = {
        'Good': 'Enjoy outdoor activities.',
        'Moderate': 'Unusually sensitive people should consider limiting prolonged outdoor exertion.',
        'Unhealthy for Sensitive Groups': 'Sensitive groups should reduce prolonged or heavy outdoor exertion.',
        'Unhealthy': 'Everyone should reduce prolonged or heavy outdoor exertion.',
        'Very Unhealthy': 'Everyone should avoid prolonged or heavy outdoor exertion.',
        'Hazardous': 'Everyone should avoid all outdoor exertion.'
    };
    return statements[category] || '';
};

/**
 * Get at-risk groups for category
 */
const getAtRiskGroups = (category) => {
    const groups = {
        'Good': [],
        'Moderate': ['Unusually sensitive people'],
        'Unhealthy for Sensitive Groups': ['Children', 'Elderly', 'People with asthma', 'People with heart disease'],
        'Unhealthy': ['Everyone', 'Especially sensitive groups'],
        'Very Unhealthy': ['Everyone', 'Serious effects on sensitive groups'],
        'Hazardous': ['Everyone', 'Emergency conditions']
    };
    return groups[category] || [];
};

/**
 * Get general advice for category
 */
const getGeneralAdvice = (category) => {
    const advice = {
        'Good': "It's a great day to be active outside.",
        'Moderate': 'Enjoy outdoor activities, but sensitive individuals should watch for symptoms.',
        'Unhealthy for Sensitive Groups': 'Sensitive groups should limit outdoor activities.',
        'Unhealthy': 'Everyone should limit outdoor activities.',
        'Very Unhealthy': 'Avoid outdoor activities. Stay indoors with air purification.',
        'Hazardous': 'Remain indoors and keep activity levels low. Follow emergency guidelines.'
    };
    return advice[category] || '';
};

/**
 * Get precautions for category
 */
const getPrecautions = (category) => {
    const precautions = {
        'Good': [],
        'Moderate': ['Monitor air quality', 'Watch for symptoms'],
        'Unhealthy for Sensitive Groups': ['Limit outdoor time', 'Wear N95 mask if going outside', 'Keep medications accessible'],
        'Unhealthy': ['Stay indoors when possible', 'Wear N95 mask outdoors', 'Use air purifier'],
        'Very Unhealthy': ['Avoid all outdoor activity', 'Keep windows closed', 'Run air purifier continuously'],
        'Hazardous': ['Seal windows and doors', 'Use HEPA air purifier', 'Follow emergency protocols']
    };
    return precautions[category] || [];
};

/**
 * Get activity recommendations for category
 */
const getActivityRecommendations = (category) => {
    const recommendations = {
        'Good': {
            outdoor: 'All activities appropriate',
            indoor: 'No restrictions',
            exercise: 'Normal exercise routine'
        },
        'Moderate': {
            outdoor: 'Acceptable for most people',
            indoor: 'No restrictions',
            exercise: 'Normal for most, sensitive groups monitor'
        },
        'Unhealthy for Sensitive Groups': {
            outdoor: 'Limit prolonged exertion',
            indoor: 'Move strenuous activities indoors',
            exercise: 'Reduce intensity for sensitive groups'
        },
        'Unhealthy': {
            outdoor: 'Reduce outdoor exertion',
            indoor: 'Move activities indoors',
            exercise: 'Reduce intensity for everyone'
        },
        'Very Unhealthy': {
            outdoor: 'Avoid outdoor activities',
            indoor: 'Stay indoors with air purification',
            exercise: 'Light indoor activity only'
        },
        'Hazardous': {
            outdoor: 'Avoid all outdoor exposure',
            indoor: 'Remain indoors in sealed environment',
            exercise: 'Minimal activity'
        }
    };
    return recommendations[category] || {};
};

export const healthRiskService = {
    getHealthRisk,
    getMultiPersonaAdvice,
    classifyAQI,
    getColorCode,
    getRiskLevel
};

export default healthRiskService;

