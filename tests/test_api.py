"""
Unit tests for meriweather.api module.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from meriweather.api import get_api_headers, find_stations, get_historical_observations
from meriweather.config import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_EMAIL

class TestAPI(unittest.TestCase):
    """Test cases for API functions."""
    
    def test_get_api_headers(self):
        """Test that API headers are correctly generated."""
        headers = get_api_headers()
        
        # Check User-Agent format
        expected_user_agent = f"({PACKAGE_NAME}/{PACKAGE_VERSION}, {PACKAGE_EMAIL})"
        self.assertEqual(headers["User-Agent"], expected_user_agent)
        
        # Check Accept header
        self.assertEqual(headers["Accept"], "application/geo+json")
    
    @patch('requests.get')
    def test_find_stations_success(self, mock_get):
        """Test finding stations with successful API responses."""
        # Mock responses for the two API calls
        mock_point_response = MagicMock()
        mock_point_response.json.return_value = {
            "properties": {
                "observationStations": "https://api.weather.gov/gridpoints/LOT/65,73/stations"
            }
        }
        
        mock_stations_response = MagicMock()
        mock_stations_response.json.return_value = {
            "features": [
                {
                    "properties": {
                        "stationIdentifier": "KORD",
                        "name": "Chicago O'Hare International Airport"
                    }
                },
                {
                    "properties": {
                        "stationIdentifier": "KMDW",
                        "name": "Chicago Midway Airport"
                    }
                }
            ]
        }
        
        # Set up the mock to return the appropriate response for each URL
        def mock_get_side_effect(url, headers, timeout):
            if 'points' in url:
                return mock_point_response
            elif 'stations' in url:
                return mock_stations_response
            return None
        
        mock_get.side_effect = mock_get_side_effect
        
        # Call the function under test
        result = find_stations(41.8781, -87.6298)
        
        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['properties']['stationIdentifier'], 'KORD')
        self.assertEqual(result[1]['properties']['stationIdentifier'], 'KMDW')
        
        # Verify that requests.get was called twice with appropriate headers
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.get')
    def test_find_stations_error(self, mock_get):
        """Test error handling in find_stations."""
        # Mock the requests.get to raise an exception
        mock_get.side_effect = Exception("API Error")
        
        # Call the function under test
        result = find_stations(41.8781, -87.6298)
        
        # Verify that None is returned on error
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_get_historical_observations_success(self, mock_get):
        """Test retrieving historical observations with successful API response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "features": [
                {"properties": {"timestamp": "2023-01-01T12:00:00Z"}},
                {"properties": {"timestamp": "2023-01-01T13:00:00Z"}}
            ]
        }
        mock_get.return_value = mock_response
        
        # Test date range
        start_date = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        
        # Call the function under test
        result = get_historical_observations('KORD', start_date, end_date)
        
        # Verify the result
        self.assertEqual(len(result['features']), 2)
        
        # Verify that requests.get was called with the correct URL and parameters
        expected_url = f"https://api.weather.gov/stations/KORD/observations"
        expected_params = {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
        mock_get.assert_called_with(
            expected_url,
            headers=get_api_headers(),
            params=expected_params,
            timeout=30
        )
    
    @patch('requests.get')
    def test_get_historical_observations_error(self, mock_get):
        """Test error handling in get_historical_observations."""
        # Mock the requests.get to raise an exception
        mock_get.side_effect = Exception("API Error")
        
        # Test date range
        start_date = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        
        # Call the function under test
        result = get_historical_observations('KORD', start_date, end_date)
        
        # Verify that None is returned on error
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()