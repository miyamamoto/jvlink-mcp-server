"""Test MCP server's get_table_info with comprehensive descriptions"""

import sys
import os
import json

# Set environment variables
os.environ.setdefault("DB_TYPE", "duckdb")
os.environ.setdefault("DB_PATH", "C:/Users/<username>/JVData/race.duckdb")

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jvlink_mcp_server.database.schema_descriptions import get_column_description, get_table_description
from jvlink_mcp_server.database import DatabaseConnection

def test_table_info():
    """Test table info generation with descriptions"""

    test_tables = ["NL_RA_RACE", "NL_SE_RACE_UMA", "NL_UM_UMA"]

    for table_name in test_tables:
        print(f"\n{'='*80}")
        print(f"Table: {table_name}")
        print('='*80)

        with DatabaseConnection() as db:
            schema_df = db.get_table_schema(table_name)

            # Get table description
            table_desc = get_table_description(table_name)
            print(f"\nTable Description: {table_desc.get('description', 'N/A')}")
            print(f"Target Equivalent: {table_desc.get('target_equivalent', 'N/A')}")
            print(f"Primary Keys: {table_desc.get('primary_keys', [])}")

            # Show first 10 columns with descriptions
            print(f"\nColumns ({len(schema_df)} total) - First 10:")
            print("-" * 80)

            for i, row in schema_df.head(10).iterrows():
                col_name = row["column_name"]
                col_type = row["column_type"]
                description = get_column_description(table_name, col_name)

                # Truncate long descriptions
                desc_display = description[:50] + "..." if len(description) > 50 else description
                print(f"  {col_name:30} {col_type:15} {desc_display}")

            # Count description coverage
            total = len(schema_df)
            with_desc = 0
            for _, row in schema_df.iterrows():
                desc = get_column_description(table_name, row["column_name"])
                if not desc.startswith("（説明未登録:"):
                    with_desc += 1

            coverage = (with_desc / total * 100) if total > 0 else 0
            print(f"\nCoverage: {with_desc}/{total} ({coverage:.1f}%)")

if __name__ == "__main__":
    test_table_info()
