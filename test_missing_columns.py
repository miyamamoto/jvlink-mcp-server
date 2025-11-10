"""Test script to find columns without descriptions"""

import sys
import os

# Set environment variables
os.environ.setdefault("DB_TYPE", "duckdb")
os.environ.setdefault("DB_PATH", "C:/Users/<username>/JVData/race.duckdb")

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jvlink_mcp_server.database.schema_descriptions import get_column_description
from jvlink_mcp_server.database import DatabaseConnection

def find_missing_columns():
    """Find columns without descriptions"""

    with DatabaseConnection() as db:
        # Focus on tables with many columns
        main_tables = ["NL_CH_CHOKYOSI", "NL_KS_KISYU", "NL_HR_PAY", "NL_DM_INFO"]

        for table in main_tables:
            schema_df = db.get_table_schema(table)

            print(f"\n{'='*80}")
            print(f"{table}: Missing descriptions")
            print('='*80)

            missing = []
            for _, row in schema_df.iterrows():
                col_name = row["column_name"]
                description = get_column_description(table, col_name)

                if description.startswith("（説明未登録:"):
                    missing.append(col_name)

            print(f"Total missing: {len(missing)} / {len(schema_df)}")
            print("\nFirst 30 missing columns:")
            for col in missing[:30]:
                print(f"  - {col}")

if __name__ == "__main__":
    find_missing_columns()
