"""
Utility functions for the weather_nws package.
"""
import logging
import os
from datetime import datetime

def setup_logging(level=logging.INFO, log_file=None):
    """
    Configure logging for the weather_nws package.
    
    Args:
        level (int): Logging level (default: logging.INFO)
        log_file (str, optional): Path to log file. If None, logs to console only.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get the package logger
    logger = logging.getLogger('meriweather')
    logger.setLevel(level)
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # Add file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def validate_coordinates(lat, lon):
    """
    Validate that coordinates are within proper ranges.
    
    Args:
        lat (float): Latitude value to validate (-90 to 90)
        lon (float): Longitude value to validate (-180 to 180)
        
    Returns:
        bool: True if coordinates are valid, False otherwise
        
    Raises:
        ValueError: If coordinates are not valid and cannot be auto-corrected
    """
    try:
        # Convert to float if strings
        lat = float(lat)
        lon = float(lon)
        
        # Check latitude range
        if not -90 <= lat <= 90:
            raise ValueError(f"Latitude must be between -90 and 90 degrees, got {lat}")
            
        # Check longitude range
        if not -180 <= lon <= 180:
            raise ValueError(f"Longitude must be between -180 and 180 degrees, got {lon}")
            
        return True
        
    except (ValueError, TypeError) as e:
        # Re-raise with more descriptive message
        raise ValueError(f"Invalid coordinates: {lat}, {lon}. {str(e)}")

def format_date(date_obj):
    """
    Format a date object as an ISO 8601 string.
    
    Args:
        date_obj (datetime): The date to format
        
    Returns:
        str: Formatted date string
    """
    if not isinstance(date_obj, datetime):
        raise TypeError("Expected datetime object")
        
    return date_obj.isoformat()