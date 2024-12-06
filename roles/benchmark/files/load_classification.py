import os
import pandas as pd
import numpy as np
import argparse
from tqdm import tqdm

def add_load_column(data_file, load_file, output_file):
    data_df = pd.read_csv(data_file)
    load_df = pd.read_csv(load_file)

    data_df["Timestamp (s)"] = pd.to_numeric(data_df["Timestamp (s)"], errors="coerce").fillna(-1).astype(int)
    data_df["Timestamp (s)"] = data_df["Timestamp (s)"].apply(lambda x: int(x))
    load_df["start_time"] = load_df["start_time"].apply(lambda x: int(x))
    load_df["end_time"] = load_df["end_time"].apply(lambda x: int(x))
    
    data_df["load"] = -1

    for _, load_row in load_df.iterrows():
        start_time = load_row["start_time"]
        end_time = load_row["end_time"]
        load_value = load_row["load"]

        data_df.loc[
            (data_df["Timestamp (s)"] >= start_time) & (data_df["Timestamp (s)"] <= end_time), 
            "load"
        ] = load_value

    data_df.to_csv(output_file, index=False)

def main():
    parser = argparse.ArgumentParser(description='Add load column to CSV files in subfolders based on start and end times.')
    parser.add_argument('base_folder', type=str, help='Path to the base folder containing subfolders for each device')

    args = parser.parse_args()

    hostname = os.uname()[1]
    
    for device_folder in ['rpi4-1', 'rpi4-2', 'rpi5-1', 'rpi5-2']:
        input_file_path = os.path.join(args.base_folder, device_folder, f"{device_folder}_cpu_usage.csv")
        output_file_path = os.path.join(args.base_folder, device_folder, f"{device_folder}_cpu_usage_classified.csv")
        load_file_path = os.path.join(args.base_folder, device_folder, f"{device_folder}_start_end_time.csv")

        print(f"Processing {device_folder}...")
        print(f"Input file: {input_file_path}")
        
        print(f"Processing {device_folder}...")
        add_load_column(input_file_path, load_file_path, output_file_path)
        print(f"Classified power usage for {device_folder} saved to {output_file_path}")
            

if __name__ == "__main__":
    main()
