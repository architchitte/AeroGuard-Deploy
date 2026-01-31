"""
Generative AI API Routes

Endpoints for generating human-readable AI insights and explanations.
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging
import os

from app.services.generative_explainer import (
    create_generative_explainer,
    ExplanationStyle,
    APIProvider
)

logger = logging.getLogger(__name__)

bp = Blueprint("generative_ai", __name__, url_prefix="/api/v1/ai")

@bp.route("/briefing", methods=["GET"])
def get_ai_briefing():
    """
    Get a personalized AI-powered health briefing.
    
    Query Parameters:
        city: City name
        persona: User persona (e.g., 'outdoor_athlete', 'child', 'elderly')
    """
    try:
        city = request.args.get('city', 'Mumbai')
        persona = request.args.get('persona', 'general_public')
        
        # In a real app, we'd fetch actual real-time data for this city
        # For now, let's pretend we have data or use a fallback.
        # Let's try to get data if available (e.g. from our earlier trained city Mumbai)
        
        aqi_value = 156 # Default mock
        trend = "rising"
        factors = ["PM2.5", "Evening Traffic", "Stagnant Air"]
        duration = "temporary"
        
        # If the city is Mumbai, maybe we can be more specific
        if city.lower() == 'mumbai':
            aqi_value = 156
            factors = ["Nitrogen Dioxide (NO2)", "Evening Traffic", "Industrial Exhaust"]
        
        # Initialize Explainer
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key or api_key == 'your-gemini-api-key-here':
            # Try to get from environment
            api_key = os.environ.get('GEMINI_API_KEY')
            
        explainer = create_generative_explainer(
            api_key=api_key if api_key and api_key != 'your-gemini-api-key-here' else None,
            provider=APIProvider.GEMINI if api_key and api_key != 'your-gemini-api-key-here' else APIProvider.TEMPLATE
        )
        
        # Generate explanation
        explanation_obj = explainer.generate_explanation(
            aqi_value=aqi_value,
            trend=trend,
            main_factors=factors,
            duration=duration,
            persona=persona,
            style=ExplanationStyle.CASUAL
        )
        
        return jsonify({
            "status": "success",
            "city": city,
            "persona": persona,
            "data": explanation_obj.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error generating AI briefing: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to generate AI briefing: {str(e)}",
        }), 500

@bp.route("/explain-forecast", methods=["POST"])
def explain_forecast():
    """
    Explain a complex forecast using AI.
    """
    try:
        data = request.get_json()
        if not data or 'forecast' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing forecast data"
            }), 400
            
        # Extract details for the prompt
        aqi_value = data.get('aqi_value', 100)
        trend = data.get('trend', 'stable')
        factors = data.get('factors', ['Weather patterns'])
        persona = data.get('persona', 'general_public')
        
        api_key = current_app.config.get('GEMINI_API_KEY')
        explainer = create_generative_explainer(api_key=api_key if api_key and api_key != 'your-gemini-api-key-here' else None)
        
        explanation = explainer.generate_explanation(
            aqi_value=aqi_value,
            trend=trend,
            main_factors=factors,
            duration="persistent",
            persona=persona
        )
        
        return jsonify({
            "status": "success",
            "data": explanation.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
