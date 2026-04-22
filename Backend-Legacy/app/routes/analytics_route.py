# app/routes/analytics_routes.py

from flask import Blueprint, request, jsonify
from app.services.analytics_service import generate_xai

bp = Blueprint("analytics_route", __name__, url_prefix="/api/v1/analytics")

@bp.route("/xai", methods=["GET"])
def get_xai():
    city = request.args.get("city", "Delhi")
    aqi = int(request.args.get("aqi", 150))  # fallback

    xai = generate_xai(city, aqi)

    return jsonify({
        "city": city,
        "xai": xai,
        "model_type": "rule-based"
    })
