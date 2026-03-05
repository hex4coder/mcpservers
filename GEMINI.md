# GEMINI.md - Instructional Context

This document provides essential information and instructions for interacting with the **MCP Servers Suite** project.

## Project Overview

*   **Purpose:** A suite of Model Context Protocol (MCP) servers to extend AI agent capabilities:
    1.  **Markdown to Word & PDF**: Document conversion tools.
    2.  **Mikrotik Management**: Network monitoring and management via RouterOS API.
    3.  **Proxmox Management**: Virtualization environment management (Nodes, VMs, Snapshots).
*   **Target Platform:** NixOS (Nix Flakes) and Debian/Ubuntu systems.
*   **Key Technologies:**
    *   **Python 3**: Core implementation language.
    *   **FastMCP**: SDK for building MCP servers.
    *   **Pandoc & TeX Live**: Document conversion (DOCX/PDF).
    *   **routeros-api**: Library for Mikrotik integration.
    *   **proxmoxer**: Library for Proxmox integration.
    *   **uv**: Package and environment management.

## Architecture

### 1. Markdown to Word & PDF
Located in `md-to-word-mcpserver/`:
- `server.py`: Conversion tools (`convert_markdown_to_pdf`, etc.).
- Port: `1996` (SSE Mode).

### 2. Mikrotik Management
Located in `mikrotik-mcpserver/`:
- `server.py`: Network tools (`get_hotspot_active_users`, `get_dhcp_leases`, etc.).
- Port: `1997` (SSE Mode).

### 3. Proxmox Management
Located in `proxmox-mcpserver/`:
- `server.py`: Virtualization tools (`get_nodes_status`, `manage_vm_power`, etc.).
- Port: `1998` (SSE Mode).

## Building and Running

### Development Environment (NixOS)
To enter the development shell for a specific server:
```bash
cd <server-directory>
nix develop
```

### Running for n8n (SSE)
```bash
# Markdown Server (Port 1996)
cd md-to-word-mcpserver && nix develop --command python server.py --sse

# Mikrotik Server (Port 1997)
cd mikrotik-mcpserver && nix develop --command python server.py --sse

# Proxmox Server (Port 1998)
cd proxmox-mcpserver && nix develop --command python server.py --sse
```

## Deployment / Claude Desktop Integration

```json
{
  "mcpServers": {
    "md-to-doc-pdf": {
      "command": "nix",
      "args": ["develop", "/path/to/md-to-word-mcpserver", "--command", "python", "/path/to/md-to-word-mcpserver/server.py"]
    },
    "mikrotik-mgmt": {
      "command": "nix",
      "args": ["develop", "/path/to/mikrotik-mcpserver", "--command", "python", "/path/to/mikrotik-mcpserver/server.py"]
    },
    "proxmox-mgmt": {
      "command": "nix",
      "args": ["develop", "/path/to/proxmox-mcpserver", "--command", "python", "/path/to/proxmox-mcpserver/server.py"]
    }
  }
}
```
