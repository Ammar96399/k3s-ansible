import os
import time
import csv
from subprocess import call

CPU_METHODS = ["union"]
STRESS_TEST_LOG = "/home/kazem/benchmark/results/start_end_time.csv"

def initialize_log_file():
    if not os.path.isfile(STRESS_TEST_LOG):
        with open(STRESS_TEST_LOG, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["load", "start_time", "end_time"])

def perform_stress_test():
    for i in range(1):

        print(f"Stress testing ...")
        for load in range(0, 101, 10):
            start_time = time.time()
            print(f"Stressing at {load}%")
            call(["stress-ng", "-c", "0", "-l", str(load), "-t", "300s", "--cpu-method", "union"])
            end_time = time.time()

            with open(STRESS_TEST_LOG, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([load, start_time, end_time])

            time.sleep(60)

initialize_log_file()

perform_stress_test()

print("Main script finished.")