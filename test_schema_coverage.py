"""Test script to verify comprehensive schema description coverage"""

import sys
import os

# Set environment variables
os.environ.setdefault("DB_TYPE", "duckdb")
os.environ.setdefault("DB_PATH", "C:/Users/mitsu/JVData/race.duckdb")

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jvlink_mcp_server.database.schema_descriptions import get_column_description
from jvlink_mcp_server.database import DatabaseConnection

def test_schema_coverage():
    """Test that all columns have descriptions"""

    # Connect to database
    with DatabaseConnection() as db:
        # Get all tables
        tables_df = db.execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'")
        tables = tables_df["table_name"].tolist()

        print("=" * 80)
        print("JVLink Schema Coverage Test")
        print("=" * 80)

        total_columns = 0
        columns_with_manual_desc = 0
        columns_with_auto_desc = 0
        columns_without_desc = 0

        for table in tables:
            if not table.startswith("NL_"):
                continue

            schema_df = db.get_table_schema(table)
            table_columns = len(schema_df)
            total_columns += table_columns

            print(f"\n{table}: {table_columns} columns")
            print("-" * 80)

            # Process ALL columns for accurate statistics
            sample_display = min(5, table_columns)
            for i, row in schema_df.iterrows():
                col_name = row["column_name"]
                description = get_column_description(table, col_name)

                # Check if it's manual or auto-generated
                if description.startswith("（説明未登録:"):
                    columns_without_desc += 1
                    status = "[NO]"
                elif "=" in description or "形式" in description or "コード" in description:
                    columns_with_manual_desc += 1
                    status = "[MANUAL]"
                else:
                    columns_with_auto_desc += 1
                    status = "[AUTO]"

                # Only display first few for readability
                if i < sample_display:
                    print(f"  {status} {col_name:30} {description[:60]}")

            if table_columns > sample_display:
                print(f"  ... and {table_columns - sample_display} more columns")

        print("\n" + "=" * 80)
        print("Summary:")
        print("=" * 80)
        print(f"Total columns: {total_columns}")
        print(f"Manual descriptions: {columns_with_manual_desc} ({columns_with_manual_desc/total_columns*100:.1f}%)")
        print(f"Auto-generated: {columns_with_auto_desc} ({columns_with_auto_desc/total_columns*100:.1f}%)")
        print(f"No description: {columns_without_desc} ({columns_without_desc/total_columns*100:.1f}%)")
        print(f"\nCoverage: {(columns_with_manual_desc + columns_with_auto_desc)/total_columns*100:.1f}%")
        print("=" * 80)

if __name__ == "__main__":
    test_schema_coverage()
