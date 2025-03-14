"""
Main test suite for the MeriWeather package.
Run this file to execute all unit tests for the package.
"""
import unittest
import sys
import os

# Add parent directory to path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from tests.test_api import TestAPI
from tests.test_data_processing import TestDataProcessing
from tests.test_storage import TestStorage
from tests.test_utils import TestUtils

def run_test_suite():
    """Run all tests for the MeriWeather package."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == '__main__':
    result = run_test_suite()
    # Exit with non-zero code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)