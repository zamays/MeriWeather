import pytest
from unittest.mock import patch, Mock
import copy
import meriweather
from meriweather import extract_atmospheric_data, convert_celsius_to_fahrenheit

class TestConvertCelsiusToFahrenheit:
    def test_valid_conversion(self):
        """Test celsius to fahrenheit conversion with valid input."""
        # Test a few common values
        assert convert_celsius_to_fahrenheit(0) == 32
        assert convert_celsius_to_fahrenheit(100) == 212
        assert convert_celsius_to_fahrenheit(-40) == -40
        
        # Test with floating point value
        assert round(convert_celsius_to_fahrenheit(21.5), 2) == 70.7
    
    def test_none_handling(self):
        """Test that None input returns None."""
        assert convert_celsius_to_fahrenheit(None) is None

class TestExtractAtmosphericData:
    def setup_method(self):
        """Set up test data."""
        # Create sample observation data
        self.sample_observation = {
            "features": [
                {
                    "properties": {
                        "timestamp": "2023-05-01T12:00:00Z",
                        "station": "KXYZ",
                        "temperature": {"value": 22.5},
                        "dewpoint": {"value": 15.0},
                        "windDirection": {"value": 180},
                        "windSpeed": {"value": 10.0},
                        "windGust": {"value": 15.5},
                        "barometricPressure": {"value": 1013.25},
                        "seaLevelPressure": {"value": 1013.0},
                        "visibility": {"value": 10000},
                        "relativeHumidity": {"value": 65},
                        "precipitationLastHour": {"value": 0},
                        "precipitationLast3Hours": {"value": 0},
                        "precipitationLast6Hours": {"value": 2.5},
                        "textDescription": "Partly Cloudy",
                        "cloudLayers": [
                            {"base": {"value": 1500}, "amount": "FEW"},
                            {"base": {"value": 4000}, "amount": "SCT"}
                        ],
                        "maxTemperatureLast24Hours": {"value": 25.0},
                        "minTemperatureLast24Hours": {"value": 15.0}
                    }
                }
            ]
        }
    
    def test_successful_extraction(self):
        """Test that data is correctly extracted from a valid observation."""
        # Extract data from sample observation
        result = extract_atmospheric_data(self.sample_observation)
        
        # Check that one row was extracted
        assert len(result) == 1
        data = result[0]
        
        # Check basic properties
        assert data["timestamp"] == "2023-05-01T12:00:00Z"
        assert data["station"] == "KXYZ"
        
        # Check temperature conversions
        assert data["temperature_C"] == 22.5
        assert round(data["temperature_F"], 2) == 72.5
        
        # Check other meteorological fields
        assert data["dewpoint"] == 15.0
        assert data["windDirection"] == 180
        assert data["windSpeed"] == 10.0
        assert data["windGust"] == 15.5
        assert data["barometricPressure"] == 1013.25
        assert data["visibility"] == 10000
        assert data["relativeHumidity"] == 65
        
        # Check text fields
        assert data["text_description"] == "Partly Cloudy"
        assert "FEW" in data["cloud_layers"]
        assert "SCT" in data["cloud_layers"]
        
        # Check 24-hour temperature data
        assert data["maxTemperatureLast24Hours_C"] == 25.0
        assert round(data["maxTemperatureLast24Hours_F"], 2) == 77.0
        assert data["minTemperatureLast24Hours_C"] == 15.0
        assert round(data["minTemperatureLast24Hours_F"], 2) == 59.0
    
    def test_missing_data_handling(self):
        """Test handling of observations with missing data."""
        # Create a copy with some missing fields
        partial_observation = copy.deepcopy(self.sample_observation)
        props = partial_observation["features"][0]["properties"]
        
        # Remove some fields
        del props["dewpoint"]
        del props["windGust"]
        props["temperature"]["value"] = None  # Null value
        del props["cloudLayers"]
        
        # Extract data from modified observation
        result = extract_atmospheric_data(partial_observation)
        data = result[0]
        
        # Check that missing fields are set to None
        assert data["dewpoint"] is None
        assert data["windGust"] is None
        assert data["temperature_C"] is None
        assert data["temperature_F"] is None
        assert data["cloud_layers"] is None
        
        # Check that other fields are still present
        assert data["windDirection"] == 180
        assert data["barometricPressure"] == 1013.25
    
    def test_empty_observations(self):
        """Test handling of empty observation data."""
        # Test with empty dict
        result = extract_atmospheric_data({})
        assert result == []
        
        # Test with None
        result = extract_atmospheric_data(None)
        assert result == []
        
        # Test with missing features key
        result = extract_atmospheric_data({"not_features": []})
        assert result == []
    
    @patch('logging.getLogger')
    def test_logging(self, mock_get_logger):
        """Test that appropriate logging occurs."""
        # Set up mock logger
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Call function with valid data
        result = extract_atmospheric_data(self.sample_observation)
        
        # Verify logging calls
        mock_logger.info.assert_any_call("Extracting data from 1 observations")
        mock_logger.info.assert_any_call("Successfully extracted data for 1 observations")
    
    def test_multiple_observations(self):
        """Test extraction from multiple observations."""
        # Create a sample with multiple observations
        multi_observation = copy.deepcopy(self.sample_observation)
        # Add a second observation with different values
        second_obs = copy.deepcopy(self.sample_observation["features"][0])
        second_obs["properties"]["timestamp"] = "2023-05-01T13:00:00Z"
        second_obs["properties"]["temperature"]["value"] = 23.5
        multi_observation["features"].append(second_obs)
        
        # Extract data
        result = extract_atmospheric_data(multi_observation)
        
        # Check that two rows were extracted
        assert len(result) == 2
        
        # Check timestamps to verify both records are included
        assert result[0]["timestamp"] == "2023-05-01T12:00:00Z"
        assert result[1]["timestamp"] == "2023-05-01T13:00:00Z"
        
        # Check that temperature values are correct for each
        assert result[0]["temperature_C"] == 22.5
        assert result[1]["temperature_C"] == 23.5
    
    def test_error_in_cloud_layers(self):
        """Test handling of errors when processing cloud layers."""
        # Create a copy with problematic cloud layers
        error_observation = copy.deepcopy(self.sample_observation)
        # Set cloud layers to something that will cause an error when str() is called
        class BadCloudLayers:
            def __str__(self):
                raise ValueError("Cannot convert to string")
        
        error_observation["features"][0]["properties"]["cloudLayers"] = BadCloudLayers()
        
        # Extract data
        result = extract_atmospheric_data(error_observation)
        
        # Check that data was extracted but cloud_layers is None
        assert len(result) == 1
        assert result[0]["cloud_layers"] is None