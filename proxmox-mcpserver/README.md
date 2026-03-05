# Proxmox Ultimate Management MCP Server

Model Context Protocol (MCP) server implementation for full life cycle management of Proxmox Virtual Environment (VE).

## Tools Available

### 📊 Monitoring & Network
- `get_proxmox_nodes_status`: Check health of physical nodes (CPU, RAM, Uptime).
- `get_proxmox_vm_status(node, vmid)`: Real-time status of a VM/LXC.
- `get_proxmox_storage_status(node)`: Check disk usage across storages.
- `get_proxmox_node_networks(node)`: List all network interfaces and IP addresses on a node.
- `check_proxmox_connectivity(target)`: **Ping Test** from the server to local/internet.

### 📦 System & Packages (Debian/Proxmox)
- `update_proxmox_repositories(node)`: Trigger **APT Update** to refresh package lists.
- `list_proxmox_packages(node)`: List available updates and current package status.

### ⚙️ Life Cycle Management
- `list_proxmox_vms(node)`: List all VMs and LXCs.
- `manage_proxmox_power(node, vmid, action)`: **Start, Stop, Reboot, Shutdown**, etc.
- `create_proxmox_container(node, vmid, ostemplate, password)`: **Create a New LXC** container.
- `clone_proxmox_vm(node, vmid, template_vmid)`: **Clone a New VM** from a template.
- `delete_proxmox_vm(node, vmid)`: **Permanently Delete** a VM or LXC (must be stopped).

### 🛠️ Configuration & Options
- `set_proxmox_vm_config(node, vmid, cores, memory)`: Update VM CPU and RAM on the fly.
- `set_proxmox_container_config(node, vmid, cores, memory)`: Update LXC CPU and RAM.
- `create_proxmox_snapshot(node, vmid, snapname)`: Take snapshots for safe updates.
- `list_proxmox_snapshots(node, vmid)`: View available snapshots for a VM.

## Quick Start (NixOS)
1. `cd proxmox-mcpserver`
2. `cp .env.example .env` (fill in your proxmox host, user, and password)
3. `nix develop`
4. `python server.py --sse` (runs on port 1998)

## Configuration for n8n
- **SSE URL**: `http://<YOUR_IP>:1998/proxmox-mcpserver/sse`
