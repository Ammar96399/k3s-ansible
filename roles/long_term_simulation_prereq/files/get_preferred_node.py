import sys

def get_preferred_nodes(file_path):
    preferred_nodes = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]: 
            parts = line.strip().split(',')
            if len(parts) > 1:
                preferred_nodes.append(parts[1])
    return preferred_nodes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_preferred_node.py <workload_id>")
        sys.exit(1)

    workload_id = int(sys.argv[1])
    file_path = '/home/kazem/simulation/long_term_simulation/preferred_nodes.csv'
    preferred_nodes = get_preferred_nodes(file_path)
    print(preferred_nodes[workload_id - 1])