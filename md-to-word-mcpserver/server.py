import os
import pypandoc
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# Initialize the MCP server
mcp = FastMCP("Markdown to Word & PDF Converter")

@mcp.tool()
def convert_markdown_to_docx(markdown_text: str, output_filename: str) -> str:
    """
    Convert Markdown text to a Microsoft Word (.docx) file.
    """
    try:
        if not output_filename.lower().endswith(".docx"):
            output_filename += ".docx"
        pypandoc.convert_text(markdown_text, 'docx', format='md', outputfile=output_filename)
        return f"Successfully converted to Word: {os.path.abspath(output_filename)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def convert_markdown_to_pdf(markdown_text: str, output_filename: str) -> str:
    """
    Convert Markdown text to a PDF file.
    """
    try:
        if not output_filename.lower().endswith(".pdf"):
            output_filename += ".pdf"
        
        # Use pdflatex (provided by Nix texlive.combined.scheme-small)
        pypandoc.convert_text(markdown_text, 'pdf', format='md', outputfile=output_filename, extra_args=['--pdf-engine=pdflatex'])
        
        return f"Successfully converted to PDF: {os.path.abspath(output_filename)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def convert_md_file_to_docx(input_file_path: str, output_file_path: str = None) -> str:
    """
    Convert an existing Markdown file (.md) to a Word (.docx) file.
    """
    try:
        if not os.path.exists(input_file_path):
            return f"Error: File {input_file_path} not found."
            
        if output_file_path is None:
            output_file_path = os.path.splitext(input_file_path)[0] + ".docx"
        elif not output_file_path.lower().endswith(".docx"):
            output_file_path += ".docx"

        pypandoc.convert_file(input_file_path, 'docx', outputfile=output_file_path)
        return f"Successfully converted file to Word: {os.path.abspath(output_file_path)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def convert_md_file_to_pdf(input_file_path: str, output_file_path: str = None) -> str:
    """
    Convert an existing Markdown file (.md) to a PDF file.
    """
    try:
        if not os.path.exists(input_file_path):
            return f"Error: File {input_file_path} not found."
            
        if output_file_path is None:
            output_file_path = os.path.splitext(input_file_path)[0] + ".pdf"
        elif not output_file_path.lower().endswith(".pdf"):
            output_file_path += ".pdf"

        pypandoc.convert_file(input_file_path, 'pdf', outputfile=output_file_path, extra_args=['--pdf-engine=pdflatex'])
        return f"Successfully converted file to PDF: {os.path.abspath(output_file_path)}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import sys
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.requests import Request

    # Check for transport type in command line arguments
    transport_type = "stdio"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--sse":
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
        ])
        
        print("Starting Markdown MCP Server on http://0.0.0.0:1996/md-to-word-mcpserver/sse")
        uvicorn.run(app, host="0.0.0.0", port=1996)
    else:
        mcp.run(transport="stdio")
