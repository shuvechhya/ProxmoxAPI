from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import urllib3
from urllib.parse import quote
import logging
from dotenv import load_dotenv
# import os

# load_dotenv()

logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to INFO for cleaner logs
logger = logging.getLogger(__name__)

app = FastAPI()

PROXMOX_HOST = "https://10.0.1.10:8006"
USERNAME = "shuvechhya@pve"
PASSWORD = "Nepal1234$#@!#"
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

class ResizeDiskRequest(BaseModel):
    node: str
    vmid: int
    disk: str
    size: str


# Helper function for authentication
def authenticate():
    
    auth_url = f"{PROXMOX_HOST}/api2/json/access/ticket"
    auth_data = {"username": USERNAME, "password": PASSWORD}
    
    try:
        auth_response = requests.post(auth_url, data=auth_data, verify=VERIFY_SSL)
        auth_response.raise_for_status()

        logger.debug("hello")

        auth_token = auth_response.json()["data"]
        cookies = {"PVEAuthCookie": auth_token["ticket"]}
        headers = {"CSRFPreventionToken": auth_token["CSRFPreventionToken"]}

           
        logger.debug(cookies)
        logger.debug(headers)

        return cookies, headers
   
    except requests.exceptions.RequestException as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed.")
    except KeyError:
        logger.error("Authentication response missing expected data")
        raise HTTPException(status_code=500, detail="Authentication response error.")
 


# Helper function to handle Proxmox API responses
def handle_response(response):
    if response.status_code != 200:
        try:
            response_data = response.json()
            error_message = response_data.get("errors", "Unexpected error")
        except ValueError:
            error_message = f"Unexpected response format: {response.text}"
        logger.error(f"API error: {error_message}")
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

    snapshot_url = f"{PROXMOX_HOST}/api2/json/nodes/{request.node}/qemu/{request.vmid}/snapshot"
    payload = {"snapname": request.snapname, "description": request.description}

    snapshot_response = requests.post(snapshot_url, headers=headers, cookies=cookies, json=payload, verify=VERIFY_SSL)
    snapshot_response_data = handle_response(snapshot_response)

    logger.info(f"Snapshot creation response: {snapshot_response_data}")
    return {"message": "Snapshot created successfully", "details": snapshot_response_data}


@app.put("/resize-disk/")
def api_resize_disk(request: ResizeDiskRequest):
    """Resize a disk on a Proxmox VM."""
    try:
        cookies, headers = authenticate()

        resize_url = f"{PROXMOX_HOST}/api2/json/nodes/{request.node}/qemu/{request.vmid}/resize"
        payload = {
            "disk": request.disk,
            "size": request.size,
        }

        logger.info(f"Sending resize request to {resize_url} with payload: {payload}")
        resize_response = requests.put(
            resize_url, headers=headers, cookies=cookies, json=payload, verify=VERIFY_SSL
        )

        resize_response_data = handle_response(resize_response)

        logger.info(f"Disk resized successfully: {resize_response_data}")
        return {"message": "Disk resized successfully", "details": resize_response_data}

    except requests.exceptions.RequestException as req_error:
        logger.error(f"Request error: {req_error}")
        raise HTTPException(status_code=500, detail=str(req_error))

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")