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

# --- HOTSPOT SERVER MANAGEMENT ---

@mcp.tool()
def get_hotspot_servers() -> str:
    """List all hotspot server instances."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        servers = api.get_resource('/ip/hotspot').get()
        connection.disconnect()
        if not servers: return "No hotspot servers configured."
        return "Hotspot Servers:\n" + "\n".join([f"- {s['name']} on {s['interface']} (Profile: {s['profile']})" for s in servers])
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_hotspot_server_profiles() -> str:
    """List hotspot server profiles (where HTML directory is set)."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        profiles = api.get_resource('/ip/hotspot/profile').get()
        connection.disconnect()
        return "Hotspot Server Profiles:\n" + "\n".join([f"- {p['name']} | HTML Dir: {p['html-directory']} | DNS Name: {p.get('dns-name', '-')}" for p in profiles])
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_hotspot_html_directory(profile_name: str, html_directory: str) -> str:
    """Change the login page HTML directory for a server profile."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        resource = api.get_resource('/ip/hotspot/profile')
        profile = resource.get(name=profile_name)
        if not profile: return f"Server Profile {profile_name} not found."
        resource.set(id=profile[0]['id'], **{'html-directory': html_directory})
        connection.disconnect()
        return f"Successfully updated HTML directory for {profile_name} to {html_directory}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- HOTSPOT USER & PROFILE MANAGEMENT ---

@mcp.tool()
def get_hotspot_user_profiles() -> str:
    """List all user profiles including bandwidth limits (rate-limit)."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        profiles = api.get_resource('/ip/hotspot/user/profile').get()
        connection.disconnect()
        output = "Hotspot User Profiles:\n"
        for p in profiles:
            limit = p.get('rate-limit', 'No Limit')
            shared = p.get('shared-users', '1')
            output += f"- {p['name']} | Limit: {limit} | Shared: {shared}\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def add_hotspot_user_profile(name: str, rate_limit: str = None, shared_users: int = 1) -> str:
    """
    Create or update a hotspot user profile with bandwidth management.
    Example rate_limit: '1M/1M' (Upload/Download).
    """
    try:
        connection = get_api_connection()
        api = connection.get_api()
        resource = api.get_resource('/ip/hotspot/user/profile')
        params = {'name': name, 'shared-users': str(shared_users)}
        if rate_limit:
            params['rate-limit'] = rate_limit
        
        existing = resource.get(name=name)
        if existing:
            resource.set(id=existing[0]['id'], **params)
            msg = f"Updated profile {name}"
        else:
            resource.add(**params)
            msg = f"Created profile {name}"
            
        connection.disconnect()
        return msg
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_user_profile(user_name: str, profile_name: str) -> str:
    """Assign a specific profile (and its bandwidth limits) to a user."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        # Find user
        user_resource = api.get_resource('/ip/hotspot/user')
        user = user_resource.get(name=user_name)
        if not user: return f"User {user_name} not found."
        
        # Find profile
        profile_resource = api.get_resource('/ip/hotspot/user/profile')
        profile = profile_resource.get(name=profile_name)
        if not profile: return f"Profile {profile_name} not found."
        
        user_resource.set(id=user[0]['id'], profile=profile_name)
        connection.disconnect()
        return f"Successfully moved user {user_name} to profile {profile_name}"
    except Exception as e:
        return f"Error: {str(e)}"

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

# --- DHCP & ARP ---

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

if __name__ == "__main__":
    import sys
    transport_type = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport_type = "sse"
    
    if transport_type == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=1997, sse_path="/mikrotik-mcpserver/sse")
    else:
        mcp.run(transport="stdio")
