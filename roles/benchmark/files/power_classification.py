import os
import pandas as pd
import numpy as np
import argparse

def add_load_column(input_file, load_file, output_file):
    load_df = pd.read_csv(load_file)

    data_df = pd.read_csv(input_file)

    data_df['load'] = -1

    data_df["time"] = pd.to_numeric(data_df["time"], errors="coerce").fillna(-1).astype(int)
    data_df["time"] = data_df["time"].apply(lambda x: int(x))
    load_df["start_time"] = load_df["start_time"].apply(lambda x: int(x))
    load_df["end_time"] = load_df["end_time"].apply(lambda x: int(x))

    load_starts = load_df['start_time'].values
    load_ends = load_df['end_time'].values
    load_values = load_df['load'].values

    start_idx = np.searchsorted(load_starts, data_df['time'].values, side='right') - 1
    end_idx = np.searchsorted(load_ends, data_df['time'].values, side='right')

    mask = (start_idx == end_idx) & (start_idx >= 0) & (end_idx < len(load_df))
    data_df.loc[mask, 'load'] = load_values[start_idx[mask]]

    data_df.to_csv(output_file, index=False)

def main():
    parser = argparse.ArgumentParser(description='Add load column to CSV files in subfolders based on start and end times.')
    parser.add_argument('base_folder', type=str, help='Path to the base folder containing subfolders for each device')

    args = parser.parse_args()

    for device_folder in ['rpi4-1', 'rpi4-2', 'rpi5-1', 'rpi5-2']:
        input_file_path = os.path.join(args.base_folder, device_folder, f"{device_folder}_power_usage.csv")
        output_file_path = os.path.join(args.base_folder, device_folder, f"{device_folder}_power_usage_classified.csv")
        load_file_path = os.path.join(args.base_folder, device_folder, f"{device_folder}_start_end_time.csv")

        print(f"Processing {device_folder}...")
        print(f"Input file: {input_file_path}")
        
        print(f"Processing {device_folder}...")
        add_load_column(input_file_path, load_file_path, output_file_path)
        print(f"Classified power usage for {device_folder} saved to {output_file_path}")

if __name__ == "__main__":
    main()
