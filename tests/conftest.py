collect_ignore = [
    "test_mcp_startup.py",
    "test_db_compatibility.py",
    "test_mcp_schema.py",
    "test_schema_coverage.py",
    "test_missing_columns.py",
    "comprehensive_query_patterns.py",
    "test_query_patterns.py",
]

# Unit tests need no real DB; set safe defaults so imports don't crash.
import os
os.environ.setdefault("DB_TYPE", "sqlite")
os.environ.setdefault("DB_PATH", ":memory:")
