# NixOS MCP Server (Python) - Markdown to Word & PDF

This is a Model Context Protocol (MCP) server implementation using Python on NixOS for converting Markdown to Word (.docx) and PDF files.

## Prerequisites

- [Nix](https://nixos.org/download.html) with Flakes enabled.

## Setup

1.  **Enter the development shell:**
    ```bash
    nix develop
    ```
    This will automatically set up a Python virtual environment (`.venv`) and install the `mcp` library using `uv`, along with `pandoc` and `texlive` for PDF generation.

2.  **Run the server:**
    The server uses `stdio` by default (for Claude Desktop).
    ```bash
    python server.py
    ```

    To run for **n8n** (SSE mode):
    ```bash
    python server.py --sse
    ```

## Available Tools

- `convert_markdown_to_docx`: Convert Markdown text to Word.
- `convert_markdown_to_pdf`: Convert Markdown text to PDF.
- `convert_md_file_to_docx`: Convert a .md file to Word.
- `convert_md_file_to_pdf`: Convert a .md file to PDF.

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
    "md-to-doc-pdf": {
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
*Note: Replace `/path/to/project/md-to-word-mcpserver` with the absolute path to your folder.*
