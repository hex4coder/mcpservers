# Mikrotik Pro Management MCP Server

Model Context Protocol (MCP) server implementation for deep management of Mikrotik RouterOS (v6 & v7).

## Tools Available

### 🛠️ System
- `get_system_resources`: Board info, CPU load, uptime, and memory.
- `get_system_logs`: Get recent system logs (customizable lines).

### 🌐 Network & Routing
- `get_interfaces`: Status, type, and traffic (Rx/Tx) for all interfaces.
- `get_ip_addresses`: All assigned IP addresses and their interfaces.
- `get_routes`: View the routing table and active gateways.
- `get_dns_settings`: Check current DNS configuration.
- `get_arp_table`: IP to MAC address mappings.

### 📶 Hotspot Management
- `get_hotspot_active_summary`: Summary of all currently active sessions.
- `get_hotspot_users`: List all registered hotspot users.
- `add_hotspot_user`: Create a new user (with profile, password, and comment).
- `remove_hotspot_user`: Delete a hotspot user.

### 🔌 DHCP
- `get_dhcp_leases_detailed`: Full list of DHCP leases including hostnames and MACs.

## Quick Start (NixOS)
1. `cd mikrotik-mcpserver`
2. `cp .env.example .env` (fill in your router credentials)
3. `nix develop`
4. `python server.py --sse` (runs on port 1997)

## Configuration for n8n
- **SSE URL**: `http://<YOUR_IP>:1997/mikrotik-mcpserver/sse`
