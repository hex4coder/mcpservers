# Proxmox Management MCP Server

Model Context Protocol (MCP) server implementation for managing Proxmox Virtual Environment (VE).

## Tools Available
- `get_nodes_status`: Check CPU/RAM/Uptime of Proxmox physical nodes.
- `list_all_vms(node)`: List all VMs and LXCs on a node.
- `get_vm_status(node, vmid)`: Detailed status of a VM/LXC.
- `manage_vm_power(node, vmid, action)`: Start, stop, reboot, etc.
- `create_vm_snapshot(node, vmid, snapname)`: Take snapshots before updates.
- `list_vm_snapshots(node, vmid)`: List existing snapshots.
- `get_storage_status(node)`: Check disk usage.

## Quick Start (NixOS)
1. `cd proxmox-mcpserver`
2. `cp .env.example .env` (fill in your proxmox host, user, and password)
3. `nix develop`
4. `python server.py --sse` (runs on port 1998)

## Configuration for n8n
- **SSE URL**: `http://<YOUR_IP>:1998/proxmox-mcpserver/sse`
