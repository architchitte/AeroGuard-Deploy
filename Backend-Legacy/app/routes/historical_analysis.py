"""
Historical Analysis API Routes

Provides endpoints for SARIMA-based historical AQI analysis and forecasting.
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.historical_analysis_service import get_historical_analysis_service

logger = logging.getLogger(__name__)

bp = Blueprint('historical_analysis', __name__, url_prefix='/api/v1/historical-analysis')


@bp.route('/forecast', methods=['GET'])
def get_forecast():
    """
    Get AQI forecast for specified hours.
    
    Query Parameters:
        location (str): Location name (default: 'Unknown')
        hours (int): Number of hours to forecast (default: 24)
    
    Returns:
        JSON with forecast data including confidence intervals
    """
    try:
        location = request.args.get('location', 'Unknown')
        hours = int(request.args.get('hours', 24))
        
        # Validate hours
        if hours < 1 or hours > 168:
            return jsonify({
                'error': 'Invalid hours parameter',
                'message': 'Hours must be between 1 and 168'
            }), 400
        
        service = get_historical_analysis_service()
        forecast = service.get_forecast(location, hours)
        
        return jsonify(forecast), 200
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        return jsonify({
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Forecast endpoint error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to generate forecast'
        }), 500


@bp.route('/trends', methods=['GET'])
def get_trends():
    """
    Get historical trend analysis.
    
    Query Parameters:
        location (str): Location name (default: 'Unknown')
        days (int): Number of days to analyze (default: 7)
    
    Returns:
        JSON with historical trend analysis
    """
    try:
        location = request.args.get('location', 'Unknown')
        days = int(request.args.get('days', 7))
        
        # Validate days
        if days < 1 or days > 90:
            return jsonify({
                'error': 'Invalid days parameter',
                'message': 'Days must be between 1 and 90'
            }), 400
        
        service = get_historical_analysis_service()
        analysis = service.analyze_historical_data(location, days=days)
        
        return jsonify(analysis), 200
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        return jsonify({
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Trends endpoint error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to analyze trends'
        }), 500


@bp.route('/patterns', methods=['GET'])
def get_patterns():
    """
    Get pattern analysis (daily, weekly, seasonal).
    
    Query Parameters:
        location (str): Location name (default: 'Unknown')
    
    Returns:
        JSON with pattern analysis
    """
    try:
        location = request.args.get('location', 'Unknown')
        
        service = get_historical_analysis_service()
        patterns = service.get_pattern_analysis(location)
        
        return jsonify(patterns), 200
        
    except Exception as e:
        logger.error(f"Patterns endpoint error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to analyze patterns'
        }), 500


@bp.route('/status', methods=['GET'])
def get_model_status():
    """
    Get SARIMA model status and information.
    
    Returns:
        JSON with model status
    """
    try:
        service = get_historical_analysis_service()
        status = service.get_model_status()
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to get model status'
        }), 500


# Health check endpoint
@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'historical_analysis'
    }), 200


__all__ = ['bp']
