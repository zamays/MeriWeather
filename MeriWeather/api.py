"""
Functions for interacting with the National Weather Service API.
"""

import requests
import logging
from .config import (
    PACKAGE_NAME,
    PACKAGE_VERSION,
    PACKAGE_EMAIL
)

logger = logging.getLogger(__name__)


def get_api_headers():
    """
    Generate API headers using package information.

    Returns:
        dict: Headers dictionary for API requests
    """
    return {
        "User-Agent": f"({PACKAGE_NAME}/{PACKAGE_VERSION}, {PACKAGE_EMAIL})",
        "Accept": "application/geo+json",
    }


def find_stations(lat, lon):
    """
    Find weather stations near a specified latitude and longitude.

    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate

    Returns:
        list: List of station data dictionaries or None if no stations found
    """
    # Get headers using package information
    headers = get_api_headers()

    # First, we need to get the grid coordinates from the lat/lon
    point_url = f"https://api.weather.gov/points/{lat},{lon}"
    logger.info(f"Requesting metadata for coordinates ({lat}, {lon})")

    try:
        response = requests.get(point_url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for non-200 responses

        data = response.json()
        # Extract the URL for the nearest observation stations
        stations_url = data["properties"]["observationStations"]
        logger.debug(f"Observation stations URL: {stations_url}")

        # Get the list of stations
        logger.info("Retrieving nearby stations")
        stations_response = requests.get(stations_url, headers=headers, timeout=30)
        stations_response.raise_for_status()

        stations_data = stations_response.json()
        num_stations = len(stations_data["features"])
        logger.info(f"Found {num_stations} stations near coordinates")
        return stations_data["features"]

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during station lookup: {e}")
        return None


def get_historical_observations(station_id, start_date, end_date):
    """
    Retrieve historical weather observations for a specific station within a date range.

    Args:
        station_id (str): The station identifier
        start_date (datetime): The UTC start date/time for observations
        end_date (datetime): The UTC end date/time for observations

    Returns:
        dict: JSON response containing observation data or None if error
    """
    # Get headers using package information
    headers = get_api_headers()

    url = f"https://api.weather.gov/stations/{station_id}/observations"

    # Format dates as ISO 8601 with proper timezone handling
    params = {"start": start_date.isoformat(), "end": end_date.isoformat()}

    logger.info(
        f"Requesting observations for station {station_id} from {start_date.isoformat()} to {end_date.isoformat()}"
    )

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        observation_count = len(data.get("features", []))
        logger.info(
            f"Retrieved {observation_count} observations for station {station_id}"
        )
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving observations for station {station_id}: {e}")
        return None
