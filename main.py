"""
Main script for collecting and processing weather data from Ann Arbor, MI.
This script uses the weather_data_collector module to retrieve data from the NWS API
and saves it to a parquet file with snappy compression.
"""

import os
import argparse
from tqdm import tqdm
import pandas as pd

# Import the weather data collector function
from weather_data_collector import get_ann_arbor_weather_data


def main():
    """
    Main function to collect weather data and save it to a parquet file.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Collect weather data from Ann Arbor, MI area')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days of historical data to retrieve (default: 7)')
    parser.add_argument('--output', type=str, default='ann_arbor_weather_data.parquet',
                        help='Output filename (default: ann_arbor_weather_data.parquet)')

    args = parser.parse_args()

    print(f"Collecting weather data for the past {args.days} days from Ann Arbor, MI area...")

    # Get weather data for the specified number of days
    weather_data = get_ann_arbor_weather_data(days_history=args.days)

    # Print summary information
    print(f"\nRetrieved data from {len(weather_data)} weather stations in the Ann Arbor area:")

    # Create a list to hold all dataframes
    all_dfs = []

    # Add progress bar for preparing data for export
    for station_id, station_info in tqdm(weather_data.items(),
                                         desc="Preparing data for export",
                                         unit="station"):
        data_count = len(station_info['data']) if 'data' in station_info else 0
        print(f"  - {station_info['name']} ({station_id}): {data_count} observations")

        # Add dataframe to the list of all dataframes, with station information added
        if data_count > 0:
            df = station_info['data'].copy()

            # Add station information as columns
            df['station_id'] = station_id
            df['station_name'] = station_info['name']
            df['station_latitude'] = station_info['latitude']
            df['station_longitude'] = station_info['longitude']

            all_dfs.append(df)

    # Combine all dataframes into one
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)

        # Save to parquet file with snappy compression
        output_file = args.output
        combined_df.to_parquet(output_file, compression='snappy')

        # Get file size for reporting
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

        print(f"\nAll data saved to {output_file}")
        print(f"Total observations: {len(combined_df)}")
        print(f"File size: {file_size_mb:.2f} MB")
    else:
        print("\nNo data was collected from any station.")


if __name__ == "__main__":
    main()