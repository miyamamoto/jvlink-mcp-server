"""JVLink MCP Server - SSE (HTTP) mode for remote access"""
import os
from dotenv import load_dotenv
import uvicorn
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Import the MCP server instance
from .server import mcp

# Get server configuration
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8000"))


def run_sse_server():
    """Run MCP server in SSE mode with uvicorn"""
    # Get the ASGI app from FastMCP
    app = mcp.sse_app()

    print(f"Starting JVLink MCP Server (SSE mode)")
    print(f"  Host: {HOST}")
    print(f"  Port: {PORT}")
    print(f"  Endpoint: http://{HOST}:{PORT}/sse")
    print(f"  Database: {os.getenv('DB_TYPE', 'sqlite')} - {os.getenv('DB_PATH', 'N/A')}")

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )


if __name__ == "__main__":
    run_sse_server()
