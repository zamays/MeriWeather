"""
Unit tests for meriweather.utils module.
"""
import os
import logging
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from meriweather.utils import setup_logging, validate_coordinates, format_date

class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset logging before each test
        logging.getLogger('meriweather').handlers = []
    
    def test_setup_logging_console_only(self):
        """Test setup_logging with console output only."""
        logger = setup_logging(level=logging.DEBUG)
        
        # Check logger level
        self.assertEqual(logger.level, logging.DEBUG)
        
        # Should have exactly one handler (console)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
    
    @patch('os.makedirs')
    def test_setup_logging_with_file(self, mock_makedirs):
        """Test setup_logging with file output."""
        test_log_file = "test_logs/test.log"
        
        logger = setup_logging(level=logging.INFO, log_file=test_log_file)
        
        # Check logger level
        self.assertEqual(logger.level, logging.INFO)
        
        # Should have exactly two handlers (console and file)
        self.assertEqual(len(logger.handlers), 2)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertIsInstance(logger.handlers[1], logging.FileHandler)
        
        # Check that directory was created
        mock_makedirs.assert_called_once_with("test_logs", exist_ok=True)
    
    def test_validate_coordinates_valid(self):
        """Test validate_coordinates with valid coordinates."""
        # Test valid coordinates
        self.assertTrue(validate_coordinates(0, 0))
        self.assertTrue(validate_coordinates(90, 180))
        self.assertTrue(validate_coordinates(-90, -180))
        self.assertTrue(validate_coordinates(45.5, -120.5))
        
        # Test valid string coordinates (should be converted)
        self.assertTrue(validate_coordinates("45", "-120"))
    
    def test_validate_coordinates_invalid(self):
        """Test validate_coordinates with invalid coordinates."""
        # Test invalid latitude
        with self.assertRaises(ValueError):
            validate_coordinates(91, 0)
        
        with self.assertRaises(ValueError):
            validate_coordinates(-91, 0)
        
        # Test invalid longitude
        with self.assertRaises(ValueError):
            validate_coordinates(0, 181)
        
        with self.assertRaises(ValueError):
            validate_coordinates(0, -181)
        
        # Test non-numeric coordinates
        with self.assertRaises(ValueError):
            validate_coordinates("invalid", 0)
        
        with self.assertRaises(ValueError):
            validate_coordinates(0, "invalid")
    
    def test_format_date(self):
        """Test format_date function."""
        # Test with UTC datetime
        test_date = datetime(2023, 1, 15, 12, 30, 45)
        expected = "2023-01-15T12:30:45"
        self.assertEqual(format_date(test_date), expected)
        
        # Test with non-datetime input
        with self.assertRaises(TypeError):
            format_date("2023-01-15")

if __name__ == '__main__':
    unittest.main()