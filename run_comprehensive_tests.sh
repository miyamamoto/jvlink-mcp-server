#!/bin/bash
export DB_TYPE=duckdb
export DB_PATH=C:/Users/mitsu/JVData/race.duckdb
C:/Users/mitsu/.local/bin/uv.exe run python tests/comprehensive_query_patterns.py
