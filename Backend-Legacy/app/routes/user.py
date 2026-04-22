from flask import Blueprint, jsonify

bp = Blueprint("user", __name__, url_prefix="/api/v1/user")

@bp.route("/profile", methods=["GET"])
def get_profile():
    return jsonify({
        "status": "success",
        "data": {
            "name": "Demo User",
            "email": "user@aeroguard.com",
            "persona": "general_public"
        }
    }), 200
