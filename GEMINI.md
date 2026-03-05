# GEMINI.md - Instructional Context

This document provides essential information and instructions for interacting with the **Markdown to Word MCP Server** project.

## Project Overview

*   **Purpose:** A Model Context Protocol (MCP) server that provides tools for converting Markdown text or files into Microsoft Word (`.docx`) documents.
*   **Target Platform:** NixOS (using Nix Flakes for environment reproducibility).
*   **Key Technologies:**
    *   **Python 3**: The core implementation language.
    *   **FastMCP (mcp SDK)**: High-level framework for building MCP servers.
    *   **Pandoc**: The underlying document conversion engine (installed via Nix).
    *   **pypandoc**: Python wrapper for Pandoc.
    *   **uv**: Fast Python package installer and virtual environment manager.

## Architecture

The project is located in the `md-to-word-mcpserver` directory:
- `md-to-word-mcpserver/server.py`: Contains the server logic and tool definitions.
- `md-to-word-mcpserver/flake.nix`: Defines the system-level dependencies.
- `md-to-word-mcpserver/README.md`: Basic setup and usage.
- `md-to-word-mcpserver/GuideUse.md`: Guide for n8n integration.

## Building and Running

### Development Environment
To enter the development shell:
```bash
cd md-to-word-mcpserver
nix develop
```

### Running the Server
```bash
# Within 'nix develop' shell inside md-to-word-mcpserver/
python server.py
```

## Deployment / Claude Desktop Integration

```json
{
  "mcpServers": {
    "md-to-word": {
      "command": "nix",
      "args": [
        "develop",
        "/path/to/project/md-to-word-mcpserver",
        "--command",
        "python",
        "/path/to/project/md-to-word-mcpserver/server.py"
      ]
    }
  }
}
```

