"""
National Weather Service data collector for Ann Arbor, MI area.
Provides functionality to retrieve weather data from all stations in the area.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time
import os
from tqdm import tqdm


def get_ann_arbor_weather_data(days_history=7, output_file='data/ann_arbor_weather_data.parquet',
                               start_date=None, end_date=None, chunk_days=30):
    """
    Pull weather data from all weather stations in the Ann Arbor, MI area.

    If an existing output file is found, data collection will start from
    the last recorded timestamp in that file.

    Parameters:
    -----------
    days_history : int, optional
        Number of days of historical data to retrieve (default is 7)
        Only used if no existing data file is found and start_date is not specified

    output_file : str, optional
        Path to the output parquet file (default is 'data/ann_arbor_weather_data.parquet')
        Used to check for existing data

    start_date : datetime or str, optional
        Specific start date for data collection
        If string, format should be 'YYYY-MM-DD'
        If specified, days_history is ignored for new collections

    end_date : datetime or str, optional
        Specific end date for data collection (defaults to current time)
        If string, format should be 'YYYY-MM-DD'

    chunk_days : int, optional
        Number of days to request in each API chunk to avoid rate limits
        Larger requests may fail due to API limitations

    Returns:
    --------
    tuple : (new_station_data, existing_data)
        new_station_data: Dictionary containing weather data from all stations
        existing_data: DataFrame with existing data or empty dict if none
    """
    # Ann Arbor coordinates (approximate center)
    lat, lon = 42.2808, -83.7430

    # Process date inputs if provided as strings
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Set end_date to now if not specified
    if end_date is None:
        end_date = datetime.now(timezone.utc)

    # Check for existing data file and determine start date
    existing_data_start_date = None
    existing_data = {}
    existing_stations = set()

    # Add rate limiting implementation
    def make_request(url, params=None, headers=None):
        """Helper function with rate limiting and retries"""
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers)

                # Check for rate limiting (HTTP 429)
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', retry_delay * (attempt + 1)))
                    print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"Request failed: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

        return None  # Should not reach here due to the raise in the last iteration

    if os.path.exists(output_file):
        try:
            print(f"Found existing data file: {output_file}")
            existing_df = pd.read_parquet(output_file)

            if not existing_df.empty and 'timestamp' in existing_df.columns:
                # Convert timestamp strings to datetime objects
                existing_df['timestamp_dt'] = pd.to_datetime(existing_df['timestamp'])

                # Get the latest timestamp
                latest_timestamp = existing_df['timestamp_dt'].max()

                # Use the latest timestamp as our start date (if not explicitly specified)
                # Add a small buffer (1 hour) to avoid duplicates
                existing_data_start_date = latest_timestamp + timedelta(hours=1)

                print(f"Latest data timestamp: {latest_timestamp}")

                # Get the earliest timestamp for user info
                earliest_timestamp = existing_df['timestamp_dt'].min()
                print(f"Earliest data timestamp: {earliest_timestamp}")
                print(f"Existing data spans {(latest_timestamp - earliest_timestamp).days} days")

                # Store station IDs for reference
                if 'station_id' in existing_df.columns:
                    existing_stations = set(existing_df['station_id'].unique())
                    print(f"Found {len(existing_stations)} existing stations in data file")

                # Keep the existing data for merging later
                existing_data = existing_df
        except Exception as e:
            print(f"Error reading existing data file: {e}")
            print("Starting fresh data collection")
            existing_data_start_date = None

    # Determine final start date
    if start_date is not None:
        # If explicit start date provided, use it
        collection_start_date = start_date
        print(f"Using specified start date: {collection_start_date}")
    elif existing_data_start_date is not None:
        # If incremental collection, start from last data point
        collection_start_date = existing_data_start_date
        print(f"Continuing data collection from: {collection_start_date}")
    else:
        # Default to days_history
        collection_start_date = end_date - timedelta(days=days_history)
        print(f"Starting new data collection from: {collection_start_date}")

    # Calculate total days we're requesting
    total_days = (end_date - collection_start_date).days
    print(f"Requesting {total_days} days of weather data from {collection_start_date.date()} to {end_date.date()}")

    # Step 1: Find all weather stations around Ann Arbor
    # The NWS API uses grid points rather than direct lat/lon queries
    try:
        # Get the grid point for Ann Arbor
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        response = make_request(points_url, headers={"User-Agent": "WeatherDataCollector/1.0"})
        response.raise_for_status()

        grid_data = response.json()
        grid_id = grid_data['properties']['gridId']
        grid_x = grid_data['properties']['gridX']
        grid_y = grid_data['properties']['gridY']

        # Step 2: Get a list of stations that provide observations for this grid point
        stations_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/stations"
        response = make_request(stations_url, headers={"User-Agent": "WeatherDataCollector/1.0"})
        response.raise_for_status()

        stations_data = response.json()
        stations = stations_data['features']

        print(f"Found {len(stations)} weather stations for grid point {grid_id} {grid_x},{grid_y}")

        # Step 3: Split the date range into chunks to avoid API limitations
        all_station_data = {}

        # Calculate date chunks
        current_start = collection_start_date
        chunk_count = 0

        while current_start < end_date:
            chunk_count += 1
            chunk_end = min(current_start + timedelta(days=chunk_days), end_date)

            # Format dates for API requests
            start_date_str = current_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_date_str = chunk_end.strftime("%Y-%m-%dT%H:%M:%SZ")

            print(f"\nProcessing chunk {chunk_count}: {current_start.date()} to {chunk_end.date()} ({(chunk_end - current_start).days} days)")

            # When processing stations and chunks, add delay between requests
            for station in tqdm(stations, desc=f"Processing stations for chunk {chunk_count}", unit="station"):
                station_id = station['properties']['stationIdentifier']
                station_name = station['properties']['name']

                # Get observations for this station
                observations_url = f"https://api.weather.gov/stations/{station_id}/observations"
                params = {
                    "start": start_date_str,
                    "end": end_date_str
                }

                try:
                    response = make_request(
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
                                lambda x: (x * 9/5) + 32 if pd.notnull(x) else None
                            )

                        if station_id in all_station_data:
                            # Append to existing data for this station
                            all_station_data[station_id]['data'] = pd.concat(
                                [all_station_data[station_id]['data'], df],
                                ignore_index=True
                            )
                        else:
                            # Create new entry for this station
                            all_station_data[station_id] = {
                                'name': station_name,
                                'latitude': station['geometry']['coordinates'][1],
                                'longitude': station['geometry']['coordinates'][0],
                                'data': df
                            }
                    else:
                        print(f"No observation data available for station {station_id} in this chunk")

                except requests.exceptions.HTTPError as e:
                    print(f"Error retrieving data for station {station_id}: {e}")
                    continue

                # Add a small delay between station requests to be nice to the API
                time.sleep(0.5)  # 500ms pause between stations

            # Move to next chunk
            current_start = chunk_end

            # Between chunks, add a longer delay
            time.sleep(2)  # 2 second pause between chunks

        return all_station_data, existing_data

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return {}, existing_data


def merge_with_existing_data(new_station_data, existing_data):
    """
    Merge newly collected station data with existing data.

    Parameters:
    -----------
    new_station_data : dict
        Dictionary of newly collected station data
    existing_data : DataFrame or dict
        Existing data as a DataFrame or empty dict

    Returns:
    --------
    DataFrame : Combined data frame with old and new data
    """
    # Create a list to hold all dataframes
    all_dfs = []

    # Process new station data
    for station_id, station_info in tqdm(new_station_data.items(),
                                       desc="Preparing new data for export",
                                       unit="station"):
        data_count = len(station_info['data']) if 'data' in station_info else 0
        print(f"  - {station_info['name']} ({station_id}): {data_count} new observations")

        # Add dataframe to the list of all dataframes, with station information added
        if data_count > 0:
            df = station_info['data'].copy()

            # Add station information as columns
            df['station_id'] = station_id
            df['station_name'] = station_info['name']
            df['station_latitude'] = station_info['latitude']
            df['station_longitude'] = station_info['longitude']

            all_dfs.append(df)

    # Combine all new dataframes
    if all_dfs:
        new_df = pd.concat(all_dfs, ignore_index=True)

        # If we have existing data, merge with new data
        if isinstance(existing_data, pd.DataFrame) and not existing_data.empty:
            # Remove timestamp_dt column if it exists (we added it temporarily)
            if 'timestamp_dt' in existing_data.columns:
                existing_data = existing_data.drop(columns=['timestamp_dt'])

            # Combine existing and new data
            combined_df = pd.concat([existing_data, new_df], ignore_index=True)

            # Drop duplicates based on station_id and timestamp
            combined_df = combined_df.drop_duplicates(subset=['station_id', 'timestamp'], keep='last')

            print(f"Added {len(new_df)} new observations to {len(existing_data)} existing observations")
            print(f"After removing duplicates: {len(combined_df)} total observations")

            return combined_df
        else:
            return new_df
    elif isinstance(existing_data, pd.DataFrame) and not existing_data.empty:
        # If no new data but we have existing data, return existing data
        # Remove timestamp_dt column if it exists
        if 'timestamp_dt' in existing_data.columns:
            existing_data = existing_data.drop(columns=['timestamp_dt'])
        return existing_data
    else:
        # No data at all
        return pd.DataFrame()