import os
import pypandoc
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Markdown to Word Converter")

@mcp.tool()
def convert_text_to_docx(markdown_text: str, output_filename: str) -> str:
    """
    Convert a string of Markdown text into a Word (.docx) file.
    The file will be saved in the current directory unless a path is provided.
    """
    try:
        if not output_filename.endswith(".docx"):
            output_filename += ".docx"
            
        # Convert text to docx using pandoc
        pypandoc.convert_text(markdown_text, 'docx', format='md', outputfile=output_filename)
        
        absolute_path = os.path.abspath(output_filename)
        return f"Successfully converted text to {absolute_path}"
    except Exception as e:
        return f"Error during conversion: {str(e)}"

@mcp.tool()
def convert_file_to_docx(input_file_path: str, output_file_path: str = None) -> str:
    """
    Convert an existing Markdown (.md) file to a Word (.docx) file.
    If output_file_path is not provided, it will use the same name as the input file.
    """
    try:
        if not os.path.exists(input_file_path):
            return f"Error: Input file '{input_file_path}' not found."

        if output_file_path is None:
            output_file_path = os.path.splitext(input_file_path)[0] + ".docx"
        elif not output_file_path.endswith(".docx"):
            output_file_path += ".docx"

        # Convert file to docx using pandoc
        pypandoc.convert_file(input_file_path, 'docx', outputfile=output_file_path)
        
        absolute_path = os.path.abspath(output_file_path)
        return f"Successfully converted '{input_file_path}' to '{absolute_path}'"
    except Exception as e:
        return f"Error during conversion: {str(e)}"

if __name__ == "__main__":
    import sys
    
    # Check for transport type in command line arguments
    transport_type = "stdio"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--sse":
            transport_type = "sse"
    
    if transport_type == "sse":
        # Configure host, port and endpoint path for n8n or network access
        # This will run a Starlette app on 0.0.0.0:1996
        # The endpoint will be http://<ip>:1996/md-to-word-mcpserver/sse
        mcp.run(
            transport="sse",
            host="0.0.0.0",
            port=1996,
            sse_path="/md-to-word-mcpserver/sse"
        )
    else:
        mcp.run(transport="stdio")
