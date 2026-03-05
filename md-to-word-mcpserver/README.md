# NixOS MCP Server (Python)

This is a basic Model Context Protocol (MCP) server implementation using Python on NixOS.

## Prerequisites

- [Nix](https://nixos.org/download.html) with Flakes enabled.

## Setup

1.  **Enter the development shell:**
    ```bash
    nix develop
    ```
    This will automatically set up a Python virtual environment (`.venv`) and install the `mcp` library using `uv`.

2.  **Run the server:**
    The server uses `stdio` by default, which is what Claude Desktop expects.
    ```bash
    python server.py
    ```

## Testing

To test your server with the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
npx @modelcontextprotocol/inspector python server.py
```

## Configuring with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-nixos-server": {
      "command": "nix",
      "args": [
        "develop",
        "--command",
        "python",
        "/path/to/your/project/server.py"
      ]
    }
  }
}
```
*Note: Replace `/path/to/your/project/server.py` with the absolute path to your file.*
