"""
Unit tests for meriweather.data_processing module.
"""
import unittest
from meriweather.data_processing import extract_atmospheric_data, convert_celsius_to_fahrenheit

class TestDataProcessing(unittest.TestCase):
    """Test cases for data processing functions."""
    
    def test_convert_celsius_to_fahrenheit(self):
        """Test temperature conversion function."""
        # Test normal values
        self.assertEqual(convert_celsius_to_fahrenheit(0), 32)
        self.assertEqual(convert_celsius_to_fahrenheit(100), 212)
        self.assertAlmostEqual(convert_celsius_to_fahrenheit(37), 98.6, places=1)
        self.assertAlmostEqual(convert_celsius_to_fahrenheit(-40), -40, places=1)
        
        # Test None value
        self.assertIsNone(convert_celsius_to_fahrenheit(None))
    
    def test_extract_atmospheric_data_empty(self):
        """Test extract_atmospheric_data with empty or invalid input."""
        # Test with None
        self.assertEqual(extract_atmospheric_data(None), [])
        
        # Test with empty dict
        self.assertEqual(extract_atmospheric_data({}), [])
        
        # Test with dict missing 'features'
        self.assertEqual(extract_atmospheric_data({'properties': {}}), [])
    
    def test_extract_atmospheric_data_valid(self):
        """Test extract_atmospheric_data with valid input."""
        # Create a simplified but realistic test observation
        test_observations = {
            'features': [
                {
                    'properties': {
                        'timestamp': '2023-01-01T12:00:00Z',
                        'station': 'KORD',
                        'temperature': {
                            'value': 20.0  # 20°C
                        },
                        'dewpoint': {
                            'value': 15.0
                        },
                        'windDirection': {
                            'value': 180
                        },
                        'windSpeed': {
                            'value': 5.0
                        },
                        'barometricPressure': {
                            'value': 101325
                        },
                        'textDescription': 'Partly cloudy'
                    }
                }
            ]
        }
        
        # Extract data
        result = extract_atmospheric_data(test_observations)
        
        # Verify results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['timestamp'], '2023-01-01T12:00:00Z')
        self.assertEqual(result[0]['station'], 'KORD')
        self.assertEqual(result[0]['temperature_C'], 20.0)
        self.assertEqual(result[0]['temperature_F'], 68.0)  # 20°C = 68°F
        self.assertEqual(result[0]['dewpoint'], 15.0)
        self.assertEqual(result[0]['windDirection'], 180)
        self.assertEqual(result[0]['windSpeed'], 5.0)
        self.assertEqual(result[0]['barometricPressure'], 101325)
        self.assertEqual(result[0]['text_description'], 'Partly cloudy')
    
    def test_extract_atmospheric_data_missing_fields(self):
        """Test extract_atmospheric_data with missing fields."""
        # Create test observation with missing fields
        test_observations = {
            'features': [
                {
                    'properties': {
                        'timestamp': '2023-01-01T12:00:00Z',
                        'station': 'KORD',
                        # temperature is missing
                        'dewpoint': None,  # null value
                        'textDescription': 'Partly cloudy'
                    }
                }
            ]
        }
        
        # Extract data
        result = extract_atmospheric_data(test_observations)
        
        # Verify results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['timestamp'], '2023-01-01T12:00:00Z')
        self.assertEqual(result[0]['station'], 'KORD')
        self.assertIsNone(result[0]['temperature_C'])
        self.assertIsNone(result[0]['temperature_F'])
        self.assertIsNone(result[0]['dewpoint'])
        self.assertEqual(result[0]['text_description'], 'Partly cloudy')
    
    def test_extract_atmospheric_data_multiple_observations(self):
        """Test extract_atmospheric_data with multiple observations."""
        # Create test data with multiple observations
        test_observations = {
            'features': [
                {
                    'properties': {
                        'timestamp': '2023-01-01T12:00:00Z',
                        'station': 'KORD',
                        'temperature': {
                            'value': 20.0
                        }
                    }
                },
                {
                    'properties': {
                        'timestamp': '2023-01-01T13:00:00Z',
                        'station': 'KORD',
                        'temperature': {
                            'value': 22.0
                        }
                    }
                }
            ]
        }
        
        # Extract data
        result = extract_atmospheric_data(test_observations)
        
        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['timestamp'], '2023-01-01T12:00:00Z')
        self.assertEqual(result[0]['temperature_C'], 20.0)
        self.assertEqual(result[1]['timestamp'], '2023-01-01T13:00:00Z')
        self.assertEqual(result[1]['temperature_C'], 22.0)

if __name__ == '__main__':
    unittest.main()