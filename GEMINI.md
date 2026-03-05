# GEMINI.md - Instructional Context

This document provides essential information and instructions for interacting with the **MCP Servers Suite** project.

## Project Overview

*   **Purpose:** A suite of Model Context Protocol (MCP) servers to extend AI agent capabilities:
    1.  **Markdown to Word & PDF**: Document conversion tools.
    2.  **Mikrotik Management**: Network monitoring and management via RouterOS API.
*   **Target Platform:** NixOS (Nix Flakes) and Debian/Ubuntu systems.
*   **Key Technologies:**
    *   **Python 3**: Core implementation language.
    *   **FastMCP**: SDK for building MCP servers.
    *   **Pandoc & TeX Live**: Document conversion (DOCX/PDF).
    *   **routeros-api**: Library for Mikrotik integration.
    *   **uv**: Package and environment management.

## Architecture

### 1. Markdown to Word & PDF
Located in `md-to-word-mcpserver/`:
- `server.py`: Conversion tools (`convert_markdown_to_pdf`, etc.).
- Port: `1996` (SSE Mode).

### 2. Mikrotik Management
Located in `mikrotik-mcpserver/`:
- `server.py`: Network tools (`get_hotspot_active_users`, `get_dhcp_leases`, etc.).
- Port: `1997` (SSE Mode).

## Building and Running

### Development Environment (NixOS)
To enter the development shell for a specific server:
```bash
cd <server-directory>
nix develop
```

### Running for n8n (SSE)
```bash
# Markdown Server
cd md-to-word-mcpserver && nix develop --command python server.py --sse

# Mikrotik Server
cd mikrotik-mcpserver && nix develop --command python server.py --sse
```

## Deployment / Claude Desktop Integration

```json
{
  "mcpServers": {
    "md-to-doc-pdf": {
      "command": "nix",
      "args": [
        "develop",
        "/absolute/path/to/md-to-word-mcpserver",
        "--command",
        "python",
        "/absolute/path/to/md-to-word-mcpserver/server.py"
      ]
    },
    "mikrotik-mgmt": {
      "command": "nix",
      "args": [
        "develop",
        "/absolute/path/to/mikrotik-mcpserver",
        "--command",
        "python",
        "/absolute/path/to/mikrotik-mcpserver/server.py"
      ]
    }
  }
}
```
