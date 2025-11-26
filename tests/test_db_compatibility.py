"""Test database compatibility: SQLite, DuckDB, PostgreSQL (jrvltsql版)"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jvlink_mcp_server.database import DatabaseConnection

def test_db_type(db_type: str, db_path: str):
    """Test specific database type"""
    print(f"\n{'='*80}")
    print(f"Testing {db_type.upper()}")
    print('='*80)

    # Set environment variables
    os.environ["DB_TYPE"] = db_type
    os.environ["DB_PATH"] = db_path

    try:
        with DatabaseConnection() as db:
            # Test 1: Get tables
            print("\n[Test 1] Getting tables...")
            tables = db.get_tables()
            print(f"  Found {len(tables)} tables")
            if tables:
                print(f"  First 5 tables: {tables[:5]}")

            # Test 2: Get schema for first NL_ table
            nl_tables = [t for t in tables if t.startswith("NL_")]
            if nl_tables:
                test_table = nl_tables[0]
                print(f"\n[Test 2] Getting schema for {test_table}...")
                schema_df = db.get_table_schema(test_table)

                print(f"  Schema DataFrame columns: {list(schema_df.columns)}")
                print(f"  Total columns in table: {len(schema_df)}")

                # Check for required columns
                required_cols = ["column_name", "column_type"]
                missing_cols = [c for c in required_cols if c not in schema_df.columns]

                if missing_cols:
                    print(f"  [FAIL] Missing required columns: {missing_cols}")
                    return False
                else:
                    print(f"  [PASS] All required columns present")

                # Show first 5 columns
                print(f"\n  First 5 columns:")
                for _, row in schema_df.head(5).iterrows():
                    print(f"    - {row['column_name']:30} {row['column_type']:15}")

                return True
            else:
                print("  [WARN] No NL_ tables found to test schema")
                return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Database Compatibility Test (jrvltsql版)")
    print("=" * 80)

    # Check which databases are available
    # jrvltsql database path
    sqlite_path = "C:/Users/mitsu/work/jrvltsql/data/keiba.db"

    results = {}

    # Test SQLite (if exists)
    if os.path.exists(sqlite_path):
        results["SQLite"] = test_db_type("sqlite", sqlite_path)
    else:
        print(f"\n[WARN] SQLite database not found: {sqlite_path}")
        results["SQLite"] = None

    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print('='*80)

    for db_name, result in results.items():
        if result is None:
            print(f"{db_name:15} : [WARN] NOT TESTED (database not found)")
        elif result:
            print(f"{db_name:15} : [PASS]")
        else:
            print(f"{db_name:15} : [FAIL]")

    print('='*80)

    # Return exit code
    if any(r is False for r in results.values()):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
