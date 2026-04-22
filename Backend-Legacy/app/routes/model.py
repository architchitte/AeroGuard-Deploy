"""
Model Management Routes

Endpoints for model training, saving, and loading.
"""

from flask import Blueprint, request, jsonify, current_app
import numpy as np
import re
from pathlib import Path
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
    Save trained model to disk (secure version with path validation).

    Request JSON:
        {
            "model_name": "string (filename only, e.g., 'my_model.pkl')"
        }

    Returns:
        JSON with save status
    """
    from flask import current_app
    from pathlib import Path
    
    try:
        data = request.get_json()

        if not data or "model_name" not in data:
            raise ValidationError("model_name is required")

        # Validate model name (filename only, no paths)
        model_name = InputValidator.sanitize_string(data["model_name"], max_length=100)
        
        # Only allow alphanumeric, underscore, hyphen, and .pkl extension
        if not re.match(r'^[a-zA-Z0-9_-]+\.pkl$', model_name):
            raise ValidationError("Invalid model filename. Use format: name.pkl")
        
        # Get safe model directory from config
        model_dir = Path(current_app.config.get('MODEL_DIR', 'app/models/saved'))
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct safe path
        model_path = model_dir / model_name
        
        # Prevent path traversal - ensure resolved path is within model_dir
        if not str(model_path.resolve()).startswith(str(model_dir.resolve())):
            raise ValidationError("Invalid model path")
        
        model = _get_model()

        if not model.is_trained:
            raise ValidationError("Model must be trained before saving")

        model.save(str(model_path))

        return jsonify(
            {
                "status": "success",
                "message": f"Model saved successfully",
                "model_name": model_name
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
    Load model from disk (secure version with path validation).

    Request JSON:
        {
            "model_name": "string (filename only)"
        }

    Returns:
        JSON with load status
    """
    from flask import current_app
    from pathlib import Path
    
    try:
        data = request.get_json()

        if not data or "model_name" not in data:
            raise ValidationError("model_name is required")

        # Validate model name
        model_name = InputValidator.sanitize_string(data["model_name"], max_length=100)
        
        if not re.match(r'^[a-zA-Z0-9_-]+\.pkl$', model_name):
            raise ValidationError("Invalid model filename")
        
        # Get safe model directory
        model_dir = Path(current_app.config.get('MODEL_DIR', 'app/models/saved'))
        model_path = model_dir / model_name
        
        # Prevent path traversal
        if not str(model_path.resolve()).startswith(str(model_dir.resolve())):
            raise ValidationError("Invalid model path")
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model '{model_name}' not found")
        
        model = _get_model()
        model.load(str(model_path))

        return jsonify(
            {
                "status": "success",
                "message": f"Model loaded successfully",
                "model_name": model_name,
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
