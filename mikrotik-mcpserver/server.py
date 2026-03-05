import os
import routeros_api
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Mikrotik Management Server")

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

@mcp.tool()
def get_system_resources() -> str:
    """
    Get system resources like CPU usage, uptime, and memory status.
    """
    try:
        connection = get_api_connection()
        api = connection.get_api()
        resource = api.get_resource('/system/resource').get()
        connection.disconnect()
        
        res = resource[0]
        return f"Uptime: {res['uptime']}, CPU Load: {res['cpu-load']}%, Free Memory: {int(res['free-memory'])/1024/1024:.2f} MB"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_hotspot_active_users() -> str:
    """
    Get a list of currently active hotspot users.
    """
    try:
        connection = get_api_connection()
        api = connection.get_api()
        active_users = api.get_resource('/ip/hotspot/active').get()
        connection.disconnect()
        
        if not active_users:
            return "No active hotspot users found."
            
        user_list = [f"- User: {u['user']}, IP: {u['address']}, Uptime: {u['uptime']}" for u in active_users]
        return "Active Hotspot Users:
" + "
".join(user_list)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_dhcp_leases() -> str:
    """
    Retrieve the list of DHCP leases (connected devices).
    """
    try:
        connection = get_api_connection()
        api = connection.get_api()
        leases = api.get_resource('/ip/dhcp-server/lease').get()
        connection.disconnect()
        
        if not leases:
            return "No DHCP leases found."
            
        lease_list = [f"- {l.get('comment', 'Unknown')}: {l['address']} ({l['mac-address']}) - Status: {l['status']}" for l in leases]
        return "DHCP Leases:
" + "
".join(lease_list)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import sys
    
    # Check for transport type in command line arguments
    transport_type = "stdio"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--sse":
            transport_type = "sse"
    
    if transport_type == "sse":
        # Configure for network access
        mcp.run(
            transport="sse",
            host="0.0.0.0",
            port=1997, # Using 1997 for Mikrotik MCP
            sse_path="/mikrotik-mcpserver/sse"
        )
    else:
        mcp.run(transport="stdio")
