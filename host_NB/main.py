from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import yaml
import json
import os


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
    print(yaml_data)
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            existing_data = json.load(file)
        n = len(existing_data)
        yaml_data['customer_id'] = n+1
        existing_data[yaml_data['name']] = yaml_data
        with open(json_file, "w") as file:
            json.dump(existing_data, file, indent=4)
    else:
        with open(json_file, "w") as file:
            data = {}
            yaml_data['customer_id'] = 1
            data[yaml_data['name']] = yaml_data
            json.dump(data, file, indent=4)
    return yaml_data['customer_id']

@app.post("/uploadUserDetails/")
async def create_upload_file(file: UploadFile):

    if file.filename.endswith(".yaml"):
        contents = await file.read()
        try:
            yaml_data = yaml.safe_load(contents)
            id = create_or_update_user_data(yaml_data, "../database/user_data.json")
            return {"message": "Your customer ID is: "+str(id)}
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {e}")
    else:
        raise HTTPException(status_code=400, detail="U  ploaded file must be in YAML format.")

@app.get("/getUserDetails/{customer_name}")
async def get_customer(customer_name: str):
    with open("../database/user_data.json", "r") as file:
        data = json.load(file)
        return data[customer_name]

#------------------------------VPC Details-----------------------------------------------------------
def create_or_update_vpc(yaml_data, json_file):
    
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            existing_data = json.load(file)
        if yaml_data['name'] in existing_data:
            yaml_data, vpc_ids = add_vpc_ids(yaml_data, existing_data[yaml_data['name']])
        else:
            yaml_data, vpc_ids = add_vpc_ids(yaml_data)

        existing_data[yaml_data['name']] = yaml_data
        with open(json_file, "w") as file:
            json.dump(existing_data, file, indent=4)
    else:
        with open(json_file, "w") as file:
            data = {}
            yaml_data, vpc_ids = add_vpc_ids(yaml_data)
            data[yaml_data['name']] = yaml_data
            json.dump(data, file, indent=4)
    return vpc_ids


def add_vpc_ids(yaml_data,existing_data=None):
    vpc_ids = {}
    if not existing_data:
        for i, val in enumerate(yaml_data['details']):
            val['vpc_id'] = i+1
            vpc_ids[val['vpc_name']] = i+1
    else:
        n = len(existing_data['details'])
        for i, val in enumerate(yaml_data['details']):
            val['vpc_id'] = n+i+1
            vpc_ids[val['vpc_name']] = n+i+1
            existing_data['details'].append(val)
            yaml_data = existing_data
    return yaml_data, vpc_ids

@app.post("/uploadVPCDetails/")
async def create_upload_vpc_file(file: UploadFile):

    if file.filename.endswith(".yaml"):
        contents = await file.read()
        try:
            yaml_data = yaml.safe_load(contents)
            id = create_or_update_vpc(yaml_data, "../database/vpc_data.json")
            return {"message": "Your VPC ID is: "+str(id)}
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {e}")
    else:
        raise HTTPException(status_code=400, detail="Uploaded file must be in YAML format.")
    
@app.get("/getVPCDetails/{customer_name}")
async def get_vpc(customer_name: str):
    with open("../database/vpc_data.json", "r") as file:
        data = json.load(file)
        return data[customer_name]

#------------------------------Subnet Details-----------------------------------------------------------

def create_or_update_subnet(yaml_data, json_file):
    
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            existing_data = json.load(file)
        if yaml_data['name'] in existing_data:
            yaml_data, subnet_ids = add_subnet_ids(yaml_data, existing_data[yaml_data['name']])
        else:
            yaml_data, subnet_ids = add_subnet_ids(yaml_data)

        existing_data[yaml_data['name']] = yaml_data
        with open(json_file, "w") as file:
            json.dump(existing_data, file, indent=4)
    else:
        with open(json_file, "w") as file:
            data = {}
            yaml_data, subnet_ids = add_subnet_ids(yaml_data)
            data[yaml_data['name']] = yaml_data
            json.dump(data, file, indent=4)
    
    return subnet_ids


def add_subnet_ids(yaml_data,existing_data=None):
    subnet_ids = {}
    
    if not existing_data:
        for i, vpc in enumerate(yaml_data['details']):
            for j, sub in enumerate(vpc['subnet_details']):
                sub['subnet_id'] = j+1
                subnet_ids[vpc['vpc_name']+" : "+sub['subnet_name']] = i+1
    else:
        for i, vpc1 in enumerate(yaml_data['details']):
            exists_vpc = {}
            index = 0
            for j, vpc2 in enumerate(existing_data['details']):
                if(vpc1['vpc_name']==vpc2['vpc_name']):
                    exists_vpc = vpc2
                    index = j
            
            if len(exists_vpc)==0:
                for j, sub in enumerate(vpc1['subnet_details']):
                    sub['subnet_id'] = j+1
                    subnet_ids[vpc1['vpc_name']+" : "+sub['subnet_name']] = j+1
                existing_data['details'].append(vpc1)
            else: 
                n = len(exists_vpc['subnet_details'])
                for j, sub in enumerate(vpc1['subnet_details']):
                    sub['subnet_id'] = n+j+1
                    subnet_ids[vpc1['vpc_name']+" : "+sub['subnet_name']] = n+j+1
                    exists_vpc['subnet_details'].append(sub)
                
                existing_data['details'][index] = exists_vpc
            yaml_data = existing_data
    return yaml_data, subnet_ids

@app.post("/uploadSubnetDetails/")
async def create_upload_subnet_file(file: UploadFile):

    if file.filename.endswith(".yaml"):
        contents = await file.read()
        try:
            yaml_data = yaml.safe_load(contents)
            id = create_or_update_subnet(yaml_data, "../database/subnet_data.json")
            return {"message": "Your Subnet ID is: "+str(id)}
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML format: {e}")
    else:
        raise HTTPException(status_code=400, detail="Uploaded file must be in YAML format.")
    
@app.get("/getSubnetDetails/{customer_name}")
async def get_subnet(customer_name: str):
    with open("../database/subnet_data.json", "r") as file:
        data = json.load(file)
        return data[customer_name]



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
