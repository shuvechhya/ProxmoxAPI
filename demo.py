<<<<<<< HEAD
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import urllib3
from urllib.parse import quote


app = FastAPI()

PROXMOX_HOST = "https://10.0.1.10:8006/api2/json"
USERNAME = "shuvechhya@pve"
PASSWORD = "Nepal1234$#@!#"
VERIFY_SSL = False

if not VERIFY_SSL:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CloneVMRequest(BaseModel):
    node_name: str
    template_vmid: int
    new_vmid: int
    name: str
    storage: str

class ConfigData(BaseModel):
    ciuser: str
    cipassword: str
    node_name: str
    vm_id: int
    sshkeys:str

class ControlVMRequest(BaseModel):
    node_name: str
    vmid: int
    action: str

def authenticate():
    auth_url = "https://10.0.1.10:8006/api2/json/access/ticket"
    auth_data = {"username": USERNAME, "password": PASSWORD}
    
    try:
        auth_response = requests.post(auth_url, data=auth_data, verify=VERIFY_SSL)
        auth_response.raise_for_status()
        
        auth_token = auth_response.json()["data"]
        csrf_token = auth_token["CSRFPreventionToken"]
        ticket = auth_token["ticket"]
        
        # Return the CSRF token and cookies for further requests
        cookies = {"PVEAuthCookie": ticket}
        headers = {"CSRFPreventionToken": csrf_token}
        
        return cookies, headers
    
    except requests.exceptions.RequestException as e:
        print("Authentication failed:", e)
        return None, None

## VM configuration endpoint
@app.post("/update-config")
async def update_config(data: ConfigData):
    try:
        cookies, headers = authenticate()
        if not cookies or not headers:
            raise HTTPException(status_code=500, detail="Authentication failed")

        config_url = f"{PROXMOX_HOST}/nodes/{data.node_name}/qemu/{data.vm_id}/config"
        
        
    
        config_data = {
            "ciuser": data.ciuser,
            "cipassword": data.cipassword,
            "ipconfig0": "ip=dhcp",
            "sshkeys": data.sshkeys 
        }

        print(f"Configuration data payload: {config_data}")

        # Make the POST request to update the configuration
        config_response = requests.post(
            config_url,
            headers=headers,
            cookies=cookies,
            json=config_data,
            verify=VERIFY_SSL,
        )

        print(f"Response status code: {config_response.status_code}")
        print(f"Response text: {config_response.text}")

        # Handle errors in the response
        if config_response.status_code != 200:
            try:
                response_data = config_response.json()  # Attempt to parse JSON response
                print(f"Parsed JSON response: {response_data}")
                error_message = response_data.get("errors", "Failed to update configuration")
            except ValueError:
                print("Response is not a valid JSON")
                error_message = f"Unexpected response format: {config_response.text}"
            raise HTTPException(status_code=config_response.status_code, detail=error_message)

        print(f"Configuration update response JSON: {config_response.json()}")
        return {"message": "VM configuration updated successfully."}

    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        print(f"Unexpected exception: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# VM power control helper function
@app.post("/control-vm")
async def control_vm(data: ControlVMRequest):
    try:
        # Authenticate with the Proxmox API
        cookies, headers = authenticate()
        if not cookies or not headers:
            raise HTTPException(status_code=500, detail="Authentication failed")

        # Validate action
        if data.action not in ["start", "stop"]:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'start' or 'stop'.")

        # Construct the URL for the action
        action_url = f"{PROXMOX_HOST}/nodes/{data.node_name}/qemu/{data.vmid}/status/{data.action}"

        print(f"Performing action '{data.action}' on VM {data.vmid} at URL: {action_url}")

        # Make the POST request to perform the action
        action_response = requests.post(
            action_url,
            headers=headers,
            cookies=cookies,
            verify=VERIFY_SSL,
        )
# Log the response details
        print(f"Proxmox API response status code: {action_response.status_code}")
        print(f"Proxmox API response content: {action_response.text}")

        # Handle errors in the response
        if action_response.status_code != 200:
            try:
                response_data = action_response.json()  # Attempt to parse JSON response
                print(f"Parsed JSON response: {response_data}")
                error_message = response_data.get("errors", f"Failed to {data.action} VM {data.vmid}")
            except ValueError:
                print("Response is not a valid JSON")
                error_message = f"Unexpected response format: {action_response.text}"
            raise HTTPException(status_code=action_response.status_code, detail=error_message)

        print(f"Action response JSON: {action_response.json()}")
        return {"message": f"VM {data.vmid} {data.action}ed successfully."}

    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        print(f"Unexpected exception: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



=======
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import urllib3
from urllib.parse import quote
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

PROXMOX_HOST = os.getenv('PROXMOX_HOST')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
VERIFY_SSL = False

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Pydantic models for request validation
class CloneVMRequest(BaseModel):
    node_name: str
    template_vmid: int
    new_vmid: int
    name: str
    storage: str

class ConfigData(BaseModel):
    ciuser: str
    cipassword: str
    node_name: str
    vm_id: int
    sshkeys: str

class ControlVMRequest(BaseModel):
    node_name: str
    vmid: int
    action: str

class SnapshotRequest(BaseModel):
    node: str
    vmid: int
    snapname: str
    description: str = ""

# Helper function for authentication
def authenticate():
    auth_url = f"{PROXMOX_HOST}/access/ticket"
    auth_data = {"username": USERNAME, "password": PASSWORD}
    
    try:
        auth_response = requests.post(auth_url, data=auth_data, verify=VERIFY_SSL)
        auth_response.raise_for_status()

        auth_token = auth_response.json()["data"]
        cookies = {"PVEAuthCookie": auth_token["ticket"]}
        headers = {"CSRFPreventionToken": auth_token["CSRFPreventionToken"]}

        return cookies, headers
    except requests.exceptions.RequestException as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed.")

# Helper function to handle Proxmox API responses
def handle_response(response):
    if response.status_code != 200:
        try:
            response_data = response.json()
            error_message = response_data.get("errors", "Unexpected error")
        except ValueError:
            error_message = f"Unexpected response format: {response.text}"
        raise HTTPException(status_code=response.status_code, detail=error_message)
    return response.json()

# Endpoint to update VM configuration
@app.post("/update-config")
async def update_config(data: ConfigData):
    cookies, headers = authenticate()
    config_url = f"{PROXMOX_HOST}/nodes/{data.node_name}/qemu/{data.vm_id}/config"
    
    encoded_sshkeys = quote(data.sshkeys)  

    config_data = {
        "ciuser": data.ciuser,
        "cipassword": data.cipassword,
        "sshkeys": encoded_sshkeys,
        "ipconfig0": "ip=dhcp",
    }

    config_response = requests.post(config_url, headers=headers, cookies=cookies, json=config_data, verify=VERIFY_SSL)
    config_response_data = handle_response(config_response)

    logger.info(f"Configuration update response: {config_response_data}")
    return {"message": "VM configuration updated successfully."}

# Endpoint to control VM (start/stop)
@app.post("/control-vm")
async def control_vm(data: ControlVMRequest):
    cookies, headers = authenticate()
    
    if data.action not in ["start", "stop"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'start' or 'stop'.")

    action_url = f"{PROXMOX_HOST}/nodes/{data.node_name}/qemu/{data.vmid}/status/{data.action}"
    action_response = requests.post(action_url, headers=headers, cookies=cookies, verify=VERIFY_SSL)
    
    action_response_data = handle_response(action_response)

    logger.info(f"Action response: {action_response_data}")
    return {"message": f"VM {data.vmid} {data.action}ed successfully."}

# Endpoint to create a snapshot
@app.post("/create-snapshot/")
def create_snapshot(request: SnapshotRequest):
    cookies, headers = authenticate()

    snapshot_url = f"{PROXMOX_HOST}/nodes/{request.node}/qemu/{request.vmid}/snapshot"
    payload = {"snapname": request.snapname, "description": request.description}

    snapshot_response = requests.post(snapshot_url, headers=headers, cookies=cookies, json=payload, verify=VERIFY_SSL)
    snapshot_response_data = handle_response(snapshot_response)

    logger.info(f"Snapshot creation response: {snapshot_response_data}")
    return {"message": "Snapshot created successfully", "details": snapshot_response_data}
>>>>>>> 641590d (added optimized api code)
