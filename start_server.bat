@echo off
echo Starting JVLink MCP Server (SSE mode)...
cd /d C:\Users\<username>\jvlink-mcp-server
C:\Users\<username>\.local\bin\uv.exe run python -m jvlink_mcp_server.server_sse
