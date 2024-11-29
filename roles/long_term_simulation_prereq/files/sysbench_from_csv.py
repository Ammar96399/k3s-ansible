import csv
import sys
import subprocess
import os

WAIT_TIME = 15

def run_stress_ng(value):
    command = f"stress-ng --cpu 1 --cpu-method union -t {WAIT_TIME}s -l {value}"
    print(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error running stress-ng: {stderr.decode('utf-8')}")
    else:
        print(stdout.decode('utf-8'))

def main(folder_path, rpi_model):
    print(f"Reading files in folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.startswith("processed"):
            csv_path = os.path.join(folder_path, filename)
            print(f"Using file: {csv_path}")
            with open(csv_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    value = float(row[rpi_model])
                    print(f"Running stress-ng with value: {value * 100.0}")
                    run_stress_ng(int(value * 100.0))
            break
    else:
        print("No file starting with 'processed' found in the folder.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sysbench_from_csv.py <folder_path> <rpi_model>")
        sys.exit(1)
    
    folder_path = "/app/long_term_observatory/workload_"+sys.argv[1]
    rpi_model = sys.argv[2]
    print(f"Folder Path: {folder_path}, RPI Model: {rpi_model}")
    main(folder_path, rpi_model)