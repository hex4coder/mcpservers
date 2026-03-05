import os
import pypandoc
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# Initialize the MCP server
mcp = FastMCP("Markdown to Word & PDF Converter")

# Ensure output directory exists
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper to get base URL (useful for download links)
def get_base_url():
    # You can set this via environment variable if needed
    # Defaulting to localhost for local testing
    host = os.getenv("SERVER_IP", "localhost")
    return f"http://{host}:1996/md-to-word-mcpserver/download"

@mcp.tool()
def convert_markdown_to_docx(markdown_text: str, output_filename: str) -> str:
    """
    Convert Markdown text to a Microsoft Word (.docx) file and return download link.
    """
    try:
        if not output_filename.lower().endswith(".docx"):
            output_filename += ".docx"
        
        file_path = os.path.join(OUTPUT_DIR, output_filename)
        pypandoc.convert_text(markdown_text, 'docx', format='md', outputfile=file_path)
        
        download_url = f"{get_base_url()}/{output_filename}"
        return f"Successfully converted to Word.\nDownload Link: {download_url}\nLocal Path: {os.path.abspath(file_path)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def convert_markdown_to_pdf(markdown_text: str, output_filename: str) -> str:
    """
    Convert Markdown text to a PDF file and return download link.
    """
    try:
        if not output_filename.lower().endswith(".pdf"):
            output_filename += ".pdf"
        
        file_path = os.path.join(OUTPUT_DIR, output_filename)
        # Use pdflatex (provided by Nix texlive.combined.scheme-small)
        pypandoc.convert_text(markdown_text, 'pdf', format='md', outputfile=file_path, extra_args=['--pdf-engine=pdflatex'])
        
        download_url = f"{get_base_url()}/{output_filename}"
        return f"Successfully converted to PDF.\nDownload Link: {download_url}\nLocal Path: {os.path.abspath(file_path)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def convert_md_file_to_docx(input_file_path: str, output_filename: str = None) -> str:
    """
    Convert an existing Markdown file (.md) to a Word (.docx) file and return download link.
    """
    try:
        if not os.path.exists(input_file_path):
            return f"Error: File {input_file_path} not found."
            
        if output_filename is None:
            output_filename = os.path.splitext(os.path.basename(input_file_path))[0] + ".docx"
        elif not output_filename.lower().endswith(".docx"):
            output_filename += ".docx"

        file_path = os.path.join(OUTPUT_DIR, output_filename)
        pypandoc.convert_file(input_file_path, 'docx', outputfile=file_path)
        
        download_url = f"{get_base_url()}/{output_filename}"
        return f"Successfully converted file to Word.\nDownload Link: {download_url}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def convert_md_file_to_pdf(input_file_path: str, output_filename: str = None) -> str:
    """
    Convert an existing Markdown file (.md) to a PDF file and return download link.
    """
    try:
        if not os.path.exists(input_file_path):
            return f"Error: File {input_file_path} not found."
            
        if output_filename is None:
            output_filename = os.path.splitext(os.path.basename(input_file_path))[0] + ".pdf"
        elif not output_filename.lower().endswith(".pdf"):
            output_filename += ".pdf"

        file_path = os.path.join(OUTPUT_DIR, output_filename)
        pypandoc.convert_file(input_file_path, 'pdf', outputfile=file_path, extra_args=['--pdf-engine=pdflatex'])
        
        download_url = f"{get_base_url()}/{output_filename}"
        return f"Successfully converted file to PDF.\nDownload Link: {download_url}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import sys
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.requests import Request
    from starlette.staticfiles import StaticFiles

    transport_type = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport_type = "sse"
    
    if transport_type == "sse":
        transport = SseServerTransport("/md-to-word-mcpserver/messages")

        async def handle_sse(request: Request):
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await mcp._mcp_server.run(
                    streams[0], 
                    streams[1], 
                    mcp._mcp_server.create_initialization_options()
                )

        app = Starlette(routes=[
            Route("/md-to-word-mcpserver/sse", endpoint=handle_sse),
            Mount("/md-to-word-mcpserver/messages", app=transport.handle_post_message),
            # Mount the outputs directory to serve files for download
            Mount("/md-to-word-mcpserver/download", app=StaticFiles(directory=OUTPUT_DIR), name="download"),
        ])
        
        print(f"Starting Markdown MCP Server on http://0.0.0.0:1996/md-to-word-mcpserver/sse")
        print(f"Downloads will be available at http://<SERVER_IP>:1996/md-to-word-mcpserver/download/")
        uvicorn.run(app, host="0.0.0.0", port=1996)
    else:
        mcp.run(transport="stdio")
