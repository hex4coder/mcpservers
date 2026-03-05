import os
from proxmoxer import ProxmoxAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Proxmox Ultimate Management Server")

# Helper function to get Proxmox API connection
def get_proxmox_api():
    host = os.getenv("PROXMOX_HOST")
    user = os.getenv("PROXMOX_USER")
    password = os.getenv("PROXMOX_PASSWORD")
    verify_ssl = os.getenv("PROXMOX_VERIFY_SSL", "False").lower() == "true"

    if not all([host, user, password]):
        raise Exception("Proxmox credentials not fully configured in environment.")

    return ProxmoxAPI(host, user=user, password=password, verify_ssl=verify_ssl)

# --- NODE & CLUSTER TOOLS ---

@mcp.tool()
def get_nodes_status() -> str:
    """Get status of all Proxmox nodes (CPU, RAM, Uptime)."""
    try:
        proxmox = get_proxmox_api()
        nodes = proxmox.nodes.get()
        output = "📊 Proxmox Nodes Status:\n"
        for n in nodes:
            cpu = n.get('cpu', 0) * 100
            mem_used = int(n.get('mem', 0)) / (1024**3)
            mem_max = int(n.get('maxmem', 0)) / (1024**3)
            uptime_days = int(n.get('uptime', 0)) // 86400
            
            output += (f"🖥️ Node: {n['node']} ({n['status'].upper()})\n"
                       f"   - CPU Usage: {cpu:.1f}%\n"
                       f"   - Memory: {mem_used:.2f} GB / {mem_max:.2f} GB ({ (mem_used/mem_max)*100 if mem_max > 0 else 0 :.1f}%)\n"
                       f"   - Uptime: {uptime_days} days\n\n")
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_storage_status(node: str) -> str:
    """Check storage usage (Disk) on a specific node."""
    try:
        proxmox = get_proxmox_api()
        storage = proxmox.nodes(node).storage.get()
        output = f"💾 Storage Status on Node '{node}':\n"
        for s in storage:
            if s['active'] == 0: continue
            used = int(s.get('used', 0)) / (1024**3)
            total = int(s.get('total', 0)) / (1024**3)
            perc = (used / total) * 100 if total > 0 else 0
            
            output += (f"   - [{s['storage']}] ({s['type']}):\n"
                       f"     Used: {used:.2f} GB / {total:.2f} GB ({perc:.1f}%)\n")
        return output
    except Exception as e:
        return f"Error: {str(e)}"

# --- VM/CONTAINER MANAGEMENT ---

@mcp.tool()
def list_all_vms(node: str) -> str:
    """List all VMs and Containers on a specific node."""
    try:
        proxmox = get_proxmox_api()
        vms = proxmox.nodes(node).qemu.get()
        lxcs = proxmox.nodes(node).lxc.get()
        
        output = f"📦 VMs/LXCs on Node '{node}':\n"
        for v in vms:
            output += f"   - [VM {v['vmid']}] {v['name']} ({v['status']})\n"
        for l in lxcs:
            output += f"   - [LXC {l['vmid']}] {l['name']} ({l['status']})\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_vm_status(node: str, vmid: int) -> str:
    """Get detailed real-time status of a specific VM or Container (CPU, RAM, Net)."""
    try:
        proxmox = get_proxmox_api()
        try:
            status = proxmox.nodes(node).qemu(vmid).status.current.get()
        except:
            status = proxmox.nodes(node).lxc(vmid).status.current.get()
            
        cpu = status.get('cpu', 0) * 100
        mem = int(status.get('mem', 0)) / (1024**2)
        mem_max = int(status.get('maxmem', 0)) / (1024**2)
        
        return (f"🔍 Status for {status.get('name', vmid)}:\n"
                f"   - State: {status['status'].upper()}\n"
                f"   - CPU Usage: {cpu:.1f}%\n"
                f"   - Memory: {mem:.1f} MB / {mem_max:.1f} MB\n"
                f"   - Network In: {int(status.get('netin', 0))/1024/1024:.2f} MB\n"
                f"   - Network Out: {int(status.get('netout', 0))/1024/1024:.2f} MB\n"
                f"   - Uptime: {int(status.get('uptime', 0))//3600} hours")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def manage_vm_power(node: str, vmid: int, action: str) -> str:
    """Manage VM/Container power (start, stop, shutdown, reboot, etc)."""
    try:
        proxmox = get_proxmox_api()
        vm_type = "qemu"
        try:
            proxmox.nodes(node).qemu(vmid).status.current.get()
        except:
            vm_type = "lxc"

        if vm_type == "qemu":
            proxmox.nodes(node).qemu(vmid).status.post(action)
        else:
            proxmox.nodes(node).lxc(vmid).status.post(action)
            
        return f"✅ Action '{action}' sent to {vm_type} {vmid} on {node}."
    except Exception as e:
        return f"Error: {str(e)}"

# --- PROVISIONING & CONFIG ---

@mcp.tool()
def create_container(node: str, vmid: int, ostemplate: str, password: str, hostname: str = None, memory: int = 512, storage: str = "local-lvm") -> str:
    """Create a new LXC Container."""
    try:
        proxmox = get_proxmox_api()
        params = {'vmid': vmid, 'ostemplate': ostemplate, 'password': password, 'memory': memory, 'storage': storage, 'net0': 'name=eth0,bridge=vmbr0,ip=dhcp'}
        if hostname: params['hostname'] = hostname
        proxmox.nodes(node).lxc.post(**params)
        return f"🚀 Creating LXC {vmid} ({hostname or 'unnamed'}) on {node}..."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_vm_config(node: str, vmid: int, cores: int = None, memory: int = None, onboot: bool = None) -> str:
    """Update VM CPU, RAM, or Auto-start."""
    try:
        proxmox = get_proxmox_api()
        params = {}
        if cores: params['cores'] = cores
        if memory: params['memory'] = memory
        if onboot is not None: params['onboot'] = 1 if onboot else 0
        proxmox.nodes(node).qemu(vmid).config.post(**params)
        return f"⚙️ Config updated for VM {vmid} on {node}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def create_vm_snapshot(node: str, vmid: int, snapname: str, description: str = "") -> str:
    """Create a snapshot for a VM."""
    try:
        proxmox = get_proxmox_api()
        proxmox.nodes(node).qemu(vmid).snapshot.post(snapname=snapname, description=description)
        return f"📸 Snapshot '{snapname}' created for VM {vmid}."
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
        transport = SseServerTransport("/proxmox-mcpserver/messages")
        async def handle_sse(request: Request):
            async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
                await mcp._mcp_server.run(streams[0], streams[1], mcp._mcp_server.create_initialization_options())
        app = Starlette(routes=[Route("/proxmox-mcpserver/sse", endpoint=handle_sse), Mount("/proxmox-mcpserver/messages", app=transport.handle_post_message)])
        print("Starting Proxmox MCP Server on http://0.0.0.0:1998/proxmox-mcpserver/sse")
        uvicorn.run(app, host="0.0.0.0", port=1998)
    else:
        mcp.run(transport="stdio")
