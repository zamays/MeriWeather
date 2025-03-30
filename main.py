"""
Main script for collecting and processing weather data from Ann Arbor, MI.
This script uses the weather_data_collector module to retrieve data from the NWS API
and saves it to a parquet file with snappy compression.

It includes incremental collection capability, which means it will check for existing
data and only collect new data since the last collection.
"""

import os
import argparse
from tqdm import tqdm
import pandas as pd

# Import the weather data collector functions
from weather_data_collector import get_ann_arbor_weather_data, merge_with_existing_data


def main():
    """
    Main function to collect weather data and save it to a parquet file.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Collect weather data from Ann Arbor, MI area')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days of historical data to retrieve (default: 7, only used for new collections)')
    parser.add_argument('--output', type=str, default='data/ann_arbor_weather_data.parquet',
                        help='Output filename (default: data/ann_arbor_weather_data.parquet)')
    parser.add_argument('--force-new', action='store_true',
                        help='Force new data collection ignoring existing data')

    args = parser.parse_args()

    print(f"Weather Data Collection Tool for Ann Arbor, MI")
    print(f"{'=' * 50}")

    # Check if we're forcing a new collection
    if args.force_new and os.path.exists(args.output):
        print(f"Forcing new collection. Ignoring existing data in {args.output}")
        # Optionally, create backup of existing file
        backup_file = f"{args.output}.backup"
        print(f"Creating backup of existing data: {backup_file}")
        os.rename(args.output, backup_file)

    # Get weather data, taking into account existing data
    new_station_data, existing_data = get_ann_arbor_weather_data(
        days_history=args.days,
        output_file=args.output if not args.force_new else None
    )

    # Merge the new data with any existing data
    combined_df = merge_with_existing_data(new_station_data, existing_data)

    # Save the combined data
    if not combined_df.empty:
        # Save to parquet file with snappy compression
        combined_df.to_parquet(args.output, compression='snappy')

        # Get file size for reporting
        file_size_mb = os.path.getsize(args.output) / (1024 * 1024)

        print(f"\nAll data saved to {args.output}")
        print(f"Total observations: {len(combined_df)}")
        print(f"File size: {file_size_mb:.2f} MB")
    else:
        print("\nNo data was collected or found.")


if __name__ == "__main__":
    main()