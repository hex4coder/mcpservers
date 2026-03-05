import os
from proxmoxer import ProxmoxAPI
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Proxmox Management Server")

# Helper function to get Proxmox API connection
def get_proxmox_api():
    host = os.getenv("PROXMOX_HOST")
    user = os.getenv("PROXMOX_USER")
    password = os.getenv("PROXMOX_PASSWORD")
    verify_ssl = os.getenv("PROXMOX_VERIFY_SSL", "False").lower() == "true"

    if not all([host, user, password]):
        raise Exception("Proxmox credentials not fully configured in environment.")

    return ProxmoxAPI(host, user=user, password=password, verify_ssl=verify_ssl)

# --- NODE TOOLS ---

@mcp.tool()
def get_nodes_status() -> str:
    """Get status of all Proxmox nodes (CPU, RAM, Uptime)."""
    try:
        proxmox = get_proxmox_api()
        nodes = proxmox.nodes.get()
        output = "Proxmox Nodes Status:
"
        for n in nodes:
            output += (f"- Node: {n['node']} | Status: {n['status']} | "
                       f"CPU: {n.get('cpu', 0)*100:.1f}% | "
                       f"RAM: {int(n.get('mem', 0))/1024/1024/1024:.1f}GB / {int(n.get('maxmem', 0))/1024/1024/1024:.1f}GB | "
                       f"Uptime: {n.get('uptime', 0)}s
")
        return output
    except Exception as e:
        return f"Error: {str(e)}"

# --- VM/CONTAINER TOOLS ---

@mcp.tool()
def list_all_vms(node: str) -> str:
    """List all VMs and Containers on a specific node."""
    try:
        proxmox = get_proxmox_api()
        vms = proxmox.nodes(node).qemu.get()
        lxcs = proxmox.nodes(node).lxc.get()
        
        output = f"VMs/LXCs on Node '{node}':
"
        for v in vms:
            output += f"- VM {v['vmid']}: {v['name']} ({v['status']})
"
        for l in lxcs:
            output += f"- LXC {l['vmid']}: {l['name']} ({l['status']})
"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_vm_status(node: str, vmid: int) -> str:
    """Get detailed status of a specific VM or Container."""
    try:
        proxmox = get_proxmox_api()
        # Try QEMU first
        try:
            status = proxmox.nodes(node).qemu(vmid).status.current.get()
        except:
            status = proxmox.nodes(node).lxc(vmid).status.current.get()
            
        return (f"Status for {status.get('name', vmid)}:
"
                f"- State: {status['status']}
"
                f"- CPU Usage: {status.get('cpu', 0)*100:.1f}%
"
                f"- RAM: {int(status.get('mem', 0))/1024/1024:.1f}MB
"
                f"- Uptime: {status.get('uptime', 0)}s")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def manage_vm_power(node: str, vmid: int, action: str) -> str:
    """
    Manage VM power status. 
    Actions: start, stop, shutdown, reboot, reset, suspend, resume
    """
    try:
        proxmox = get_proxmox_api()
        # Detect if it's QEMU or LXC
        vm_type = "qemu"
        try:
            proxmox.nodes(node).qemu(vmid).status.current.get()
        except:
            vm_type = "lxc"

        if vm_type == "qemu":
            proxmox.nodes(node).qemu(vmid).status.post(action)
        else:
            proxmox.nodes(node).lxc(vmid).status.post(action)
            
        return f"Command '{action}' sent to {vm_type} {vmid} on node {node}."
    except Exception as e:
        return f"Error: {str(e)}"

# --- BACKUP & SNAPSHOT TOOLS ---

@mcp.tool()
def create_vm_snapshot(node: str, vmid: int, snapname: str, description: str = "") -> str:
    """Create a snapshot for a VM."""
    try:
        proxmox = get_proxmox_api()
        proxmox.nodes(node).qemu(vmid).snapshot.post(snapname=snapname, description=description)
        return f"Creating snapshot '{snapname}' for VM {vmid}..."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_vm_snapshots(node: str, vmid: int) -> str:
    """List all snapshots of a specific VM."""
    try:
        proxmox = get_proxmox_api()
        snapshots = proxmox.nodes(node).qemu(vmid).snapshot.get()
        if not snapshots: return "No snapshots found."
        return f"Snapshots for VM {vmid}:
" + "
".join([f"- {s['name']} | {s.get('description', '-')}" for s in snapshots])
    except Exception as e:
        return f"Error: {str(e)}"

# --- STORAGE TOOLS ---

@mcp.tool()
def get_storage_status(node: str) -> str:
    """Check storage usage on a specific node."""
    try:
        proxmox = get_proxmox_api()
        storage = proxmox.nodes(node).storage.get()
        output = f"Storage on Node '{node}':
"
        for s in storage:
            used = int(s.get('used', 0))/1024/1024/1024
            total = int(s.get('total', 0))/1024/1024/1024
            output += f"- {s['storage']} ({s['type']}): {used:.1f}GB / {total:.1f}GB ({s.get('used_fraction', 0)*100:.1f}%)
"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import sys
    transport_type = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport_type = "sse"
    
    if transport_type == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=1998, sse_path="/proxmox-mcpserver/sse")
    else:
        mcp.run(transport="stdio")
