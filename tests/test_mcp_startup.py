import sys
import os

# Set environment variables
os.environ['DB_TYPE'] = 'duckdb'
os.environ['DB_PATH'] = 'C:/Users/<username>/JVData/race.duckdb'

print("Starting MCP server test...", file=sys.stderr, flush=True)

try:
    from jvlink_mcp_server.server import mcp
    print(f"Server imported: {mcp.name}", file=sys.stderr, flush=True)
    
    print("Calling mcp.run()...", file=sys.stderr, flush=True)
    mcp.run()
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
