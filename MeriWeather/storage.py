"""
Functions for storing and retrieving weather data.
"""
import os
import csv
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def save_to_csv(data, station_id):
    """
    Save the extracted weather data to a CSV file.
    
    Args:
        data (list): List of dictionaries containing observation data
        station_id (str): Station identifier to use in the filename
        
    Returns:
        str: Path to the saved CSV file or None if save failed
    """
    # Create output directory if it doesn't exist
    output_dir = 'weather_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/{station_id}_{timestamp}.csv"
    
    if not data:
        logger.warning(f"No data to save for station {station_id}")
        return None
    
    try:
        # Get column headers from the first data row
        fieldnames = list(data[0].keys())
        
        # Sort fieldnames for consistent column order
        fieldnames.sort()
        
        # Move timestamp and station to the beginning for readability
        if 'timestamp' in fieldnames:
            fieldnames.remove('timestamp')
            fieldnames.insert(0, 'timestamp')
        if 'station' in fieldnames:
            fieldnames.remove('station')
            fieldnames.insert(1, 'station')
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Data successfully saved to {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving data to CSV: {e}")
        return None

def get_data_filepath(station_id, timestamp=None):
    """Generate a standardized filepath for weather data."""
    # Implementation to create consistent file paths
    pass