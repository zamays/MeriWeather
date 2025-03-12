"""
Basic example showing how to use the weather_nws package.
"""
from datetime import datetime, timedelta, timezone
from meriweather import find_stations, get_historical_observations, extract_atmospheric_data, save_to_csv

def main():
    # Coordinates (Ann Arbor, Michigan)
    # You can modify these coordinates as needed
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
            save_to_csv(data, station_id)

if __name__ == "__main__":
    main()