# Mikrotik MCP Server (Python)

Model Context Protocol (MCP) server implementation for managing Mikrotik RouterOS (v6 & v7) via API.

## Tools Available
- `get_system_resources`: Monitor CPU load, uptime, and free memory.
- `get_hotspot_active_users`: View currently active hotspot users.
- `get_dhcp_leases`: View all DHCP server leases.

## Quick Start (NixOS)
1. `cd mikrotik-mcpserver`
2. `cp .env.example .env` (fill in your router credentials)
3. `nix develop`
4. `python server.py` (stdio) or `python server.py --sse` (for n8n at port 1997)

## Configuration for n8n
- **SSE URL**: `http://<YOUR_IP>:1997/mikrotik-mcpserver/sse`
