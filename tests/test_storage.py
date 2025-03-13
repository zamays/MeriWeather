"""
Unit tests for meriweather.storage module.
"""
import os
import csv
import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timezone
from meriweather.storage import save_to_csv, get_data_filepath

class TestStorage(unittest.TestCase):
    """Test cases for storage functions."""
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_csv(self, mock_file, mock_makedirs):
        """Test saving data to CSV file."""
        # Setup test data
        test_data = [
            {'timestamp': '2023-01-01T12:00:00Z', 'station': 'TEST1', 'temperature_C': 20, 'temperature_F': 68},
            {'timestamp': '2023-01-01T13:00:00Z', 'station': 'TEST1', 'temperature_C': 22, 'temperature_F': 71.6}
        ]
        station_id = 'TEST1'
        
        # Call function under test
        with patch('MeriWeather.storage.datetime') as mock_datetime:
            # Mock the datetime.now() to return a fixed value
            mock_now = datetime(2023, 1, 1, 14, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            # Ensure timezone.utc is available
            mock_datetime.timezone = timezone
            
            result = save_to_csv(test_data, station_id)
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with('weather_data', exist_ok=True)
        
        # Verify file was opened with correct name
        expected_filename = 'weather_data/TEST1_20230101_140000.csv'
        mock_file.assert_called_once_with(expected_filename, 'w', newline='', encoding='utf-8')
        
        # Verify CSV writing
        handle = mock_file()
        
        # Check that writerow was called for header and each data row
        self.assertEqual(handle.write.call_count, 4)  # Roughly 3 calls (header + 2 data rows)
        
        # Verify result
        self.assertEqual(result, expected_filename)
    
    def test_save_to_csv_empty_data(self):
        """Test save_to_csv with empty data."""
        result = save_to_csv([], 'TEST1')
        self.assertIsNone(result)
    
    @patch('os.makedirs')
    def test_get_data_filepath(self, mock_makedirs):
        """Test get_data_filepath function."""
        # Test with explicit timestamp
        test_time = datetime(2023, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        result = get_data_filepath('KORD', test_time)
        self.assertEqual(result, 'weather_data/KORD_20230115_123045.csv')
        
        # Test with default timestamp
        with patch('MeriWeather.storage.datetime') as mock_datetime:
            # Mock the datetime.now() to return a fixed value
            mock_now = datetime(2023, 1, 1, 14, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            # Ensure timezone.utc is available
            mock_datetime.timezone = timezone
            
            result = get_data_filepath('KORD')
            self.assertEqual(result, 'weather_data/KORD_20230101_140000.csv')
        
        # Verify directory creation
        mock_makedirs.assert_called_with('weather_data', exist_ok=True)

if __name__ == '__main__':
    unittest.main()