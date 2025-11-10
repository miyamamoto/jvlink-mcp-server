#!/bin/bash
# JVLink MCP Server - SSE mode startup script
cd "$(dirname "$0")"
uv run python -m jvlink_mcp_server.server_sse
