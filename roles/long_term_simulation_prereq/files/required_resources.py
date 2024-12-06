import csv
import argparse

def get_resource_limit(workload, model):
    workload_key = f"workload_{workload}"
    with open('/home/kazem/simulation/long_term_simulation/long_term_observatory.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['workload'] == workload_key:
                if model == 'rpi3b':
                    return row['rpi3b_required']
                elif model == 'rpi3b+':
                    return row['rpi3bplus_required']
                elif model == 'rpi4b':
                    return row['rpi4b_required']
                elif model == 'rpi5':
                    return row['rpi5_required']
                else:
                    raise ValueError("Invalid model specified")
        raise ValueError("Workload not found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get resource limit for a given workload and model.')
    parser.add_argument('workload', type=int, help='The workload number to look up')
    parser.add_argument('model', type=str, help='The model to look up')

    args = parser.parse_args()
    workload = args.workload
    model = args.model

    try:
        resource_limit = get_resource_limit(workload, model)
        print(f"{resource_limit}")
    except ValueError as e:
        print(e)
