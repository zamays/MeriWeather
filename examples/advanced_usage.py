"""
Advanced example showing how to use the MeriWeather package with custom options.
"""
import logging
from datetime import datetime, timedelta, timezone
import os
import pandas as pd
import matplotlib.pyplot as plt

from meriweather import find_stations, get_historical_observations, extract_atmospheric_data, save_to_csv
from meriweather.utils import setup_logging, validate_coordinates

def main():
    # Setup enhanced logging
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'meriweather.log')
    setup_logging(level=logging.DEBUG, log_file=log_file)
    
    logger = logging.getLogger('meriweather')
    logger.info("Starting advanced MeriWeather usage example")
    
    # User input for coordinates - example values for Chicago, IL
    lat, lon = 41.8781, -87.6298
    
    try:
        # Validate coordinates
        validate_coordinates(lat, lon)
        logger.info(f"Using coordinates: ({lat}, {lon})")
        
        # Time period for data collection (past 30 days)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        logger.info(f"Time range: {start_date.isoformat()} to {end_date.isoformat()}")
        
        # Find nearby stations
        stations = find_stations(lat, lon)
        
        if not stations:
            logger.error("No weather stations found near the specified coordinates")
            return
        
        # Process multiple stations (up to 3)
        max_stations = min(3, len(stations))
        logger.info(f"Found {len(stations)} stations, processing the closest {max_stations}")
        
        all_data = []
        station_ids = []
        
        # Process each station
        for i in range(max_stations):
            station = stations[i]
            station_id = station['properties']['stationIdentifier']
            station_name = station['properties']['name']
            station_ids.append(station_id)
            
            logger.info(f"Processing station {i+1}/{max_stations}: {station_id} - {station_name}")
            
            # Get historical observations
            observations = get_historical_observations(station_id, start_date, end_date)
            
            if observations:
                # Extract the data
                data = extract_atmospheric_data(observations)
                
                if data:
                    # Save to CSV
                    csv_path = save_to_csv(data, station_id)
                    logger.info(f"Data saved to {csv_path}")
                    
                    # Store for analysis
                    all_data.append(data)
                else:
                    logger.warning(f"No data extracted for station {station_id}")
            else:
                logger.warning(f"No observations retrieved for station {station_id}")
        
        # If we have data, perform some analysis
        if all_data:
            analyze_temperature_data(all_data, station_ids)
        else:
            logger.warning("No data collected for analysis")
    
    except ValueError as e:
        logger.error(f"Error in coordinates: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")

def analyze_temperature_data(all_data, station_ids):
    """
    Analyze and visualize temperature data from multiple stations.
    
    Args:
        all_data (list): List of data lists from different stations
        station_ids (list): List of station IDs corresponding to the data
    """
    logger = logging.getLogger('meriweather')
    logger.info("Analyzing temperature data")
    
    try:
        # Create DataFrames for each station
        dfs = []
        for i, data in enumerate(all_data):
            if data:
                df = pd.DataFrame(data)
                # Convert timestamp strings to datetime objects
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                # Set as index for time series analysis
                df.set_index('timestamp', inplace=True)
                # Add station identifier
                df['station_id'] = station_ids[i]
                dfs.append(df)
        
        if not dfs:
            logger.warning("No valid DataFrames created for analysis")
            return
            
        # Plot temperature data for each station
        plt.figure(figsize=(12, 6))
        
        for i, df in enumerate(dfs):
            if 'temperature_F' in df.columns:
                # Resample to hourly data for cleaner visualization
                hourly_temp = df['temperature_F'].resample('H').mean()
                plt.plot(hourly_temp.index, hourly_temp.values, label=station_ids[i])
        
        plt.title('Temperature Comparison Between Stations')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°F)')
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        output_dir = 'weather_data'
        os.makedirs(output_dir, exist_ok=True)
        plot_path = f"{output_dir}/temperature_comparison.png"
        plt.savefig(plot_path)
        
        logger.info(f"Temperature comparison plot saved to {plot_path}")
        
        # Calculate and display statistics
        logger.info("Temperature Statistics (°F):")
        for i, df in enumerate(dfs):
            if 'temperature_F' in df.columns:
                stats = df['temperature_F'].describe()
                logger.info(f"Station {station_ids[i]}:")
                logger.info(f"  Min: {stats['min']:.1f}°F")
                logger.info(f"  Max: {stats['max']:.1f}°F")
                logger.info(f"  Avg: {stats['mean']:.1f}°F")
                logger.info(f"  Std Dev: {stats['std']:.1f}°F")
    
    except Exception as e:
        logger.exception(f"Error analyzing temperature data: {e}")

if __name__ == "__main__":
    main()