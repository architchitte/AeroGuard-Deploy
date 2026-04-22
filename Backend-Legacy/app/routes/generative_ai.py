"""
Generative AI API Routes

Endpoints for generating human-readable AI insights and explanations
based on REAL AQI data.
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

from app.services.realtime_aqi_service import RealtimeAQIService

logger = logging.getLogger(__name__)

bp = Blueprint("generative_ai", __name__, url_prefix="/api/v1/ai")


# =====================================================
# AI BRIEFING (REAL AQI → AI EXPLANATION)
# =====================================================

@bp.route("/briefing", methods=["GET"])
def get_ai_briefing():
    """
    Get a personalized AI-powered health briefing.

    Query Parameters:
        city: City name (required)
        persona: general_public | elderly | athletes | children
    """
    try:
        city = request.args.get("city")
        persona = request.args.get("persona", "general_public")

        if not city:
            return jsonify({
                "status": "error",
                "message": "City parameter is required"
            }), 400

        # ===============================
        # 1️⃣ FETCH REAL AQI DATA
        # ===============================
        aqi_service = RealtimeAQIService()
        aqi_data = aqi_service.get_city_aqi(city)

        if not aqi_data or "aqi" not in aqi_data:
            return jsonify({
                "status": "error",
                "message": f"Could not fetch AQI for {city}"
            }), 404

        aqi_value = aqi_data["aqi"]

        # ===============================
        # 2️⃣ DERIVE CONTEXT (LOGIC)
        # ===============================

        # Trend heuristic
        if aqi_value >= 150:
            trend = "rising"
        elif aqi_value <= 80:
            trend = "falling"
        else:
            trend = "stable"

        # Duration heuristic
        duration = "persistent" if aqi_value >= 120 else "temporary"

        # Main pollutants
        pollutants = aqi_data.get("pollutants", {})
        main_factors = list(pollutants.keys())[:3] if pollutants else ["Traffic emissions"]

        # ===============================
        # 3️⃣ INIT GENERATIVE EXPLAINER
        # ===============================
        api_key = (
            current_app.config.get("GEMINI_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )

        explainer = create_generative_explainer(
            api_key=api_key if api_key else None,
            provider=APIProvider.GEMINI if api_key else APIProvider.TEMPLATE
        )

        # ===============================
        # 4️⃣ GENERATE AI EXPLANATION
        # ===============================
        explanation_obj = explainer.generate_explanation(
            aqi_value=aqi_value,
            trend=trend,
            main_factors=main_factors,
            duration=duration,
            persona=persona,
            style=ExplanationStyle.CASUAL
        )

        # ===============================
        # 5️⃣ RESPONSE
        # ===============================
        return jsonify({
            "status": "success",
            "city": city,
            "aqi": aqi_value,
            "persona": persona,
            "data": explanation_obj.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"AI briefing error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to generate AI briefing"
        }), 500


# =====================================================
# AI FORECAST EXPLANATION (UNCHANGED)
# =====================================================

@bp.route("/explain-forecast", methods=["POST"])
def explain_forecast():
    """
    Explain a complex AQI forecast using AI.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Missing request body"
            }), 400

        aqi_value = data.get("aqi_value", 100)
        trend = data.get("trend", "stable")
        factors = data.get("factors", ["Weather patterns"])
        persona = data.get("persona", "general_public")

        api_key = (
            current_app.config.get("GEMINI_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )

        explainer = create_generative_explainer(
            api_key=api_key if api_key else None,
            provider=APIProvider.GEMINI if api_key else APIProvider.TEMPLATE
        )

        explanation = explainer.generate_explanation(
            aqi_value=aqi_value,
            trend=trend,
            main_factors=factors,
            duration="persistent",
            persona=persona,
            style=ExplanationStyle.CASUAL
        )

        return jsonify({
            "status": "success",
            "data": explanation.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Forecast explanation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to explain forecast"
        }), 500
