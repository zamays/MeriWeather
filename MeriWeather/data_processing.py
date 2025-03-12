"""
Functions for processing and transforming weather data.
"""
import logging

logger = logging.getLogger(__name__)

def extract_atmospheric_data(observations):
    """
    Extract all relevant atmospheric data from the observations JSON.
    Handles missing or null values that may be present in the API response.
    
    Args:
        observations (dict): JSON response from the NWS API
        
    Returns:
        list: List of dictionaries, each containing data for one observation
    """
    data_rows = []
    
    # Exit early if observations are empty or malformed
    if not observations or 'features' not in observations:
        logger.warning("No valid observation data found to extract")
        return data_rows
    
    logger.info(f"Extracting data from {len(observations['features'])} observations")
    
    for obs in observations['features']:
        props = obs['properties']
        
        # Initialize row with timestamp and station
        row = {
            'timestamp': props.get('timestamp'),
            'station': props.get('station')
        }
        
        # Extract all available meteorological data
        # Temperature data
        if 'temperature' in props and props['temperature'] is not None:
            temp_c = props['temperature'].get('value')
            row['temperature_C'] = temp_c
            # Convert to Fahrenheit if Celsius value exists
            if temp_c is not None:
                row['temperature_F'] = (temp_c * 9/5) + 32
            else:
                row['temperature_F'] = None
        else:
            row['temperature_C'] = None
            row['temperature_F'] = None
            
        # Process other meteorological data
        # For each field, check if it exists and has a value property
        meteorological_fields = [
            'dewpoint', 'windDirection', 'windSpeed', 'windGust', 
            'barometricPressure', 'seaLevelPressure', 'visibility',
            'relativeHumidity', 'precipitationLastHour',
            'precipitationLast3Hours', 'precipitationLast6Hours'
        ]
        
        for field in meteorological_fields:
            if field in props and props[field] is not None:
                row[field] = props[field].get('value')
            else:
                row[field] = None
        
        # Text description and cloud layers
        row['text_description'] = props.get('textDescription')
        
        if 'cloudLayers' in props:
            # Convert cloud layers to a string representation
            try:
                row['cloud_layers'] = str(props['cloudLayers'])
            except Exception as e:
                logger.warning(f"Could not process cloud layers: {e}")
                row['cloud_layers'] = None
        else:
            row['cloud_layers'] = None
            
        # Additional 24-hour temperature data if available
        for field in ['maxTemperatureLast24Hours', 'minTemperatureLast24Hours']:
            if field in props and props[field] is not None:
                temp_value = props[field].get('value')
                row[f"{field}_C"] = temp_value
                if temp_value is not None:
                    row[f"{field}_F"] = (temp_value * 9/5) + 32
                else:
                    row[f"{field}_F"] = None
        
        data_rows.append(row)
    
    logger.info(f"Successfully extracted data for {len(data_rows)} observations")
    return data_rows

def convert_celsius_to_fahrenheit(celsius_value):
    """Convert temperature from Celsius to Fahrenheit."""
    if celsius_value is None:
        return None
    return (celsius_value * 9/5) + 32