from flask import Flask, jsonify, request
import json
import yaml
import requests
import random

app = Flask(__name__)

# Static customer and VM details
CUSTOMER_NAME = "Enter your name"
CUSTOMER_ID = "Enter your ID"
VM_MEMORY = "4GB"
VM_VCPU = "2"

# Mapping of edge servers to their VPC IDs
edge_server_vpc_mapping = {
    'edge1': 'vpc-001',
    'edge2': 'vpc-002',
    'edge3': 'vpc-003',
}

def generate_random_ip():
    """Generate a random IP address within the 192.168.0.0/16 subnet."""
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

def create_and_upload_subnet_yaml(tenant_id, tenant_name, vpc_id, file_location, edge_server_responses):
    """Generates and uploads subnet YAML file."""
    """Generates and uploads VM YAML file."""
    data = {
        'customer_name': CUSTOMER_NAME,
        'customer_id': CUSTOMER_ID,
        'vpcs': []
    }

    for edge_server in edge_server_responses:
        data['vpcs'].append({
            'vpc_name': edge_server['vpc_id'],
            'subnet_details': [{
                'subnet_name': f"{tenant_name}_{edge_server['name']}",
                'subnet_ip': generate_random_ip(),
                'subent_mask': 24  
            }]
        })
    with open('data.yaml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)

    return upload_yaml('data.yaml', 'http://localhost:8000/uploadSubnetDetails')

def create_and_upload_vm_yaml(edge_server_responses, tenant_name, file_location):
    """Generates and uploads VM YAML file."""
    yaml_data = {
        'customer_name': CUSTOMER_NAME,
        'customer_id': CUSTOMER_ID,
        'vpcs': []
    }

    for edge_server in edge_server_responses:
        yaml_data['vpcs'].append({
            'vpc_name': edge_server['vpc_id'],
            'subnet_details': [{
                'subnet_name': f"{tenant_name}_{edge_server['name']}",
                'vm_details': [{'vm_name':f"{tenant_name}_{edge_server['name']}_vm", 'memory': VM_MEMORY, 'vcpu': VM_VCPU}],
                'source_file_location': file_location
            }]
        })

    with open('vm_details.yaml', 'w') as yaml_file:
        yaml.dump(yaml_data, yaml_file, default_flow_style=False)

    return upload_yaml('vm_details.yaml', 'http://localhost:8000/uploadVMtDetails')

def upload_yaml(yaml_file_path, url):
    print("I m here 3")
    """Uploads the specified YAML file to the provided URL."""
    with open(yaml_file_path, 'rb') as file:
        files = {'file': file}
        try:
            response = requests.post(url, files=files)
            response.raise_for_status()
            print(f"{yaml_file_path} successfully uploaded. Server response:")
            print(response.text)
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload {yaml_file_path}: {e}")
            return False

@app.route('/init_gathering', methods=['POST'])
def init_data_gathering():
    data = request.json
    tenant_id = data.get('tenant_id')
    tenant_name = data.get('tenant_name')
    vpc_id = data.get('vpc_id')
    file_location = data.get('file_location')

    edge_server_responses = []
    for edge_server, vpc in edge_server_vpc_mapping.items():
        include_server = data.get(f"include_{edge_server}")
        if include_server == 'yes':
            edge_server_responses.append({'name': edge_server, 'vpc_id': vpc})

    if tenant_id and tenant_name and vpc_id and file_location:
        if create_and_upload_subnet_yaml(tenant_id, tenant_name, vpc_id, file_location, edge_server_responses):
            create_and_upload_vm_yaml(edge_server_responses, tenant_name, file_location)
        return jsonify({"message": "Data gathering and processing completed successfully"})
    else:
        return jsonify({"error": "Missing parameters"}), 400
  


@app.route('/get-data', methods=['GET'])
def get_data():
    """Endpoint to return the collected data."""
    with open('data.json') as json_file:
        data = json.load(json_file)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
