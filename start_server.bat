@echo off
echo Starting JVLink MCP Server (SSE mode)...
cd /d C:\Users\mitsu\jvlink-mcp-server
C:\Users\mitsu\.local\bin\uv.exe run python -m jvlink_mcp_server.server_sse
