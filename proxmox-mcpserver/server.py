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

# ==========================================
# 1. NODE & CLUSTER MONITORING
# ==========================================

@mcp.tool()
def get_proxmox_nodes_status() -> str:
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
def get_proxmox_storage_status(node: str) -> str:
    """Check storage usage (Disk) on a specific Proxmox node."""
    try:
        proxmox = get_proxmox_api()
        storage = proxmox.nodes(node).storage.get()
        output = f"💾 Proxmox Storage Status on Node '{node}':\n"
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

@mcp.tool()
def get_proxmox_node_networks(node: str) -> str:
    """List all network interfaces and IP addresses for a specific Proxmox node."""
    try:
        proxmox = get_proxmox_api()
        networks = proxmox.nodes(node).network.get()
        output = f"🌐 Network Interfaces on Node '{node}':\n"
        for net in networks:
            ip = net.get('address', 'N/A')
            cidr = net.get('cidr', 'N/A')
            iface_type = net.get('type', 'Unknown')
            output += f"   - {net['iface']} ({iface_type}): {ip} | CIDR: {cidr} | Status: {'Active' if net.get('active') else 'Inactive'}\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def check_proxmox_connectivity(target: str = "google.com", count: int = 4) -> str:
    """Check network connectivity from the server using ping."""
    import subprocess
    try:
        # We run the ping command locally on the system where the MCP server is hosted
        result = subprocess.run(
            ["ping", "-c", str(count), target],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            return f"✅ Connectivity to {target} OK:\n{result.stdout}"
        else:
            return f"❌ Connectivity to {target} FAILED:\n{result.stderr or result.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def update_proxmox_repositories(node: str) -> str:
    """Trigger an APT update (repository refresh) on a Proxmox node."""
    try:
        proxmox = get_proxmox_api()
        # This returns a task ID representing the APT update process
        task_id = proxmox.nodes(node).apt.update.post()
        return f"🔄 Repository update initiated on node '{node}'. Task ID: {task_id}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_proxmox_packages(node: str) -> str:
    """List available updates and packages on a Proxmox node."""
    try:
        proxmox = get_proxmox_api()
        packages = proxmox.nodes(node).apt.list.get()
        updates = [p for p in packages if p.get('Update')]
        
        output = f"📦 Proxmox Package Status for Node '{node}':\n"
        output += f"   - Total Packages: {len(packages)}\n"
        output += f"   - Updates Available: {len(updates)}\n"
        
        if updates:
            output += "\n📝 Summary of available updates:\n"
            for p in updates[:15]:  # Show top 15 updates
                output += f"     - {p['Package']} ({p['OldVersion']} -> {p['Version']})\n"
            if len(updates) > 15:
                output += f"     ... and {len(updates)-15} more.\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def execute_proxmox_shell_command(command: str) -> str:
    """Execute a raw shell command on the host (Debian Proxmox). 
    USE WITH CAUTION! This runs directly on the server's OS.
    Example: 'ip a', 'df -h', 'apt list --installed'
    """
    import subprocess
    try:
        # Run the command with shell=True for full CLI support
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return f"✅ Command: {command}\nOutput:\n{result.stdout}"
        else:
            return f"❌ Command: {command} (Return code: {result.returncode})\nError:\n{result.stderr or result.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 2. VM/CONTAINER MANAGEMENT
# ==========================================

@mcp.tool()
def list_proxmox_vms(node: str) -> str:
    """List all VMs and Containers on a specific Proxmox node."""
    try:
        proxmox = get_proxmox_api()
        vms = proxmox.nodes(node).qemu.get()
        lxcs = proxmox.nodes(node).lxc.get()
        
        output = f"📦 Proxmox VMs/LXCs on Node '{node}':\n"
        for v in vms:
            output += f"   - [VM {v['vmid']}] {v['name']} ({v['status']})\n"
        for l in lxcs:
            output += f"   - [LXC {l['vmid']}] {l['name']} ({l['status']})\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_proxmox_vm_status(node: str, vmid: int) -> str:
    """Get detailed real-time status of a specific Proxmox VM or Container."""
    try:
        proxmox = get_proxmox_api()
        try:
            status = proxmox.nodes(node).qemu(vmid).status.current.get()
        except:
            status = proxmox.nodes(node).lxc(vmid).status.current.get()
            
        cpu = status.get('cpu', 0) * 100
        mem = int(status.get('mem', 0)) / (1024**2)
        mem_max = int(status.get('maxmem', 0)) / (1024**2)
        
        return (f"🔍 Proxmox Status for {status.get('name', vmid)}:\n"
                f"   - State: {status['status'].upper()}\n"
                f"   - CPU Usage: {cpu:.1f}%\n"
                f"   - Memory: {mem:.1f} MB / {mem_max:.1f} MB\n"
                f"   - Network In: {int(status.get('netin', 0))/1024/1024:.2f} MB\n"
                f"   - Network Out: {int(status.get('netout', 0))/1024/1024:.2f} MB\n"
                f"   - Uptime: {int(status.get('uptime', 0))//3600} hours")
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def manage_proxmox_power(node: str, vmid: int, action: str) -> str:
    """Manage Proxmox VM/Container power (start, stop, shutdown, reboot, etc)."""
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
            
        return f"✅ Action '{action}' sent to Proxmox {vm_type} {vmid} on {node}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def delete_proxmox_vm(node: str, vmid: int) -> str:
    """Delete a Proxmox VM or Container (must be stopped first)."""
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
            
        return f"Successfully deleted Proxmox {vm_type} {vmid} from node {node}."
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 3. PROVISIONING & CONFIGURATION
# ==========================================

@mcp.tool()
def create_proxmox_container(node: str, vmid: int, ostemplate: str, password: str, hostname: str = None, memory: int = 512, storage: str = "local-lvm") -> str:
    """Create a new Proxmox LXC Container."""
    try:
        proxmox = get_proxmox_api()
        params = {'vmid': vmid, 'ostemplate': ostemplate, 'password': password, 'memory': memory, 'storage': storage, 'net0': 'name=eth0,bridge=vmbr0,ip=dhcp'}
        if hostname: params['hostname'] = hostname
        proxmox.nodes(node).lxc.post(**params)
        return f"🚀 Creating Proxmox LXC {vmid} ({hostname or 'unnamed'}) on {node}..."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def clone_proxmox_vm(node: str, vmid: int, template_vmid: int, name: str = None) -> str:
    """Clone a Proxmox VM from an existing template."""
    try:
        proxmox = get_proxmox_api()
        params = {'newid': vmid}
        if name: params['name'] = name
        
        proxmox.nodes(node).qemu(template_vmid).clone.post(**params)
        return f"Successfully initiated clone of Proxmox template {template_vmid} to new VM {vmid}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_proxmox_vm_config(node: str, vmid: int, cores: int = None, memory: int = None, onboot: bool = None) -> str:
    """Update Proxmox VM CPU, RAM, or Auto-start."""
    try:
        proxmox = get_proxmox_api()
        params = {}
        if cores: params['cores'] = cores
        if memory: params['memory'] = memory
        if onboot is not None: params['onboot'] = 1 if onboot else 0
        proxmox.nodes(node).qemu(vmid).config.post(**params)
        return f"⚙️ Proxmox Config updated for VM {vmid}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def set_proxmox_container_config(node: str, vmid: int, cores: int = None, memory: int = None, onboot: bool = None) -> str:
    """Update Proxmox LXC CPU, RAM, or Auto-start."""
    try:
        proxmox = get_proxmox_api()
        params = {}
        if cores: params['cores'] = cores
        if memory: params['memory'] = memory
        if onboot is not None: params['onboot'] = 1 if onboot else 0
        
        proxmox.nodes(node).lxc.config.post(**params)
        return f"Successfully updated configuration for Proxmox LXC {vmid}."
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 4. BACKUP & SNAPSHOT TOOLS
# ==========================================

@mcp.tool()
def create_proxmox_snapshot(node: str, vmid: int, snapname: str, description: str = "") -> str:
    """Create a snapshot for a Proxmox VM."""
    try:
        proxmox = get_proxmox_api()
        proxmox.nodes(node).qemu(vmid).snapshot.post(snapname=snapname, description=description)
        return f"📸 Proxmox Snapshot '{snapname}' created for VM {vmid}."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_proxmox_snapshots(node: str, vmid: int) -> str:
    """List all snapshots of a specific Proxmox VM."""
    try:
        proxmox = get_proxmox_api()
        snapshots = proxmox.nodes(node).qemu(vmid).snapshot.get()
        if not snapshots: return "No Proxmox snapshots found."
        return f"Proxmox Snapshots for VM {vmid}:\n" + "\n".join([f"- {s['name']} | {s.get('description', '-')}" for s in snapshots])
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# MAIN EXECUTION
# ==========================================

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
