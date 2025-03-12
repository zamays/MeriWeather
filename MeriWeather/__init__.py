"""
A Python package for retrieving historical weather data from the National Weather Service API.
"""

from .api import find_stations, get_historical_observations
from .data_processing import extract_atmospheric_data
from .storage import save_to_csv

# Setup default logging when the package is imported
from .utils import setup_logging
setup_logging()

# Version information
__version__ = '0.1.0'