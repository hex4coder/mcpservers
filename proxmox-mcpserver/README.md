# Proxmox Ultimate Management MCP Server

Model Context Protocol (MCP) server implementation for full life cycle management of Proxmox Virtual Environment (VE).

## Tools Available

### ⚙️ Life Cycle Management
- `list_all_vms(node)`: List all VMs and LXCs.
- `manage_vm_power(node, vmid, action)`: **Start, Stop, Reboot, Shutdown**, etc.
- `create_container(node, vmid, ostemplate, password)`: **Create a New LXC** container.
- `create_vm_from_template(node, vmid, template_vmid)`: **Clone a New VM** from a template.
- `delete_vm_or_container(node, vmid)`: **Permanently Delete** a VM or LXC (must be stopped).

### 🛠️ Configuration & Options
- `set_vm_config(node, vmid, cores, memory)`: Update VM CPU and RAM on the fly.
- `set_container_config(node, vmid, cores, memory)`: Update LXC CPU and RAM.
- `create_vm_snapshot(node, vmid, snapname)`: Take snapshots for safe updates.

### 📊 Monitoring
- `get_nodes_status`: Check health of physical nodes.
- `get_vm_status(node, vmid)`: Real-time CPU/RAM usage of a VM/LXC.
- `get_storage_status(node)`: Check disk usage across all storages.

## Quick Start (NixOS)
1. `cd proxmox-mcpserver`
2. `cp .env.example .env` (fill in your proxmox host, user, and password)
3. `nix develop`
4. `python server.py --sse` (runs on port 1998)

## Configuration for n8n
- **SSE URL**: `http://<YOUR_IP>:1998/proxmox-mcpserver/sse`
