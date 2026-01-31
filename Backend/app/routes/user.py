"""
User Routes

Endpoints for user preferences, favorites (user locations), and forecast history.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from app.models.database_models import (
    User, UserPreference, UserLocation, Forecast, Location
)
from app.database import db

bp = Blueprint("user", __name__, url_prefix="/api/v1/users")


@bp.route("/<int:user_id>/preferences", methods=["GET"])
@jwt_required()
def get_preferences(user_id: int):
    current_id = get_jwt_identity()
    if int(current_id) != int(user_id):
        return jsonify({"status": "error", "message": "forbidden"}), 403
    user = User.query.get_or_404(user_id)
    pref = UserPreference.query.filter_by(user_id=user.id).first()
    if not pref:
        return jsonify({"status": "ok", "data": None}), 200
    data = {
        "persona": pref.persona,
        "health_conditions": pref.health_conditions,
        "age_group": pref.age_group,
        "enable_alerts": pref.enable_alerts,
        "alert_threshold_aqi": pref.alert_threshold_aqi,
        "notification_method": pref.notification_method,
        "preferred_forecast_hours": pref.preferred_forecast_hours,
        "preferred_pollutants": pref.preferred_pollutants,
        "language": pref.language,
        "temperature_unit": pref.temperature_unit,
        "explanation_style": pref.explanation_style,
    }
    return jsonify({"status": "ok", "data": data}), 200


@bp.route("/<int:user_id>/preferences", methods=["PUT"])
@jwt_required()
def update_preferences(user_id: int):
    current_id = get_jwt_identity()
    if int(current_id) != int(user_id):
        return jsonify({"status": "error", "message": "forbidden"}), 403
    user = User.query.get_or_404(user_id)
    payload = request.get_json() or {}
    pref = UserPreference.query.filter_by(user_id=user.id).first()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.session.add(pref)

    # Update allowed fields
    for key in [
        "persona", "health_conditions", "age_group", "enable_alerts",
        "alert_threshold_aqi", "notification_method", "preferred_forecast_hours",
        "preferred_pollutants", "language", "temperature_unit", "explanation_style"
    ]:
        if key in payload:
            setattr(pref, key, payload[key])

    db.session.commit()
    return jsonify({"status": "ok", "message": "preferences updated"}), 200


@bp.route("/<int:user_id>/locations", methods=["GET"])
@jwt_required()
def list_user_locations(user_id: int):
    current_id = get_jwt_identity()
    if int(current_id) != int(user_id):
        return jsonify({"status": "error", "message": "forbidden"}), 403
    user = User.query.get_or_404(user_id)
    items = []
    for ul in UserLocation.query.filter_by(user_id=user.id).all():
        loc = Location.query.get(ul.location_id)
        items.append({
            "location_id": loc.location_id,
            "city": loc.city,
            "country": loc.country,
            "is_favorite": ul.is_favorite,
            "alert_threshold_aqi": ul.alert_threshold_aqi,
            "added_at": ul.added_at.isoformat() if ul.added_at else None,
        })
    return jsonify({"status": "ok", "data": items}), 200


@bp.route("/<int:user_id>/locations", methods=["POST"])
@jwt_required()
def add_user_location(user_id: int):
    current_id = get_jwt_identity()
    if int(current_id) != int(user_id):
        return jsonify({"status": "error", "message": "forbidden"}), 403
    user = User.query.get_or_404(user_id)
    payload = request.get_json() or {}
    location_id = payload.get("location_id")
    if not location_id:
        return jsonify({"status": "error", "message": "location_id required"}), 400
    loc = Location.query.filter_by(location_id=location_id).first()
    if not loc:
        return jsonify({"status": "error", "message": "location not found"}), 404

    # Upsert UserLocation
    ul = UserLocation.query.filter_by(user_id=user.id, location_id=loc.id).first()
    if not ul:
        ul = UserLocation(user_id=user.id, location_id=loc.id)
        db.session.add(ul)
    if "is_favorite" in payload:
        ul.is_favorite = bool(payload.get("is_favorite"))
    if "alert_threshold_aqi" in payload:
        ul.alert_threshold_aqi = payload.get("alert_threshold_aqi")

    db.session.commit()
    return jsonify({"status": "ok", "message": "location added"}), 201


@bp.route("/<int:user_id>/locations/<int:location_id>", methods=["DELETE"])
@jwt_required()
def remove_user_location(user_id: int, location_id: int):
    current_id = get_jwt_identity()
    if int(current_id) != int(user_id):
        return jsonify({"status": "error", "message": "forbidden"}), 403
    user = User.query.get_or_404(user_id)
    loc = Location.query.get_or_404(location_id)
    ul = UserLocation.query.filter_by(user_id=user.id, location_id=loc.id).first()
    if not ul:
        return jsonify({"status": "error", "message": "mapping not found"}), 404
    db.session.delete(ul)
    db.session.commit()
    return jsonify({"status": "ok", "message": "location removed"}), 200


@bp.route("/<int:user_id>/forecasts", methods=["GET"])
@jwt_required()
def user_forecast_history(user_id: int):
    current_id = get_jwt_identity()
    if int(current_id) != int(user_id):
        return jsonify({"status": "error", "message": "forbidden"}), 403
    user = User.query.get_or_404(user_id)
    location_filter = request.args.get("location_id")
    q = Forecast.query
    if location_filter:
        loc = Location.query.filter_by(location_id=location_filter).first()
        if not loc:
            return jsonify({"status": "error", "message": "location not found"}), 404
        q = q.filter_by(location_id=loc.id)
    items = q.order_by(Forecast.forecast_time.desc()).limit(100).all()
    result = []
    for f in items:
        result.append({
            "id": f.id,
            "location_id": f.location.location_id if f.location else None,
            "model_type": f.model_type,
            "forecast_time": f.forecast_time.isoformat() if f.forecast_time else None,
            "horizon_hours": f.horizon_hours,
            "aqi_forecast": f.aqi_forecast,
            "pm25_forecast": f.pm25_forecast,
            "pm10_forecast": f.pm10_forecast,
            "confidence": f.confidence,
            "mae": f.mae,
            "rmse": f.rmse,
        })
    return jsonify({"status": "ok", "data": result}), 200



@bp.route('/auth/login', methods=['POST'])
def login():
    """Simple login to issue JWTs for testing/demo.

    Accepts `username` in JSON and issues an access token if the user exists.
    For production, replace with proper password verification.
    """
    data = request.get_json() or {}
    username = data.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'username required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'status': 'ok', 'access_token': access_token}), 200
