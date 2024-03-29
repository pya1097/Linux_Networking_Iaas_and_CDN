from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import yaml
import json
import os
import random
import subprocess
from datetime import datetime

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/downloadTemplate/{template_name}")
async def download_file(template_name: str):
    
    file_path = "placeholder_template/"+template_name+".yaml"
    
    file_name = template_name+".yaml"

    return FileResponse(file_path, filename=file_name)

#------------------------------User Details-----------------------------------------------------------
def create_or_update_user_data(yaml_data, json_file):
    resp = {}
    try:
        with open(json_file, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}

    n = len(existing_data)
    
    for key,val in yaml_data.items():
        val['customer_id'] = n+1
        val['_Timestamp_'] = str(datetime.now())
        val['_Status_'] = "CREATED"
        n+=1
        resp[key] = val['customer_id']

    existing_data.update(yaml_data)

    with open(json_file, 'w') as file:
        json.dump(existing_data, file, indent=4)

    return resp

def transform_user_input(yaml_data):
    name = yaml_data['customer_name']

    new_dict = {
        name: yaml_data
    }

    return new_dict

@app.post("/uploadUserDetails/")
async def create_upload_file(file: UploadFile):

    if file.filename.endswith(".yaml"):
        contents = await file.read()
        try:
            yaml_data = yaml.safe_load(contents)
            yaml_data = transform_user_input(yaml_data)

            id = create_or_update_user_data(yaml_data, "../database/database.json")
            return {"message": "Your customer ID is: "+str(id)}
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {e}")
    else:
        raise HTTPException(status_code=400, detail="U  ploaded file must be in YAML format.")


#------------------------------VPC Details-----------------------------------------------------------

def generate_random_prefix():

    try:
        with open('../database/used_prefixes.txt', 'r') as prefix_file:
            used_prefixes = prefix_file.read().splitlines()
    except FileNotFoundError:
        used_prefixes = []

    prefix = ".".join([str(random.randint(0, 255)) for _ in range(3)])
    while prefix in used_prefixes:
        prefix = ".".join([str(random.randint(0, 255)) for _ in range(3)])

    used_prefixes.append(prefix)
    
    with open('../database/used_prefixes.txt', 'w') as prefix_file:
        prefix_file.write('\n'.join(used_prefixes))
    
    return prefix



def create_or_update_vpc(yaml_data, json_file):  

    with open(json_file, "r") as file:
        existing_data = json.load(file)

    if 'vpcs' in existing_data[yaml_data['customer_name']]:
        yaml_data, vpc_ids = add_vpc_ids(yaml_data, existing_data[yaml_data['customer_name']])
    else:
        yaml_data, vpc_ids = add_vpc_ids(yaml_data)
       

    existing_data[yaml_data['customer_name']]['vpcs'] = yaml_data['vpcs']
    with open(json_file, "w") as file:
        json.dump(existing_data, file, indent=4)

    return vpc_ids


def add_vpc_ids(yaml_data,existing_data=None):
    vpc_ids = {}
    if not existing_data:
        i=1
        for key, val in yaml_data['vpcs'].items():
            vpc_ids[key] = i
            val['vpc_id'] = i
            val['vpc_ip'] = generate_random_prefix()
            val['_Timestamp_'] = str(datetime.now())
            val['_Status_'] = "IN_PROGRESS"
            i+=1
    else:
        n = len(existing_data['vpcs'])
        i =1
        for key, val in yaml_data['vpcs'].items():
            val['vpc_id'] = n+i
            vpc_ids[val['vpc_name']] = n+i
            existing_data['vpcs'][key] = val
            val['vpc_ip'] = generate_random_prefix()
            val['_Timestamp_'] = str(datetime.now())
            val['_Status_'] = "IN_PROGRESS"
            i+=1
        yaml_data = existing_data
            
    return yaml_data, vpc_ids

def transform_vpc_input(yaml_data):
    vpcs_dict = {vpc['vpc_name']: vpc for vpc in yaml_data['vpcs']}

    yaml_data['vpcs'] = vpcs_dict

    return yaml_data

def update_vpc_status(val):
    val['_Status_'] = 'CREATED'
    val["_Timestamp_"] = str(datetime.now())
    return val


@app.post("/uploadVPCDetails/")
async def create_upload_vpc_file(file: UploadFile):

    if file.filename.endswith(".yaml"):
        contents = await file.read()
        # Updating database
        try:
            yaml_data = yaml.safe_load(contents)
            yaml_data = transform_vpc_input(yaml_data)

            id = create_or_update_vpc(yaml_data, "../database/database.json")
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {e}")
        
        
        with open("../database/database.json", "r") as file:
            orignal_data = json.load(file) 
        
        data = orignal_data[yaml_data["customer_name"]]

        for key, val in data["vpcs"].items():

        # # Executing vpc southbound
        # try:
        #     subprocess.run(['python', '../southbound/vpc.py','',''])
        #     print("Script executed successfully.")
        #     return {"message": "Your VPC ID is: "+str(id)}
        # except subprocess.CalledProcessError as e:
        #     print("Error occurred while executing the script:", e)
            if key in yaml_data['vpcs']:
                val = update_vpc_status(val)
        
        orignal_data[yaml_data['customer_name']] = data
        with open("../database/database.json", "w") as file:
            json.dump(orignal_data, file, indent=4)


    else:
        raise HTTPException(status_code=400, detail="Uploaded file must be in YAML format.")


#------------------------------Subnet Details-----------------------------------------------------------

def generate_random_port():

    try:
        with open('../database/used_ports.txt', 'r') as port_file:
            used_ports = port_file.read().splitlines()
    except FileNotFoundError:
        used_ports = []

    port = str(random.randint(1000, 9999))
    while port in used_ports:
        port = str(random.randint(1000, 9999))

    used_ports.append(port)
    
    with open('../database/used_ports.txt', 'w') as port_file:
        port_file.write('\n'.join(used_ports))
    
    return port

def transform_subnet_input(yaml_data):
    vpcs_dict = {}
    for vpc in yaml_data['vpcs']:
        vpc_name = vpc['vpc_name']
        vpcs_dict[vpc_name] = vpc

        subnets_dict = {}
        for subnet in vpc['subnet_details']:
            subnet_name = subnet['subnet_name']
            subnets_dict[subnet_name] = subnet
        
        vpcs_dict[vpc_name]['subnet_details'] = subnets_dict

    yaml_data['vpcs'] = vpcs_dict
    return yaml_data


def create_or_update_subnet(yaml_data, json_file):
    resp = {}
    with open(json_file, "r") as file:
        existing_data = json.load(file)

    for key, val in yaml_data['vpcs'].items():
        if 'subnet_details' in existing_data[yaml_data['customer_name']]['vpcs'][key]:
            yaml_data['vpcs'][key]['subnet_details'], subnet_ids = add_subnet_ids(yaml_data['vpcs'][key]['subnet_details'],key,existing_data[yaml_data['customer_name']]['vpcs'][key]['subnet_details'])
        else:
            yaml_data['vpcs'][key]['subnet_details'], subnet_ids = add_subnet_ids(yaml_data['vpcs'][key]['subnet_details'],key)
        resp.update(subnet_ids)

        existing_data[yaml_data['customer_name']]['vpcs'][key]['subnet_details'] = yaml_data['vpcs'][key]['subnet_details']
    
    with open(json_file, "w") as file:
        json.dump(existing_data, file, indent=4)

    
    return resp


def add_subnet_ids(yaml_data_vpc_data,vpc,existing_data=None):
    subnet_ids = {}
    
    if not existing_data:
        i=1
        for key, val in yaml_data_vpc_data.items():
            val['subnet_id'] = i
            val['incoming_dnat_routing_port'] = generate_random_port()
            val['_Timestamp_'] = str(datetime.now())
            val['_Status_'] = "IN_PROGRESS"
            subnet_ids[vpc+"_"+key] = i
            i+=1
    else:
        n = len(existing_data)
        i=1
        for key, val in yaml_data_vpc_data.items():
            val['subnet_id'] = n+i
            val['incoming_dnat_routing_port'] = generate_random_port()
            val['_Timestamp_'] = str(datetime.now())
            val['_Status_'] = "IN_PROGRESS"
            subnet_ids[vpc+"_"+key] = n+i
            existing_data[key] = val
            i+=1
        yaml_data_vpc_data = existing_data
    return yaml_data_vpc_data, subnet_ids


@app.post("/uploadSubnetDetails/")
async def create_upload_subnet_file(file: UploadFile):

    if file.filename.endswith(".yaml"):
        contents = await file.read()
        try:
            yaml_data = yaml.safe_load(contents)
            yaml_data = transform_subnet_input(yaml_data)

            id = create_or_update_subnet(yaml_data, "../database/database.json")

            with open("../database/database.json", "r") as file:
                orignal_data = json.load(file) 
        
            data = orignal_data[yaml_data["customer_name"]]

            for vpc, vpc_data in data['vpcs'].items():
                for subnet, subnet_data in vpc_data['subnet_details'].items():
                    if subnet in yaml_data['vpcs'][vpc]['subnet_details']:
                        subnet_data = update_vpc_status(subnet_data)
                        orignal_data[yaml_data["customer_name"]]['vpcs'][vpc]['subnet_details'][subnet] = subnet_data

                    ##Call SB Script for creating Subnet

            with open("../database/database.json", "w") as file:
                json.dump(orignal_data, file, indent=4)
            
            return {"message": "Your Subnet ID is: "+str(id)}
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {e}") 
        

    else:
        raise HTTPException(status_code=400, detail="Uploaded file must be in YAML format.")
    

#-----------------------------------------VM Addition details------------------------------------------------

def create_or_update_vm(yaml_data, json_file):
    resp = {}
    with open(json_file, "r") as file:
        existing_data = json.load(file)

    for vpc, vpc_val in yaml_data['vpcs'].items():
        for key, val in vpc_val['subnet_details'].items():
            
            if 'vm_details' in existing_data[yaml_data['customer_name']]['vpcs'][vpc]['subnet_details'][key]:
                yaml_data['vpcs'][vpc]['subnet_details'][key]['vm_details'], vm_ids = add_vm_ids(yaml_data['vpcs'][vpc]['subnet_details'][key]['vm_details'],vpc,key,existing_data[yaml_data['customer_name']]['vpcs'][vpc]['subnet_details'][key]['vm_details'])
            else:
                yaml_data['vpcs'][vpc]['subnet_details'][key]['vm_details'], vm_ids = add_vm_ids(yaml_data['vpcs'][vpc]['subnet_details'][key]['vm_details'],vpc,key)
            resp.update(vm_ids)

            existing_data[yaml_data['customer_name']]['vpcs'][vpc]['subnet_details'][key]['vm_details'] = yaml_data['vpcs'][vpc]['subnet_details'][key]['vm_details']
    
    with open(json_file, "w") as file:
        json.dump(existing_data, file, indent=4)

    
    return resp


def add_vm_ids(yaml_data_vpc_data,vpc,subnet,existing_data=None):
    vm_ids = {}
    vm_details = {}

    if not existing_data:
        for i, val in enumerate(yaml_data_vpc_data):
            vm_details[i+2] = val
            val['_Timestamp_'] = str(datetime.now())
            val['_Status_'] = "IN_PROGRESS"
            vm_ids[vpc+"_"+subnet+"_VM"+str(i+2)] = i+2
        yaml_data_vpc_data = vm_details
    else:
        n = len(existing_data)
        print('fine')
        for i, val in enumerate(yaml_data_vpc_data):
            vm_ids[vpc+"_"+subnet+"_VM"+str(i+2)] = n+i+2
            val['_Timestamp_'] = str(datetime.now())
            val['_Status_'] = "IN_PROGRESS"
            existing_data[n+i+2] = val

        yaml_data_vpc_data = existing_data

    return yaml_data_vpc_data, vm_ids


@app.post("/uploadVMDetails/")
async def create_upload_VMfile(file: UploadFile):

    if file.filename.endswith(".yaml"):
        contents = await file.read()
        try:
            yaml_data = yaml.safe_load(contents)
            yaml_data = transform_subnet_input(yaml_data)
            print(yaml_data)

            id = create_or_update_vm(yaml_data, "../database/database.json")
            
            with open("../database/database.json", "r") as file:
                orignal_data = json.load(file) 
        
            data = orignal_data[yaml_data["customer_name"]]

            for vpc, vpc_data in data['vpcs'].items():
                for subnet, subnet_data in vpc_data['subnet_details'].items():
                    for vm, vm_data in subnet_data['vm_details'].items():
                        if vm in yaml_data['vpcs'][vpc]['subent_details'][subnet]['vm_details']:
                            vm_data = update_vpc_status(vm_data)
                            orignal_data[yaml_data["customer_name"]]['vpcs'][vpc]['subnet_details'][subnet]['vm_details'][vm] = vm_data

                            ##Call SB Script for creating VM 

            with open("../database/database.json", "w") as file:
                json.dump(orignal_data, file, indent=4)

            return {"message": "Your Subnet ID is: "+str(id)}
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {e}")
    else:
        raise HTTPException(status_code=400, detail="Uploaded file must be in YAML format.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
