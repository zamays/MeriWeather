import pytest
from unittest.mock import patch, Mock
import datetime
import requests
from meriweather import get_api_headers, find_stations, get_historical_observations
from meriweather.config import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_EMAIL

class TestGetApiHeaders:
    def test_headers_format(self):
        """Test that headers are correctly formatted with package info."""
        headers = get_api_headers()
        
        assert headers["User-Agent"] == f"({PACKAGE_NAME}/{PACKAGE_VERSION}, {PACKAGE_EMAIL})"
        assert headers["Accept"] == "application/geo+json"
        assert len(headers) == 2

class TestFindStations:
    @patch('requests.get')
    def test_successful_station_lookup(self, mock_get):
        """Test successful retrieval of stations near coordinates."""
        # Mock the first response (points endpoint)
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "observationStations": "https://api.weather.gov/gridpoints/ABC/1,2/stations"
            }
        }
        mock_points_response.raise_for_status.return_value = None
        
        # Mock the second response (stations endpoint)
        mock_stations_response = Mock()
        mock_stations_response.json.return_value = {
            "features": [
                {"id": "station1", "properties": {"name": "Station 1"}},
                {"id": "station2", "properties": {"name": "Station 2"}}
            ]
        }
        mock_stations_response.raise_for_status.return_value = None
        
        # Configure the mock to return different responses for different URLs
        def get_side_effect(url, headers, timeout):
            if "points" in url:
                return mock_points_response
            else:
                return mock_stations_response
                
        mock_get.side_effect = get_side_effect
        
        # Call the function
        result = find_stations(35.123, -75.456)
        
        # Assertions
        assert len(result) == 2
        assert result[0]["id"] == "station1"
        assert result[1]["id"] == "station2"
        
        # Verify both API calls were made with correct parameters
        assert mock_get.call_count == 2
        mock_get.assert_any_call("https://api.weather.gov/points/35.123,-75.456", 
                                headers=get_api_headers(), 
                                timeout=30)
    
    @patch('requests.get')
    def test_request_exception_handling(self, mock_get):
        """Test error handling when API request fails."""
        # Configure mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Call function and check result
        result = find_stations(35.123, -75.456)
        
        # Should return None on error
        assert result is None
        
    @patch('requests.get')
    def test_http_error_handling(self, mock_get):
        """Test handling of HTTP errors."""
        # Configure first response to raise HTTPError
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Call function
        result = find_stations(35.123, -75.456)
        
        # Should return None on HTTP error
        assert result is None

class TestGetHistoricalObservations:
    @patch('requests.get')
    def test_successful_observations_retrieval(self, mock_get):
        """Test successful retrieval of historical observations."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "features": [
                {"id": "obs1", "properties": {"timestamp": "2023-01-01T12:00:00Z"}},
                {"id": "obs2", "properties": {"timestamp": "2023-01-01T13:00:00Z"}}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test data
        station_id = "KXYZ"
        start_date = datetime.datetime(2023, 1, 1, 12, 0)
        end_date = datetime.datetime(2023, 1, 1, 14, 0)
        
        # Call the function
        result = get_historical_observations(station_id, start_date, end_date)
        
        # Assertions
        assert len(result["features"]) == 2
        
        # Verify API call parameters
        mock_get.assert_called_once_with(
            f"https://api.weather.gov/stations/{station_id}/observations",
            headers=get_api_headers(),
            params={"start": start_date.isoformat(), "end": end_date.isoformat()},
            timeout=30
        )
    
    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """Test error handling when retrieving observations."""
        # Configure mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Test data
        station_id = "KXYZ"
        start_date = datetime.datetime(2023, 1, 1, 12, 0)
        end_date = datetime.datetime(2023, 1, 1, 14, 0)
        
        # Call function
        result = get_historical_observations(station_id, start_date, end_date)
        
        # Should return None on error
        assert result is None
    
    @patch('requests.get')
    def test_date_format_handling(self, mock_get):
        """Test proper formatting of date parameters."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {"features": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test data with timezone info
        station_id = "KXYZ"
        start_date = datetime.datetime(2023, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime(2023, 1, 2, 12, 0, tzinfo=datetime.timezone.utc)
        
        # Call the function
        get_historical_observations(station_id, start_date, end_date)
        
        # Verify date parameters were correctly formatted with ISO 8601
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["start"] == "2023-01-01T12:00:00+00:00"
        assert kwargs["params"]["end"] == "2023-01-02T12:00:00+00:00"