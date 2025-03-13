# MeriWeather

A Python package for retrieving historical weather data from the National Weather Service API.

## Features

- Find weather stations near a specified latitude/longitude
- Retrieve historical weather observations for a specific time period
- Extract and process atmospheric data (temperature, pressure, humidity, etc.)
- Save data to CSV files for further analysis
- Logging support for troubleshooting

## Installation

### From PyPI

```bash
pip install meriweather
```

### From source

```bash
git clone https://github.com/zamays/MeriWeather.git
cd MeriWeather
pip install -e .
```

## Quick Start

```python
from datetime import datetime, timedelta, timezone
from meriweather import find_stations, get_historical_observations, extract_atmospheric_data, save_to_csv

# Coordinates (Ann Arbor, Michigan)
lat, lon = 42.279594, -83.732124

# Time period for data collection (past 7 days)
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=7)

# Find nearby stations
stations = find_stations(lat, lon)

if stations:
    # Process first station
    station_id = stations[0]['properties']['stationIdentifier']
    
    # Get historical observations
    observations = get_historical_observations(station_id, start_date, end_date)
    
    if observations:
        # Extract and save the data
        data = extract_atmospheric_data(observations)
        csv_path = save_to_csv(data, station_id)
        print(f"Data saved to {csv_path}")
```

## Advanced Usage

See the `examples/advanced_usage.py` file for a more comprehensive example with 
multiple stations, data visualization and error handling.

## API Reference

### Finding Weather Stations

```python
from meriweather import find_stations

# Find stations near coordinates
stations = find_stations(latitude, longitude)

# Get the station identifier
station_id = stations[0]['properties']['stationIdentifier']
```

### Retrieving Weather Observations

```python
from meriweather import get_historical_observations
from datetime import datetime, timedelta, timezone

# Define time period (past 30 days)
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=30)

# Get observations
observations = get_historical_observations(station_id, start_date, end_date)
```

### Processing Weather Data

```python
from meriweather import extract_atmospheric_data

# Extract relevant data from observations
data = extract_atmospheric_data(observations)

# Data contains:
# - temperature (C and F)
# - dewpoint
# - wind direction and speed
# - barometric pressure
# - visibility
# - humidity
# - precipitation
# - etc.
```

### Saving Data

```python
from meriweather import save_to_csv

# Save to CSV
csv_path = save_to_csv(data, station_id)
print(f"Data saved to {csv_path}")
```

## Running Tests

```bash
# Run all tests
python -m tests.test_suite

# Run a specific test module
python -m unittest tests.test_utils
```

## License

MIT License

## Author

Zachary Mays