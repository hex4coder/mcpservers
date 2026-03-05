import os
import routeros_api
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Mikrotik Pro Management Server")

# Helper function to get Mikrotik API connection
def get_api_connection():
    host = os.getenv("MIKROTIK_HOST")
    username = os.getenv("MIKROTIK_USERNAME")
    password = os.getenv("MIKROTIK_PASSWORD")
    port = int(os.getenv("MIKROTIK_PORT", "8728"))

    if not all([host, username, password]):
        raise Exception("Mikrotik credentials not fully configured in environment.")

    connection = routeros_api.RouterOsApiPool(
        host,
        username=username,
        password=password,
        port=port,
        use_ssl=False
    )
    return connection

# --- SYSTEM TOOLS ---

@mcp.tool()
def get_system_resources() -> str:
    """Get CPU, memory, uptime, and board information."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        res = api.get_resource('/system/resource').get()[0]
        connection.disconnect()
        return (f"Board: {res.get('board-name', 'N/A')}\n"
                f"Uptime: {res['uptime']}\n"
                f"CPU: {res['cpu-load']}% ({res['cpu-count']} core)\n"
                f"Memory: {int(res['free-memory'])/1024/1024:.1f}MB free / {int(res['total-memory'])/1024/1024:.1f}MB total")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_system_logs(lines: int = 10) -> str:
    """Get the last N lines of system logs."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        logs = api.get_resource('/log').get()
        connection.disconnect()
        last_logs = logs[-lines:] if len(logs) > lines else logs
        return "\n".join([f"[{l['time']}] {l['topics']}: {l['message']}" for l in last_logs])
    except Exception as e:
        return f"Error: {str(e)}"

# --- NETWORK TOOLS ---

@mcp.tool()
def get_interfaces() -> str:
    """List all interfaces with their status and traffic."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        interfaces = api.get_resource('/interface').get()
        connection.disconnect()
        output = "Interfaces:\n"
        for i in interfaces:
            status = "UP" if i['running'] == 'true' else "DOWN"
            output += f"- {i['name']} ({i['type']}): {status} | Rx: {int(i['rx-byte'])/1024/1024:.2f}MB, Tx: {int(i['tx-byte'])/1024/1024:.2f}MB\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_ip_addresses() -> str:
    """List all IP addresses assigned to interfaces."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        ips = api.get_resource('/ip/address').get()
        connection.disconnect()
        return "IP Addresses:\n" + "\n".join([f"- {i['address']} on {i['interface']} ({i['network']})" for i in ips])
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_routes() -> str:
    """Get the routing table (Gateways)."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        routes = api.get_resource('/ip/route').get()
        connection.disconnect()
        output = "Routing Table:\n"
        for r in routes:
            active = "*" if r['active'] == 'true' else " "
            output += f"{active} Dst: {r['dst-address']} | Gateway: {r.get('gateway', 'none')} | Distance: {r['distance']}\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_dns_settings() -> str:
    """Get DNS configuration."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        dns = api.get_resource('/ip/dns').get()[0]
        connection.disconnect()
        return f"DNS Servers: {dns.get('servers', 'none')}\nDynamic Servers: {dns.get('dynamic-servers', 'none')}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- HOTSPOT TOOLS ---

@mcp.tool()
def get_hotspot_active_summary() -> str:
    """Get summary of active hotspot sessions."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        active = api.get_resource('/ip/hotspot/active').get()
        connection.disconnect()
        if not active: return "No active hotspot users."
        return f"Total Active Users: {len(active)}\n" + "\n".join([f"- {u['user']} ({u['address']}) | Uptime: {u['uptime']}" for u in active])
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_hotspot_users() -> str:
    """List all registered hotspot users (not just active)."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        users = api.get_resource('/ip/hotspot/user').get()
        connection.disconnect()
        return "Registered Hotspot Users:\n" + "\n".join([f"- {u['name']} (Profile: {u['profile']}) | Comment: {u.get('comment', '-')}" for u in users])
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def add_hotspot_user(name: str, password: str, profile: str = "default", comment: str = "") -> str:
    """Create a new hotspot user."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        api.get_resource('/ip/hotspot/user').add(name=name, password=password, profile=profile, comment=comment)
        connection.disconnect()
        return f"Successfully created hotspot user: {name}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def remove_hotspot_user(name: str) -> str:
    """Remove a hotspot user by name."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        resource = api.get_resource('/ip/hotspot/user')
        user = resource.get(name=name)
        if not user: return f"User {name} not found."
        resource.remove(id=user[0]['id'])
        connection.disconnect()
        return f"Successfully removed hotspot user: {name}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- LEASE & ARP TOOLS ---

@mcp.tool()
def get_dhcp_leases_detailed() -> str:
    """Get detailed DHCP lease information."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        leases = api.get_resource('/ip/dhcp-server/lease').get()
        connection.disconnect()
        return "DHCP Leases:\n" + "\n".join([f"- {l.get('host-name', 'Unknown')} | {l['address']} | MAC: {l['mac-address']} | Status: {l['status']}" for l in leases])
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_arp_table() -> str:
    """Get the ARP table (IP to MAC mapping)."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        arp = api.get_resource('/ip/arp').get()
        connection.disconnect()
        return "ARP Table:\n" + "\n".join([f"- {a['address']} -> {a['mac-address']} on {a['interface']}" for a in arp])
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import sys
    transport_type = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport_type = "sse"
    
    if transport_type == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=1997, sse_path="/mikrotik-mcpserver/sse")
    else:
        mcp.run(transport="stdio")
