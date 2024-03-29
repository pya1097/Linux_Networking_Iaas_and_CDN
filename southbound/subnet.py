import json
from ruamel.yaml import YAML
import random
import os
import yaml
import sys


input_client_id = sys.argv[1]
input_vpc_id = sys.argv[2]
input_subnet_id = sys.argv[3]
print(input_client_id, input_vpc_id, input_subnet_id)

current_directory = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(current_directory, '..', 'automation', 'variables', 'create_subnet_variables_test.yml')
json_file_path = os.path.join(current_directory, '..', 'database', 'database.json')

data = None
with open(json_file_path, 'r') as file:
    data = json.load(file)

for client, client_data in data.items():
    customer_id = client_data["customer_id"]
    if str(customer_id) == str(input_client_id):
        vpcs = client_data["vpcs"]
        for vpc_name, vpc_details in vpcs.items():
            vpc_id = vpc_details["vpc_id"]
            if str(vpc_id) == str(input_vpc_id):
                subnet_details = vpc_details["subnet_details"]
                vpc_yaml_data = {}
                for subnet_name, subnet_info in subnet_details.items():
                    subnet_id = subnet_info["subnet_id"]
                    if str(subnet_id) == str(input_subnet_id):
                        subnet_ip = subnet_info["subnet_ip"]
                        subnet_mask = str(subnet_info["subnet_mask"])
                        v_id = f'c{customer_id}v{vpc_id}'
                        sn_id = f'{v_id}s{subnet_id}'
                        br_id = f'b{sn_id}'
                        veth_brv_br_inf = f've_{sn_id}_b'
                        veth_brv_v_inf = f've_{sn_id}_v'
                        veth_vpns_v_inf = f've_{v_id}_v'
                        network_id = f'n{sn_id}'
                        veth_brv_v_inf_ip = '.'.join(subnet_ip.split('.')[:-1]) + '.1/' + subnet_mask
                        subnet_ip = subnet_ip + '/' + subnet_mask
                        vm_id = f'vm1{sn_id}'
                        subnet_yaml_data = {
                            "pub_namespace": 'public',
                            "vpc_id": v_id,
                            "br_id": br_id,
                            "veth_brv_br_inf": veth_brv_br_inf,
                            "veth_brv_v_inf": veth_brv_v_inf,
                            "veth_vpns_v_inf": veth_vpns_v_inf,
                            "network_id": network_id,
                            "veth_brv_v_inf_ip": veth_brv_v_inf_ip,
                            "subnet_ip": subnet_ip,
                            "template_dir": "/home/vmadm/project/automation/jinja_templates",
                            "script_files_dir": "/home/vmadm/project/subnet_files"
                        }
os.makedirs(os.path.dirname(yaml_file_path), exist_ok=True)
with open(yaml_file_path, 'w') as yaml_file:
    yaml.dump(subnet_yaml_data, yaml_file)

