# GEMINI.md - Instructional Context

This document provides essential information and instructions for interacting with the **MCP Servers Suite** project.

## Project Overview

*   **Purpose:** A comprehensive suite of Model Context Protocol (MCP) servers designed for n8n AI Agent integration to manage school infrastructure.
*   **Target Platform:** NixOS (Nix Flakes) and Debian/Ubuntu systems.
*   **Core Tech:** Python 3, FastMCP SDK, Uvicorn, Starlette, Pandoc, Mikrotik API, Proxmoxer.

## Architecture & Server Details

### 1. Markdown to Word & PDF
*   **Path:** `md-to-word-mcpserver/`
*   **Port:** `1996` (SSE) | **Base Path:** `/md-to-word-mcpserver`
*   **Features:** Converts Markdown to DOCX/PDF and provides direct download links.
*   **Key Tools:**
    *   `convert_markdown_to_docx`, `convert_markdown_to_pdf`
    *   `convert_md_file_to_docx`, `convert_md_file_to_pdf`

### 2. Mikrotik Management
*   **Path:** `mikrotik-mcpserver/`
*   **Port:** `1997` (SSE) | **Base Path:** `/mikrotik-mcpserver`
*   **Features:** Full network monitoring, Hotspot (bandwidth/users), DHCP, and logs.
*   **Key Tools (Unique Prefixes):**
    *   `get_mikrotik_resources`, `get_mikrotik_storage`, `get_mikrotik_logs`
    *   `get_mikrotik_interfaces`, `get_mikrotik_ip_addresses`, `get_mikrotik_routes`
    *   `get_mikrotik_dns_settings`, `get_mikrotik_arp_table`, `get_mikrotik_dhcp_leases`
    *   `get_hotspot_servers`, `add_hotspot_user_profile`, `set_user_profile`, etc.

### 3. Proxmox Management
*   **Path:** `proxmox-mcpserver/`
*   **Port:** `1998` (SSE) | **Base Path:** `/proxmox-mcpserver`
*   **Features:** VM/LXC Lifecycle (Create, Power, Config, Delete), Snapshots, and Node resources.
*   **Key Tools (Unique Prefixes):**
    *   `get_proxmox_nodes_status`, `get_proxmox_storage_status`
    *   `list_proxmox_vms`, `get_proxmox_vm_status`
    *   `manage_proxmox_power`, `delete_proxmox_vm`
    *   `create_proxmox_container`, `clone_proxmox_vm`
    *   `set_proxmox_vm_config`, `set_proxmox_container_config`
    *   `create_proxmox_snapshot`, `list_proxmox_snapshots`

## Implementation Details (SSE Transport)

All servers use a standardized SSE implementation via **Uvicorn** and **Starlette**:
- **Connection URL:** `http://<IP>:<PORT>/<server-path>/sse`
- **Message URL:** `http://<IP>:<PORT>/<server-path>/messages`

## Building and Running

### Development Environment (NixOS)
```bash
cd <server-directory>
nix develop
```

### Running for n8n (SSE Mode)
```bash
# Set SERVER_IP for Markdown download links
export SERVER_IP=192.168.x.x 
python server.py --sse
```

## Deployment / Claude Desktop Integration (NixOS)

```json
{
  "mcpServers": {
    "md-converter": {
      "command": "nix",
      "args": ["develop", "/path/to/md-to-word-mcpserver", "--command", "python", "server.py"]
    },
    "mikrotik-mgmt": {
      "command": "nix",
      "args": ["develop", "/path/to/mikrotik-mcpserver", "--command", "python", "server.py"]
    },
    "proxmox-mgmt": {
      "command": "nix",
      "args": ["develop", "/path/to/proxmox-mcpserver", "--command", "python", "server.py"]
    }
  }
}
```
