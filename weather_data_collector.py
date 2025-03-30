"""
National Weather Service data collector for Ann Arbor, MI area.
Provides functionality to retrieve weather data from all stations in the area.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from tqdm import tqdm


def get_ann_arbor_weather_data(days_history=7):
    """
    Pull weather data from all weather stations in the Ann Arbor, MI area.

    Parameters:
    -----------
    days_history : int, optional
        Number of days of historical data to retrieve (default is 7)

    Returns:
    --------
    dict : Dictionary containing weather data from all stations, with station IDs as keys
    """
    # Ann Arbor coordinates (approximate center)
    lat, lon = 42.2808, -83.7430

    # Step 1: Find all weather stations around Ann Arbor
    # The NWS API uses grid points rather than direct lat/lon queries
    try:
        # Get the grid point for Ann Arbor
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        response = requests.get(points_url, headers={"User-Agent": "WeatherDataCollector/1.0"})
        response.raise_for_status()

        grid_data = response.json()
        grid_id = grid_data['properties']['gridId']
        grid_x = grid_data['properties']['gridX']
        grid_y = grid_data['properties']['gridY']

        # Step 2: Get a list of stations that provide observations for this grid point
        stations_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/stations"
        response = requests.get(stations_url, headers={"User-Agent": "WeatherDataCollector/1.0"})
        response.raise_for_status()

        stations_data = response.json()
        stations = stations_data['features']

        # Step 3: For each station, pull the latest observations and historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_history)
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        all_station_data = {}

        # Add a progress bar for station processing
        for station in tqdm(stations, desc="Processing weather stations", unit="station"):
            station_id = station['properties']['stationIdentifier']
            station_name = station['properties']['name']

            # Get observations for this station
            observations_url = f"https://api.weather.gov/stations/{station_id}/observations"
            params = {
                "start": start_date_str,
                "end": end_date_str
            }

            try:
                response = requests.get(
                    observations_url,
                    params=params,
                    headers={"User-Agent": "WeatherDataCollector/1.0"}
                )
                response.raise_for_status()

                obs_data = response.json()

                # Process the observations into a more usable format
                processed_obs = []
                # Optional inner progress bar for processing observations (hidden by default)
                # Set disable=False to show this nested progress bar
                for obs in tqdm(obs_data['features'],
                                desc=f"Processing {station_id} observations",
                                leave=False,
                                disable=True):
                    properties = obs['properties']

                    # Extract basic weather info
                    obs_time = properties.get('timestamp')
                    temperature = properties.get('temperature', {}).get('value')
                    dewpoint = properties.get('dewpoint', {}).get('value')
                    wind_speed = properties.get('windSpeed', {}).get('value')
                    wind_direction = properties.get('windDirection', {}).get('value')
                    barometric_pressure = properties.get('barometricPressure', {}).get('value')
                    relative_humidity = properties.get('relativeHumidity', {}).get('value')
                    precipitation = properties.get('precipitationLastHour', {}).get('value')

                    processed_obs.append({
                        'timestamp': obs_time,
                        'temperature_celsius': temperature,
                        'dewpoint_celsius': dewpoint,
                        'wind_speed_ms': wind_speed,
                        'wind_direction_degrees': wind_direction,
                        'barometric_pressure_pa': barometric_pressure,
                        'relative_humidity_percent': relative_humidity,
                        'precipitation_mm': precipitation
                    })

                # Convert to DataFrame for easier manipulation
                if processed_obs:
                    df = pd.DataFrame(processed_obs)

                    # Convert temperature from C to F
                    if 'temperature_celsius' in df.columns:
                        df['temperature_fahrenheit'] = df['temperature_celsius'].apply(
                            lambda x: (x * 9 / 5) + 32 if pd.notnull(x) else None
                        )

                    all_station_data[station_id] = {
                        'name': station_name,
                        'latitude': station['geometry']['coordinates'][1],
                        'longitude': station['geometry']['coordinates'][0],
                        'data': df
                    }
                else:
                    print(f"No observation data available for station {station_id}")

            except requests.exceptions.HTTPError as e:
                print(f"Error retrieving data for station {station_id}: {e}")
                continue

        return all_station_data

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return {}