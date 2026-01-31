"""
REST API endpoints for model comparison and selection service.

Provides HTTP endpoints for:
- Running model comparisons
- Retrieving comparison results
- Managing model comparisons
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
import pandas as pd
import numpy as np

from app.services.model_selector import ModelComparator, ModelSelector
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel
from app.utils.timeseries_preprocessor import TimeSeriesPreprocessor

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
model_comparison_bp = Blueprint('model_comparison', __name__, url_prefix='/api/v1/models')


@model_comparison_bp.route('/compare', methods=['POST'])
def compare_models():
    """
    Run model comparison on provided data.
    
    Request JSON:
    {
        "data": [[...], [...], ...],  # Historical data as list of lists
        "columns": ["date", "PM2.5", "PM10", ...],  # Column names
        "target_col": "PM2.5",  # Column to forecast (default: "PM2.5")
        "forecast_steps": 6,  # Steps to forecast (default: 6)
        "test_size": 0.2,  # Train/test split (default: 0.2)
        "models": ["SARIMA", "XGBoost"]  # Models to use (default: both)
    }
    
    Returns:
    {
        "status": "success",
        "best_model": "XGBoost",
        "metrics": {...},
        "predictions": {...},
        "test_actual": [...],
        "timestamp": "2024-01-31T10:30:00"
    }
    """
    try:
        # Validate request
        if not request.json:
            return jsonify({
                "status": "error",
                "message": "Request body must be JSON",
                "code": 400
            }), 400
        
        data = request.json.get('data')
        columns = request.json.get('columns')
        target_col = request.json.get('target_col', 'PM2.5')
        forecast_steps = request.json.get('forecast_steps', 6)
        test_size = request.json.get('test_size', 0.2)
        models = request.json.get('models', ['SARIMA', 'XGBoost'])
        
        # Validate required fields
        if not data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: data",
                "code": 400
            }), 400
        
        if not columns:
            return jsonify({
                "status": "error",
                "message": "Missing required field: columns",
                "code": 400
            }), 400
        
        # Convert data to DataFrame
        try:
            df = pd.DataFrame(data, columns=columns)
        except Exception as e:
            logger.error(f"Error creating DataFrame: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Invalid data format: {str(e)}",
                "code": 400
            }), 400
        
        # Validate numeric columns
        try:
            df[target_col] = pd.to_numeric(df[target_col])
        except (KeyError, ValueError) as e:
            return jsonify({
                "status": "error",
                "message": f"Invalid target column '{target_col}' or non-numeric data",
                "code": 400
            }), 400
        
        # Preprocess data for XGBoost if it's in the models list
        if 'XGBoost' in models:
            try:
                preprocessor = TimeSeriesPreprocessor()
                df = preprocessor.prepare_features(df, target_col=target_col)
            except Exception as e:
                logger.warning(f"Could not preprocess data for XGBoost: {str(e)}")
                # Continue without XGBoost if preprocessing fails
                models = [m for m in models if m != 'XGBoost']
                if not models:
                    return jsonify({
                        "status": "error",
                        "message": "Data preprocessing failed and no valid models remaining",
                        "code": 400
                    }), 400
        
        # Create comparator
        comparator = ModelComparator()
        
        # Register requested models
        model_mapping = {
            'SARIMA': SARIMAModel(),
            'XGBoost': XGBoostModel()
        }
        
        for model_name in models:
            if model_name not in model_mapping:
                logger.warning(f"Unknown model: {model_name}")
                continue
            comparator.add_model(model_name, model_mapping[model_name])
        
        if not comparator.models:
            return jsonify({
                "status": "error",
                "message": "No valid models specified",
                "code": 400
            }), 400
        
        # Run comparison
        logger.info(f"Running model comparison on {len(df)} samples, target: {target_col}")
        result = comparator.train_and_compare(
            df,
            target_col=target_col,
            test_size=test_size,
            forecast_steps=forecast_steps
        )
        
        # Format response
        response = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "best_model": result['best_model'],
                "metrics": {
                    model: {
                        "MAE": float(metrics['MAE']),
                        "RMSE": float(metrics['RMSE']),
                        "sample_count": int(metrics.get('sample_count', 0))
                    }
                    for model, metrics in result['metrics'].items()
                },
                "predictions": {
                    model: [float(p) for p in preds]
                    for model, preds in result['predictions'].items()
                },
                "test_actual": [float(x) for x in result['test_actual']],
                "comparison_report": result.get('comparison')
            }
        }
        
        logger.info(f"Model comparison successful. Winner: {result['best_model']}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in compare_models: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@model_comparison_bp.route('/quick-compare', methods=['POST'])
def quick_compare():
    """
    Quick model comparison with simpler API.
    
    Request JSON:
    {
        "data": DataFrame-compatible dict or list of lists,
        "target_col": "PM2.5"
    }
    
    Returns:
    {
        "status": "success",
        "best_model": "XGBoost",
        "metrics": {...},
        "winner_forecast": [...]
    }
    """
    try:
        if not request.json:
            return jsonify({
                "status": "error",
                "message": "Request body must be JSON",
                "code": 400
            }), 400
        
        data = request.json.get('data')
        columns = request.json.get('columns', None)
        target_col = request.json.get('target_col', 'PM2.5')
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: data",
                "code": 400
            }), 400
        
        # Convert to DataFrame
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif columns:
                # data is a list of lists with separate columns spec
                df = pd.DataFrame(data, columns=columns)
            else:
                # If no columns provided, assume default: date, PM2.5, PM10 or infer from length
                # If we have 3 columns, assume date, PM2.5, PM10
                if len(data) > 0 and len(data[0]) == 3:
                    columns = ['date', 'PM2.5', 'PM10']
                    df = pd.DataFrame(data, columns=columns)
                else:
                    # Try to infer - assume list of lists
                    df = pd.DataFrame(data)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Invalid data format: {str(e)}",
                "code": 400
            }), 400
        
        # Preprocess data for XGBoost
        try:
            preprocessor = TimeSeriesPreprocessor()
            df = preprocessor.prepare_features(df, target_col=target_col)
            # Drop rows with NaN (from lag/rolling features)
            df = df.dropna()
        except Exception as e:
            logger.warning(f"Could not preprocess data for XGBoost: {str(e)}")
        
        # Quick selection
        selector = ModelSelector({
            'SARIMA': SARIMAModel(),
            'XGBoost': XGBoostModel()
        })
        
        try:
            result = selector.select_best(df, target_col=target_col)
        except Exception as e:
            logger.error(f"Error in quick_compare: {str(e)}")
            return jsonify({
                "status": "error",
                "message": str(e),
                "code": 500
            }), 500
        
        response = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "best_model": result['best_model'],
                "metrics": {
                    model: {
                        "MAE": float(metrics['MAE']),
                        "RMSE": float(metrics['RMSE'])
                    }
                    for model, metrics in result['metrics'].items()
                },
                "winner_forecast": [float(x) for x in result['predictions'][result['best_model']]]
            }
        }
        
        logger.info(f"Quick comparison successful. Winner: {result['best_model']}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in quick_compare: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@model_comparison_bp.route('/available-models', methods=['GET'])
def available_models():
    """
    Get list of available models for comparison.
    
    Returns:
    {
        "status": "success",
        "models": [
            {
                "name": "SARIMA",
                "type": "Statistical forecasting",
                "description": "...",
                "best_for": "Seasonal patterns"
            },
            ...
        ]
    }
    """
    models_info = [
        {
            "name": "SARIMA",
            "type": "Statistical Forecasting",
            "description": "Seasonal Auto-Regressive Integrated Moving Average for time-series forecasting",
            "best_for": "Seasonal patterns, 7-14 day horizons",
            "pros": ["High interpretability", "Handles seasonality", "Good for trends"],
            "cons": ["Slow training", "Requires stationarity", "Linear only"],
            "training_time": "Slow (O(n²))"
        },
        {
            "name": "XGBoost",
            "type": "Gradient Boosting",
            "description": "XGBoost regression with lag-based features for short-term forecasting",
            "best_for": "Non-linear patterns, 6-48 hour horizons",
            "pros": ["Fast training", "Non-linear patterns", "Feature importance"],
            "cons": ["Less interpretable", "Needs feature engineering", "Potential overfitting"],
            "training_time": "Very fast (O(n log n))"
        }
    ]
    
    return jsonify({
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "available_models": models_info,
            "total": len(models_info)
        }
    }), 200


@model_comparison_bp.route('/comparison-info', methods=['GET'])
def comparison_info():
    """
    Get information about the comparison service.
    
    Returns:
    {
        "status": "success",
        "service_info": {
            "name": "Judge Favorite ⭐",
            "version": "1.0.0",
            "metrics": ["MAE", "RMSE"],
            "endpoints": [...]
        }
    }
    """
    endpoints = [
        {
            "method": "POST",
            "path": "/api/v1/models/compare",
            "description": "Full model comparison with detailed options",
            "params": ["data", "columns", "target_col", "forecast_steps", "test_size", "models"]
        },
        {
            "method": "POST",
            "path": "/api/v1/models/quick-compare",
            "description": "Quick comparison with minimal parameters",
            "params": ["data", "target_col"]
        },
        {
            "method": "GET",
            "path": "/api/v1/models/available-models",
            "description": "List available models",
            "params": []
        },
        {
            "method": "GET",
            "path": "/api/v1/models/comparison-info",
            "description": "Service information",
            "params": []
        }
    ]
    
    return jsonify({
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "service_name": "Judge Favorite ⭐ Model Comparison Service",
            "version": "1.0.0",
            "description": "Intelligent model comparison and selection for air quality forecasting",
            "metrics_supported": ["MAE", "RMSE", "Percentage Difference"],
            "endpoints": endpoints
        }
    }), 200


@model_comparison_bp.route('/health', methods=['GET'])
def health():
    """
    Health check for model comparison service.
    
    Returns:
    {
        "status": "healthy",
        "service": "model_comparison",
        "timestamp": "..."
    }
    """
    return jsonify({
        "status": "healthy",
        "service": "model_comparison",
        "timestamp": datetime.utcnow().isoformat(),
        "available_models": ["SARIMA", "XGBoost"]
    }), 200


# Error handlers
@model_comparison_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request"""
    return jsonify({
        "status": "error",
        "message": "Bad request",
        "code": 400
    }), 400


@model_comparison_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "code": 500
    }), 500
