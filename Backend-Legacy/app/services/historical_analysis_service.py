"""
Historical AQI Analysis Service

Provides historical trend analysis, forecasting, and pattern detection
using the SARIMA model.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.models.historical_analysis_model import get_historical_analysis_model

logger = logging.getLogger(__name__)


# Location-specific adjustment factors
# These provide location-aware forecasts until location-specific models are trained
LOCATION_FACTORS = {
    'Mumbai': {
        'base_aqi': 120,
        'volatility_multiplier': 1.2,
        'trend_factor': 0.05,
        'description': 'Coastal city with moderate pollution'
    },
    'Delhi': {
        'base_aqi': 180,
        'volatility_multiplier': 1.5,
        'trend_factor': 0.08,
        'description': 'High pollution with seasonal variations'
    },
    'Bangalore': {
        'base_aqi': 90,
        'volatility_multiplier': 0.8,
        'trend_factor': 0.02,
        'description': 'Garden city with relatively clean air'
    },
    'Chennai': {
        'base_aqi': 100,
        'volatility_multiplier': 1.0,
        'trend_factor': 0.03,
        'description': 'Coastal city with moderate pollution'
    },
    'Kolkata': {
        'base_aqi': 150,
        'volatility_multiplier': 1.3,
        'trend_factor': 0.06,
        'description': 'Industrial city with high pollution'
    },
    'Hyderabad': {
        'base_aqi': 110,
        'volatility_multiplier': 1.1,
        'trend_factor': 0.04,
        'description': 'Tech city with growing pollution'
    },
    'Pune': {
        'base_aqi': 95,
        'volatility_multiplier': 0.9,
        'trend_factor': 0.03,
        'description': 'Hill city with moderate air quality'
    },
    'Ahmedabad': {
        'base_aqi': 140,
        'volatility_multiplier': 1.2,
        'trend_factor': 0.05,
        'description': 'Industrial city with high pollution'
    },
}

# Default factors for unknown locations
DEFAULT_FACTORS = {
    'base_aqi': 100,
    'volatility_multiplier': 1.0,
    'trend_factor': 0.0,
    'description': 'Generic location'
}


class HistoricalAnalysisService:
    """
    Service for historical AQI analysis and forecasting.
    
    Features:
    - Historical trend analysis
    - Time-series forecasting
    - Pattern detection
    - Anomaly identification
    """
    
    def __init__(self):
        """Initialize the service."""
        self.model = None
        try:
            self.model = get_historical_analysis_model()
            logger.info("✓ Historical Analysis Service initialized")
        except Exception as e:
            logger.warning(f"Could not load SARIMA model: {e}")
    
    def get_forecast(
        self,
        location: str,
        hours: int = 24
    ) -> Dict:
        """
        Get AQI forecast for specified hours with location-specific adjustments.
        
        Args:
            location: Location name
            hours: Number of hours to forecast (default: 24)
            
        Returns:
            Dictionary with forecast data
        """
        try:
            if self.model and self.model._is_loaded:
                # Get base forecast with confidence intervals
                forecast_data = self.model.get_forecast_with_confidence(hours)
                
                # Apply location-specific adjustments
                adjusted_data = self._apply_location_adjustments(
                    forecast_data, 
                    location, 
                    hours
                )
                
                # Generate timestamps
                timestamps = self._generate_timestamps(hours)
                
                # Get location factors for metadata
                factors = self._get_location_factors(location)
                
                # Format response
                forecast_points = []
                for i in range(hours):
                    forecast_points.append({
                        'timestamp': timestamps[i],
                        'hour_offset': i + 1,
                        'aqi_forecast': round(adjusted_data['forecast'][i], 1),
                        'lower_bound': round(adjusted_data['lower_bound'][i], 1),
                        'upper_bound': round(adjusted_data['upper_bound'][i], 1)
                    })
                
                return {
                    'location': location,
                    'forecast_hours': hours,
                    'generated_at': datetime.now().isoformat(),
                    'model_type': 'sarima_location_adjusted',
                    'confidence_level': adjusted_data['confidence_level'],
                    'location_aware': location in LOCATION_FACTORS,
                    'forecast': forecast_points,
                    'summary': {
                        'average_aqi': round(np.mean(adjusted_data['forecast']), 1),
                        'max_aqi': round(max(adjusted_data['forecast']), 1),
                        'min_aqi': round(min(adjusted_data['forecast']), 1),
                        'trend': self._determine_trend(adjusted_data['forecast'])
                    }
                }
            else:
                return self._get_fallback_forecast(location, hours)
                
        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            return self._get_fallback_forecast(location, hours)
    
    def analyze_historical_data(
        self,
        location: str,
        historical_data: Optional[pd.Series] = None,
        days: int = 7
    ) -> Dict:
        """
        Analyze historical AQI trends.
        
        Args:
            location: Location name
            historical_data: Pandas Series with historical AQI (optional)
            days: Number of days to analyze (default: 7)
            
        Returns:
            Dictionary with historical analysis
        """
        try:
            # If no data provided, generate mock data for demonstration
            if historical_data is None:
                historical_data = self._generate_mock_historical_data(days, location)
            
            if self.model and self.model._is_loaded:
                analysis = self.model.analyze_historical_trend(historical_data)
                
                return {
                    'location': location,
                    'analysis_period': f'{days} days',
                    'analyzed_at': datetime.now().isoformat(),
                    'statistics': {
                        'mean_aqi': round(analysis['mean'], 1),
                        'std_deviation': round(analysis['std'], 1),
                        'min_aqi': round(analysis['min'], 1),
                        'max_aqi': round(analysis['max'], 1),
                        'recent_average': round(analysis['recent_average'], 1)
                    },
                    'trends': {
                        'overall_trend': analysis['trend'],
                        'volatility': round(analysis['volatility'], 1),
                        'peak_hours': analysis['peak_hours']
                    },
                    'insights': self._generate_insights(analysis)
                }
            else:
                return self._get_fallback_analysis(location, days)
                
        except Exception as e:
            logger.error(f"Historical analysis failed: {e}")
            return self._get_fallback_analysis(location, days)
    
    def get_pattern_analysis(
        self,
        location: str,
        historical_data: Optional[pd.Series] = None
    ) -> Dict:
        """
        Analyze patterns in historical AQI data.
        
        Args:
            location: Location name
            historical_data: Pandas Series with historical AQI
            
        Returns:
            Dictionary with pattern analysis
        """
        try:
            if historical_data is None:
                historical_data = self._generate_mock_historical_data(30, location)
            
            patterns = {
                'location': location,
                'analyzed_at': datetime.now().isoformat(),
                'daily_patterns': self._analyze_daily_patterns(historical_data),
                'weekly_patterns': self._analyze_weekly_patterns(historical_data),
                'seasonal_indicators': self._detect_seasonality(historical_data)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {
                'location': location,
                'analyzed_at': datetime.now().isoformat(),
                'error': 'Pattern analysis unavailable'
            }
    
    def _get_location_factors(self, location: str) -> Dict:
        """
        Get adjustment factors for a specific location.
        
        Args:
            location: Location name
            
        Returns:
            Dictionary with location factors
        """
        # Try exact match first
        if location in LOCATION_FACTORS:
            return LOCATION_FACTORS[location]
        
        # Try case-insensitive match
        for loc_key in LOCATION_FACTORS.keys():
            if loc_key.lower() == location.lower():
                return LOCATION_FACTORS[loc_key]
        
        # Return default factors
        logger.info(f"Using default factors for unknown location: {location}")
        return DEFAULT_FACTORS
    
    def _apply_location_adjustments(
        self,
        forecast_data: Dict,
        location: str,
        hours: int
    ) -> Dict:
        """
        Apply location-specific adjustments to forecast data.
        
        Args:
            forecast_data: Base forecast from SARIMA model
            location: Location name
            hours: Number of forecast hours
            
        Returns:
            Adjusted forecast data
        """
        factors = self._get_location_factors(location)
        
        # Extract base forecast
        base_forecast = forecast_data['forecast']
        base_lower = forecast_data['lower_bound']
        base_upper = forecast_data['upper_bound']
        
        # Calculate adjustments
        adjusted_forecast = []
        adjusted_lower = []
        adjusted_upper = []
        
        for i in range(hours):
            # Apply volatility multiplier
            value = base_forecast[i] * factors['volatility_multiplier']
            
            # Shift to location baseline (difference from generic 100)
            baseline_shift = factors['base_aqi'] - 100
            value += baseline_shift
            
            # Apply trend factor (gradual increase/decrease over time)
            trend_adjustment = i * factors['trend_factor']
            value += trend_adjustment
            
            # Ensure non-negative
            value = max(0, value)
            adjusted_forecast.append(value)
            
            # Adjust bounds proportionally
            lower = base_lower[i] * factors['volatility_multiplier'] + baseline_shift + trend_adjustment
            upper = base_upper[i] * factors['volatility_multiplier'] + baseline_shift + trend_adjustment
            
            adjusted_lower.append(max(0, lower))
            adjusted_upper.append(max(0, upper))
        
        return {
            'forecast': adjusted_forecast,
            'lower_bound': adjusted_lower,
            'upper_bound': adjusted_upper,
            'confidence_level': forecast_data['confidence_level']
        }
    
    def _generate_timestamps(self, hours: int) -> List[str]:
        """Generate future timestamps."""
        now = datetime.now()
        timestamps = []
        for i in range(hours):
            future_time = now + timedelta(hours=i+1)
            timestamps.append(future_time.isoformat())
        return timestamps
    
    def _determine_trend(self, forecast: List[float]) -> str:
        """Determine trend from forecast."""
        if len(forecast) < 2:
            return 'stable'
        
        first_half = np.mean(forecast[:len(forecast)//2])
        second_half = np.mean(forecast[len(forecast)//2:])
        
        diff = second_half - first_half
        
        if diff > 10:
            return 'increasing'
        elif diff < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    def _generate_mock_historical_data(self, days: int, location: str = None) -> pd.Series:
        """
        Generate mock historical data for demonstration with location-specific patterns.
        
        Args:
            days: Number of days of historical data
            location: Location name for location-specific patterns
            
        Returns:
            Pandas Series with mock historical AQI data
        """
        hours = days * 24
        dates = pd.date_range(end=datetime.now(), periods=hours, freq='H')
        
        # Get location factors
        if location:
            factors = self._get_location_factors(location)
            base = factors['base_aqi']
            volatility = factors['volatility_multiplier']
        else:
            base = 100
            volatility = 1.0
        
        # Generate realistic AQI pattern with location adjustments
        trend = np.linspace(0, 20, hours) * volatility
        daily_cycle = 30 * np.sin(np.linspace(0, days * 2 * np.pi, hours)) * volatility
        noise = np.random.normal(0, 10 * volatility, hours)
        
        aqi_values = base + trend + daily_cycle + noise
        aqi_values = np.clip(aqi_values, 0, 500)
        
        return pd.Series(aqi_values, index=dates)
    
    def _analyze_daily_patterns(self, data: pd.Series) -> Dict:
        """Analyze daily patterns."""
        try:
            if isinstance(data.index, pd.DatetimeIndex):
                hourly_avg = data.groupby(data.index.hour).mean()
                
                return {
                    'peak_hour': int(hourly_avg.idxmax()),
                    'lowest_hour': int(hourly_avg.idxmin()),
                    'peak_aqi': round(float(hourly_avg.max()), 1),
                    'lowest_aqi': round(float(hourly_avg.min()), 1),
                    'hourly_variation': round(float(hourly_avg.std()), 1)
                }
            else:
                return {'error': 'No datetime index'}
        except Exception as e:
            logger.warning(f"Daily pattern analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_weekly_patterns(self, data: pd.Series) -> Dict:
        """Analyze weekly patterns."""
        try:
            if isinstance(data.index, pd.DatetimeIndex):
                daily_avg = data.groupby(data.index.dayofweek).mean()
                
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                return {
                    'highest_day': days[int(daily_avg.idxmax())],
                    'lowest_day': days[int(daily_avg.idxmin())],
                    'weekend_avg': round(float(daily_avg[[5, 6]].mean()), 1),
                    'weekday_avg': round(float(daily_avg[[0, 1, 2, 3, 4]].mean()), 1)
                }
            else:
                return {'error': 'No datetime index'}
        except Exception as e:
            logger.warning(f"Weekly pattern analysis failed: {e}")
            return {'error': str(e)}
    
    def _detect_seasonality(self, data: pd.Series) -> Dict:
        """Detect seasonal patterns."""
        try:
            # Simple seasonality detection
            if len(data) < 48:
                return {'detected': False, 'reason': 'Insufficient data'}
            
            # Check for 24-hour cycle
            autocorr_24h = data.autocorr(lag=24) if len(data) >= 24 else 0
            
            return {
                'detected': abs(autocorr_24h) > 0.3,
                'daily_cycle_strength': round(float(autocorr_24h), 2),
                'interpretation': 'Strong' if abs(autocorr_24h) > 0.5 else 'Moderate' if abs(autocorr_24h) > 0.3 else 'Weak'
            }
        except Exception as e:
            logger.warning(f"Seasonality detection failed: {e}")
            return {'detected': False, 'error': str(e)}
    
    def _generate_insights(self, analysis: Dict) -> List[str]:
        """Generate human-readable insights from analysis."""
        insights = []
        
        # Trend insight
        trend = analysis.get('trend', 'unknown')
        if trend == 'increasing':
            insights.append("AQI shows an increasing trend over the analyzed period")
        elif trend == 'decreasing':
            insights.append("AQI shows a decreasing trend - air quality improving")
        else:
            insights.append("AQI remains relatively stable")
        
        # Volatility insight
        volatility = analysis.get('volatility', 0)
        if volatility > 20:
            insights.append("High volatility detected - AQI fluctuates significantly")
        elif volatility > 10:
            insights.append("Moderate volatility in AQI levels")
        else:
            insights.append("Low volatility - AQI relatively consistent")
        
        # Peak hours insight
        peak_hours = analysis.get('peak_hours', [])
        if peak_hours:
            hours_str = ', '.join([f"{h}:00" for h in peak_hours])
            insights.append(f"Peak pollution typically occurs at {hours_str}")
        
        return insights
    
    def _get_fallback_forecast(self, location: str, hours: int) -> Dict:
        """Get fallback forecast when model unavailable."""
        base_aqi = 100
        timestamps = self._generate_timestamps(hours)
        
        forecast_points = []
        for i in range(hours):
            variation = np.random.normal(0, 5)
            aqi = max(0, base_aqi + variation)
            
            forecast_points.append({
                'timestamp': timestamps[i],
                'hour_offset': i + 1,
                'aqi_forecast': round(aqi, 1),
                'lower_bound': round(aqi * 0.9, 1),
                'upper_bound': round(aqi * 1.1, 1)
            })
        
        return {
            'location': location,
            'forecast_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'model_type': 'fallback',
            'confidence_level': 0.5,
            'forecast': forecast_points,
            'summary': {
                'average_aqi': base_aqi,
                'max_aqi': base_aqi + 10,
                'min_aqi': base_aqi - 10,
                'trend': 'stable'
            },
            'note': 'Using fallback forecast - SARIMA model not available'
        }
    
    def _get_fallback_analysis(self, location: str, days: int) -> Dict:
        """Get fallback analysis when model unavailable."""
        return {
            'location': location,
            'analysis_period': f'{days} days',
            'analyzed_at': datetime.now().isoformat(),
            'statistics': {
                'mean_aqi': 100.0,
                'std_deviation': 20.0,
                'min_aqi': 60.0,
                'max_aqi': 180.0,
                'recent_average': 105.0
            },
            'trends': {
                'overall_trend': 'stable',
                'volatility': 15.0,
                'peak_hours': [8, 18, 20]
            },
            'insights': [
                'Historical analysis unavailable - using default values',
                'Install pmdarima for full SARIMA model support'
            ],
            'note': 'Using fallback analysis - SARIMA model not available'
        }
    
    def get_model_status(self) -> Dict:
        """
        Get status of the historical analysis model.
        
        Returns:
            Dictionary with model status
        """
        if self.model:
            return self.model.get_model_info()
        else:
            return {
                'loaded': False,
                'error': 'Model not initialized'
            }


# Global service instance
_global_service: Optional[HistoricalAnalysisService] = None


def get_historical_analysis_service() -> HistoricalAnalysisService:
    """
    Get global historical analysis service instance (singleton pattern).
    
    Returns:
        HistoricalAnalysisService instance
    """
    global _global_service
    if _global_service is None:
        _global_service = HistoricalAnalysisService()
    return _global_service


__all__ = [
    "HistoricalAnalysisService",
    "get_historical_analysis_service"
]

