@echo off
cd /d C:\Users\<username>\jvlink-mcp-server
set DB_TYPE=duckdb
set DB_PATH=C:\Users\<username>\JVData\race.duckdb
C:\Users\<username>\.local\bin\uv.exe run python -m jvlink_mcp_server
