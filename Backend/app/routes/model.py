"""
Model Management Routes

Endpoints for model training, saving, and loading.
"""

from flask import Blueprint, request, jsonify
import numpy as np
from app.models.forecast_model import ForecastModel
from app.utils.validators import InputValidator
from app.utils.error_handlers import ValidationError, ModelLoadError

bp = Blueprint("model", __name__, url_prefix="/api/v1/model")

# Global model instance
_model = None


def _get_model():
    """Get or initialize model."""
    global _model
    if _model is None:
        _model = ForecastModel(model_type="ensemble")
    return _model


@bp.route("/train", methods=["POST"])
def train_model():
    """
    Train the forecasting model.

    Request JSON:
        {
            "X": "list of lists (feature matrix)",
            "y": "dict {parameter: list of values}",
            "model_type": "string (random_forest, xgboost, ensemble)"
        }

    Returns:
        JSON with training metrics
    """
    try:
        data = request.get_json()

        if not data or "X" not in data or "y" not in data:
            raise ValidationError(
                "X (features) and y (targets) are required"
            )

        # Convert to numpy arrays
        try:
            X = np.array(data["X"], dtype=np.float32)
            y_dict = {
                k: np.array(v, dtype=np.float32)
                for k, v in data["y"].items()
            }
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid data format: {str(e)}")

        # Validate data
        is_valid, msg = InputValidator.validate_model_data(X, y_dict)
        if not is_valid:
            raise ValidationError(msg)

        # Create or get model
        model_type = data.get("model_type", "ensemble")
        if model_type not in ForecastModel.SUPPORTED_MODELS:
            raise ValidationError(
                f"Model type must be one of {ForecastModel.SUPPORTED_MODELS}"
            )

        model = ForecastModel(model_type=model_type)

        # Train model
        metrics = model.train(X, y_dict)

        return jsonify(
            {
                "status": "success",
                "message": "Model trained successfully",
                "metrics": metrics,
                "model_type": model_type,
            }
        ), 200

    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500


@bp.route("/save", methods=["POST"])
def save_model():
    """
    Save trained model to disk.

    Request JSON:
        {
            "model_path": "string (path to save)"
        }

    Returns:
        JSON with save status
    """
    try:
        data = request.get_json()

        if not data or "model_path" not in data:
            raise ValidationError("model_path is required")

        model_path = InputValidator.sanitize_string(data["model_path"])
        model = _get_model()

        if not model.is_trained:
            raise ValidationError("Model must be trained before saving")

        model.save(model_path)

        return jsonify(
            {
                "status": "success",
                "message": f"Model saved to {model_path}",
            }
        ), 200

    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500


@bp.route("/load", methods=["POST"])
def load_model():
    """
    Load model from disk.

    Request JSON:
        {
            "model_path": "string (path to load from)"
        }

    Returns:
        JSON with load status
    """
    try:
        data = request.get_json()

        if not data or "model_path" not in data:
            raise ValidationError("model_path is required")

        model_path = InputValidator.sanitize_string(data["model_path"])
        model = _get_model()

        model.load(model_path)

        return jsonify(
            {
                "status": "success",
                "message": f"Model loaded from {model_path}",
                "model_type": model.model_type,
            }
        ), 200

    except FileNotFoundError as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 404}
        ), 404
    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500


@bp.route("/status", methods=["GET"])
def model_status():
    """
    Get model status.

    Returns:
        JSON with model status information
    """
    try:
        model = _get_model()

        return jsonify(
            {
                "status": "success",
                "data": {
                    "is_trained": model.is_trained,
                    "model_type": model.model_type,
                    "supported_parameters": model.SUPPORTED_PARAMETERS,
                    "trained_for": list(model.models.keys()),
                },
            }
        ), 200

    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500


@bp.route("/<parameter>/feature-importance", methods=["GET"])
def get_feature_importance(parameter: str):
    """
    Get feature importance for a parameter.

    Args:
        parameter: Air quality parameter

    Returns:
        JSON with feature importance scores
    """
    try:
        if parameter not in ForecastModel.SUPPORTED_PARAMETERS:
            raise ValidationError(
                f"Parameter must be one of {ForecastModel.SUPPORTED_PARAMETERS}"
            )

        model = _get_model()
        importance = model.get_feature_importance(parameter)

        if importance is None:
            raise ValidationError(
                f"Model not trained for parameter '{parameter}'"
            )

        return jsonify(
            {
                "status": "success",
                "parameter": parameter,
                "importance": importance,
            }
        ), 200

    except ValidationError as e:
        return jsonify(
            {"status": "error", "message": e.message, "code": 400}
        ), 400
    except Exception as e:
        return jsonify(
            {"status": "error", "message": str(e), "code": 500}
        ), 500
