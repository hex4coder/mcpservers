# Mikrotik Pro Management MCP Server

Model Context Protocol (MCP) server implementation for deep management of Mikrotik RouterOS (v6 & v7).

## Tools Available

### 📶 Hotspot & Bandwidth Management
- `get_hotspot_servers`: List all hotspot instances.
- `get_hotspot_server_profiles`: View server profiles (HTML login page info).
- `set_hotspot_html_directory`: **Change the Login Page** folder for a server profile.
- `get_hotspot_user_profiles`: View user profiles and their **Bandwidth Limits** (rate-limit).
- `add_hotspot_user_profile`: Create/Update user profiles with speed limits (e.g., '512k/1M').
- `set_user_profile`: **Assign/Move a User** to a specific profile/bandwidth tier.
- `add_hotspot_user`: Create new hotspot users.
- `get_hotspot_active_summary`: Monitor current active sessions.

### 🌐 Network & Routing
- `get_mikrotik_interfaces`: Status, type, and traffic (Rx/Tx) for all interfaces.
- `get_mikrotik_ip_addresses`: List all IP addresses assigned to interfaces.
- `get_mikrotik_dhcp_leases`: View connected devices with hostnames and MACs.
- `get_mikrotik_routes`: View routing table and gateways.
- `get_mikrotik_dns_settings`: View DNS configuration.
- `get_mikrotik_arp_table`: View IP to MAC mapping.
- `ping_mikrotik`: **Ping Test** from the router to any target (IP/Domain).

### 🛠️ System
- `get_mikrotik_resources`: Board info, CPU load, uptime, and memory.
- `get_mikrotik_storage`: Check internal disk usage.
- `get_mikrotik_logs`: Get recent system logs.
- `execute_mikrotik_command`: **Custom API Call** to run specific commands (e.g., flush cache, reboot).

## Quick Start (NixOS)
1. `cd mikrotik-mcpserver`
2. `cp .env.example .env` (fill in your router credentials)
3. `nix develop`
4. `python server.py --sse` (runs on port 1997)

## Configuration for n8n
- **SSE URL**: `http://<YOUR_IP>:1997/mikrotik-mcpserver/sse`
