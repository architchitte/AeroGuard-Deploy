"""
Input Validators

Validation utilities for API inputs.
"""

from typing import Any, Dict, List, Tuple
import re


class InputValidator:
    """Centralized input validation."""

    @staticmethod
    def validate_location_id(location_id: Any) -> Tuple[bool, str]:
        """
        Validate location ID format.

        Args:
            location_id: Location identifier to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if location_id is None:
            return False, "Location ID is required"

        if not isinstance(location_id, str):
            return False, "Location ID must be a string"

        if len(location_id) == 0:
            return False, "Location ID cannot be empty"

        if len(location_id) > 100:
            return False, "Location ID cannot exceed 100 characters"

        if not re.match(r"^[a-zA-Z0-9\s,._%+-]+$", location_id):
            return False, "Location ID can only contain alphanumeric characters, spaces, commas, dots, and common URL symbols"

        return True, ""

    @staticmethod
    def validate_days_ahead(days: Any) -> Tuple[bool, str]:
        """
        Validate forecast days parameter.

        Args:
            days: Number of days to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if days is None:
            return False, "days_ahead parameter is required"

        try:
            days_int = int(days)
        except (ValueError, TypeError):
            return False, "days_ahead must be an integer"

        if days_int < 1 or days_int > 30:
            return False, "days_ahead must be between 1 and 30"

        return True, ""

    @staticmethod
    def validate_forecast_request(data: Dict) -> Tuple[bool, str]:
        """
        Validate complete forecast request.

        Args:
            data: Request data dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"

        if "location_id" not in data:
            return False, "location_id is required"

        is_valid, msg = InputValidator.validate_location_id(data["location_id"])
        if not is_valid:
            return False, msg

        if "days_ahead" in data:
            is_valid, msg = InputValidator.validate_days_ahead(data["days_ahead"])
            if not is_valid:
                return False, msg

        return True, ""

    @staticmethod
    def validate_model_data(
        X: Any, y_dict: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate training data.

        Args:
            X: Feature matrix
            y_dict: Target variables dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        if X is None or len(X) == 0:
            return False, "Feature matrix cannot be empty"

        if not isinstance(y_dict, dict):
            return False, "Target variables must be a dictionary"

        if len(y_dict) == 0:
            return False, "At least one target variable is required"

        return True, ""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitize string input.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""

        # Remove leading/trailing whitespace
        value = value.strip()

        # Truncate if necessary
        if len(value) > max_length:
            value = value[:max_length]

        return value
