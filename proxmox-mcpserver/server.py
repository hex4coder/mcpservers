import os
from proxmoxer import ProxmoxAPI
from mcp.server.fastmcp import FastMCP
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

# --- NODE TOOLS ---

@mcp.tool()
def get_nodes_status() -> str:
    """Get status of all Proxmox nodes (CPU, RAM, Uptime)."""
    try:
        proxmox = get_proxmox_api()
        nodes = proxmox.nodes.get()
        output = "Proxmox Nodes Status:\n"
        for n in nodes:
            output += (f"- Node: {n['node']} | Status: {n['status']} | "
                       f"CPU: {n.get('cpu', 0)*100:.1f}% | "
                       f"RAM: {int(n.get('mem', 0))/1024/1024/1024:.1f}GB / {int(n.get('maxmem', 0))/1024/1024/1024:.1f}GB | "
                       f"Uptime: {n.get('uptime', 0)}s\n")
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
        
        output = f"VMs/LXCs on Node '{node}':\n"
        for v in vms:
            output += f"- VM {v['vmid']}: {v['name']} ({v['status']})\n"
        for l in lxcs:
            output += f"- LXC {l['vmid']}: {l['name']} ({l['status']})\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_vm_status(node: str, vmid: int) -> str:
    """Get detailed real-time status of a specific VM or Container."""
    try:
        proxmox = get_proxmox_api()
        try:
            status = proxmox.nodes(node).qemu(vmid).status.current.get()
        except:
            status = proxmox.nodes(node).lxc(vmid).status.current.get()
            
        return (f"Status for {status.get('name', vmid)}:\n"
                f"- State: {status['status']}\n"
                f"- CPU Usage: {status.get('cpu', 0)*100:.1f}%\n"
                f"- RAM: {int(status.get('mem', 0))/1024/1024:.1f}MB\n"
                f"- Net In: {int(status.get('netin', 0))/1024/1024:.2f}MB, Net Out: {int(status.get('netout', 0))/1024/1024:.2f}MB\n"
                f"- Uptime: {status.get('uptime', 0)}s")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def manage_vm_power(node: str, vmid: int, action: str) -> str:
    """
    Manage VM/Container power status.
    Actions: start, stop, shutdown, reboot, reset, suspend, resume
    """
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
            
        return f"Command '{action}' successfully sent to {vm_type} {vmid} on node {node}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def delete_vm_or_container(node: str, vmid: int) -> str:
    """Delete a VM or Container (must be stopped first)."""
    try:
        proxmox = get_proxmox_api()
        vm_type = "qemu"
        try:
            proxmox.nodes(node).qemu(vmid).status.current.get()
        except:
            vm_type = "lxc"

        if vm_type == "qemu":
            proxmox.nodes(node).qemu(vmid).delete()
        else:
            proxmox.nodes(node).lxc(vmid).delete()
            
        return f"Successfully deleted {vm_type} {vmid} from node {node}."
    except Exception as e:
        return f"Error: {str(e)}"

# --- PROVISIONING TOOLS ---

@mcp.tool()
def create_container(node: str, vmid: int, ostemplate: str, password: str, hostname: str = None, memory: int = 512, storage: str = "local-lvm") -> str:
    """
    Create a new LXC Container.
    Example ostemplate: 'local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst'
    """
    try:
        proxmox = get_proxmox_api()
        params = {
            'vmid': vmid,
            'ostemplate': ostemplate,
            'password': password,
            'memory': memory,
            'storage': storage,
            'net0': 'name=eth0,bridge=vmbr0,ip=dhcp'
        }
        if hostname: params['hostname'] = hostname
        
        proxmox.nodes(node).lxc.post(**params)
        return f"Successfully initiated creation of LXC {vmid} ({hostname or 'unnamed'}) on {node}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def create_vm_from_template(node: str, vmid: int, template_vmid: int, name: str = None) -> str:
    """Clone a VM from an existing template."""
    try:
        proxmox = get_proxmox_api()
        params = {'newid': vmid}
        if name: params['name'] = name
        
        proxmox.nodes(node).qemu(template_vmid).clone.post(**params)
        return f"Successfully initiated clone of VM template {template_vmid} to new VM {vmid} ({name or 'unnamed'})."
    except Exception as e:
        return f"Error: {str(e)}"

# --- CONFIGURATION TOOLS ---

@mcp.tool()
def set_vm_config(node: str, vmid: int, cores: int = None, memory: int = None, onboot: bool = None) -> str:
    """Update CPU cores, Memory (MB), or Onboot status for a VM."""
    try:
        proxmox = get_proxmox_api()
        params = {}
        if cores: params['cores'] = cores
        if memory: params['memory'] = memory
        if onboot is not None: params['onboot'] = 1 if onboot else 0
        
        if not params: return "No configuration changes provided."
        
        proxmox.nodes(node).qemu(vmid).config.post(**params)
        return f"Successfully updated configuration for VM {vmid} on node {node}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_container_config(node: str, vmid: int, cores: int = None, memory: int = None, onboot: bool = None) -> str:
    """Update CPU cores, Memory (MB), or Onboot status for a Container."""
    try:
        proxmox = get_proxmox_api()
        params = {}
        if cores: params['cores'] = cores
        if memory: params['memory'] = memory
        if onboot is not None: params['onboot'] = 1 if onboot else 0
        
        if not params: return "No configuration changes provided."
        
        proxmox.nodes(node).lxc(vmid).config.post(**params)
        return f"Successfully updated configuration for LXC {vmid} on node {node}."
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
        return f"Snapshots for VM {vmid}:\n" + "\n".join([f"- {s['name']} | {s.get('description', '-')}" for s in snapshots])
    except Exception as e:
        return f"Error: {str(e)}"

# --- STORAGE TOOLS ---

@mcp.tool()
def get_storage_status(node: str) -> str:
    """Check storage usage on a specific node."""
    try:
        proxmox = get_proxmox_api()
        storage = proxmox.nodes(node).storage.get()
        output = f"Storage on Node '{node}':\n"
        for s in storage:
            used = int(s.get('used', 0))/1024/1024/1024
            total = int(s.get('total', 0))/1024/1024/1024
            output += f"- {s['storage']} ({s['type']}): {used:.1f}GB / {total:.1f}GB ({s.get('used_fraction', 0)*100:.1f}%)\n"
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
