# Proxmox API Integration with FastAPI

This project provides an interface to interact with Proxmox's API using **FastAPI**. It includes endpoints for managing virtual machines (VMs), updating VM configurations, controlling VM states (start/stop), and creating snapshots of VMs. The API authenticates with Proxmox and performs these actions via HTTP requests.

## Features

- **VM Configuration Update**: Allows updating the configuration of a VM, including SSH keys and IP configuration.
- **Control VM (Start/Stop)**: Provides endpoints to start or stop VMs on a specified Proxmox node.
- **Create Snapshot**: Allows creating a snapshot of a specified VM.

## Prerequisites

- **Proxmox VE**: A running Proxmox Virtual Environment instance.
- **Python 3.7+**: Required to run the FastAPI application.
- **Dependencies**: You will need the following Python packages installed:
  
  - `fastapi`
  - `pydantic`
  - `requests`
  - `python-dotenv`
  - `uvicorn`

You can install these dependencies by running:

```bash
pip install -r requirements.txt
```

## Setup
1.Clone the repository:

```bash
git clone https://github.com/your-username/proxmox-fastapi.git
cd proxmox-fastapi
```

2.Create a .env file in the root directory with the following variables:

```bash
PROXMOX_HOST=https://your-proxmox-server-ip:8006
USERNAME=your-proxmox-username
PASSWORD=your-proxmox-password
```

3.Run the FastAPI server:

```bash
uvicorn main:app --reload
```

This will start the server at http://127.0.0.1:8000.

## Endpoints
1. Update VM Configuration
POST /update-config

This endpoint updates the configuration of a VM, such as setting the SSH keys and other configurations.

Request Body Example:
```bash
{
  "ciuser": "admin",
  "cipassword": "password123",
  "node_name": "node1",
  "vm_id": 101,
  "sshkeys": "ssh-rsa AAAAB3... user@host"
}
```

Response:
```bash
{
  "message": "VM configuration updated successfully."
}
```

2. Control VM (Start/Stop)
POST /control-vm

This endpoint allows you to start or stop a VM.

Request Body Example:
```bash
{
  "node_name": "node1",
  "vmid": 101,
  "action": "start"
}
```

Response:
```bash
{
  "message": "VM 101 started successfully."
}
```

3. Create Snapshot
POST /create-snapshot/

This endpoint creates a snapshot of a VM.

Request Body Example:
```bash
{
  "node": "node1",
  "vmid": 101,
  "snapname": "snapshot1",
  "description": "Initial snapshot"
}
```

Response:
```bash
{
  "message": "Snapshot created successfully",
  "details": {...}
}
```

## Code Explanation
### Authentication
The authentication function authenticate() sends a POST request to Proxmox's /access/ticket endpoint with the username and password. If successful, it returns the authentication cookies and headers, which are used for subsequent API requests.

### Helper Function for Handling Responses
The handle_response() function checks the status of the response from Proxmox. If the status code is not 200 OK, it raises an HTTPException with the relevant error message.

### Pydantic Models
CloneVMRequest: Defines the structure for cloning a VM (not used directly in the endpoints but can be extended for further functionality).
ConfigData: Used to validate data for updating VM configurations.
ControlVMRequest: Used to define the request body for starting or stopping a VM.
SnapshotRequest: Defines the structure of the request body for creating a snapshot.
Endpoints
/update-config: This endpoint updates a VM's configuration on Proxmox. It uses the Proxmox /qemu/{vmid}/config endpoint.
/control-vm: Starts or stops a VM by calling the /status/{action} endpoint for a specified VM.
/create-snapshot/: Creates a snapshot of a VM via Proxmox's /snapshot API endpoint.

### Error Handling
If any of the API calls fail (e.g., due to authentication failure or invalid data), the handle_response() function raises an appropriate HTTPException with the error message.

### Logging
The logging module is used to log important actions and errors throughout the application.
