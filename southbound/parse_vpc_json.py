import json
from ruamel.yaml import YAML
import random
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

yaml_file_path = os.path.join(current_directory, '..', 'automation', 'variables', 'create_vpc_variables.yml')
json_file_path = os.path.join(current_directory, '..', 'database', 'vpc_data.json')
# Function to generate random prefix
def generate_random_prefix(used_prefixes):
    prefix = ".".join([str(random.randint(0, 255)) for _ in range(3)])
    while prefix in used_prefixes:
        prefix = ".".join([str(random.randint(0, 255)) for _ in range(3)])
    return prefix

# Load JSON data from file
with open(json_file_path) as f:
    data = json.load(f)

# Load used prefixes from file or initialize an empty list
try:
    with open('used_prefixes.txt', 'r') as prefix_file:
        used_prefixes = prefix_file.read().splitlines()
except FileNotFoundError:
    used_prefixes = []

# Initialize a list to hold the transformed data
vpc_details = []

# Process each customer's details
for customer, info in data.items():
    details = []
    for detail in info['details']:
        prefix = generate_random_prefix(used_prefixes)
        details.append({
            'vpc_name': detail['vpc_name'],
            'host_ip': f"{prefix}.1",
            'host_ep_ip': f"{prefix}.1/30",
            'ns_ep_ip': f"{prefix}.2/30",
            'ip': f"{prefix}.0/30"
        })
        used_prefixes.append(prefix)
    vpc_details.append({'name': info['name'], 'vpcs': details})

# Write the YAML data to a file with proper indentation using ruamel.yaml
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
with open(yaml_file_path, 'w') as f:
    yaml.dump({'vpc_details': vpc_details}, f)
