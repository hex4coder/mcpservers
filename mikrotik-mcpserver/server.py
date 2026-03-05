import os
import routeros_api
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Mikrotik Ultimate Management Server")

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
        use_ssl=False,
        plaintext_login=True
    )
    return connection

# --- RESOURCE MONITORING ---

@mcp.tool()
def get_system_resources() -> str:
    """Get CPU, Memory (RAM), and Uptime status of Mikrotik."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        res = api.get_resource('/system/resource').get()[0]
        connection.disconnect()
        
        cpu_load = res.get('cpu-load', '0')
        free_mem = int(res.get('free-memory', 0)) / (1024**2)
        total_mem = int(res.get('total-memory', 0)) / (1024**2)
        
        return (f"📊 Mikrotik System Status ({res.get('board-name', 'N/A')}):\n"
                f"   - CPU Load: {cpu_load}%\n"
                f"   - Memory: {free_mem:.1f} MB Free / {total_mem:.1f} MB Total\n"
                f"   - Uptime: {res['uptime']}\n"
                f"   - Architecture: {res.get('architecture-name', 'N/A')}\n"
                f"   - Version: {res.get('version', 'N/A')}")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_storage_status() -> str:
    """Get Disk/Storage usage on Mikrotik."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        res = api.get_resource('/system/resource').get()[0]
        connection.disconnect()
        
        free_disk = int(res.get('free-hdd-space', 0)) / (1024**2)
        total_disk = int(res.get('total-hdd-space', 0)) / (1024**2)
        
        return (f"💾 Mikrotik Storage Status:\n"
                f"   - Free Disk: {free_disk:.2f} MB\n"
                f"   - Total Disk: {total_disk:.2f} MB\n"
                f"   - Used Disk: {(total_disk - free_disk):.2f} MB ({((total_disk-free_disk)/total_disk)*100 if total_disk > 0 else 0:.1f}%)")
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
        return "📜 Recent Logs:\n" + "\n".join([f"[{l['time']}] {l['topics']}: {l['message']}" for l in last_logs])
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
        output = "🌐 Interfaces Status:\n"
        for i in interfaces:
            status = "UP" if i['running'] == 'true' else "DOWN"
            output += f"   - {i['name']} ({i['type']}): {status} | Rx: {int(i['rx-byte'])/1024/1024:.1f}MB, Tx: {int(i['tx-byte'])/1024/1024:.1f}MB\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_hotspot_active_summary() -> str:
    """Monitor active hotspot sessions."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        active = api.get_resource('/ip/hotspot/active').get()
        connection.disconnect()
        if not active: return "No active hotspot users."
        return f"📶 Active Users: {len(active)}\n" + "\n".join([f"   - {u['user']} ({u['address']}) | {u['uptime']}" for u in active])
    except Exception as e:
        return f"Error: {str(e)}"

# --- USER MANAGEMENT ---

@mcp.tool()
def add_hotspot_user_profile(name: str, rate_limit: str = None, shared_users: int = 1) -> str:
    """Create/Update hotspot user profile with bandwidth limit (e.g., '1M/1M')."""
    try:
        connection = get_api_connection()
        api = connection.get_api()
        resource = api.get_resource('/ip/hotspot/user/profile')
        params = {'name': name, 'shared-users': str(shared_users)}
        if rate_limit: params['rate-limit'] = rate_limit
        
        existing = resource.get(name=name)
        if existing: resource.set(id=existing[0]['id'], **params)
        else: resource.add(**params)
        
        connection.disconnect()
        return f"✅ Profile '{name}' configured (Limit: {rate_limit or 'No Limit'})."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import sys
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.requests import Request

    transport_type = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport_type = "sse"
    
    if transport_type == "sse":
        transport = SseServerTransport("/mikrotik-mcpserver/messages")
        async def handle_sse(request: Request):
            async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
                await mcp._mcp_server.run(streams[0], streams[1], mcp._mcp_server.create_initialization_options())
        app = Starlette(routes=[Route("/mikrotik-mcpserver/sse", endpoint=handle_sse), Mount("/mikrotik-mcpserver/messages", app=transport.handle_post_message)])
        print("Starting Mikrotik MCP Server on http://0.0.0.0:1997/mikrotik-mcpserver/sse")
        uvicorn.run(app, host="0.0.0.0", port=1997)
    else:
        mcp.run(transport="stdio")
