"""Tests for database connection module"""

import os
import pytest
from unittest.mock import patch
from jvlink_mcp_server.database.connection import DatabaseConnection


class TestDatabaseConnection:
    def test_default_db_type(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": "/tmp/test.db"}, clear=False):
            db = DatabaseConnection()
            assert db.db_type == "sqlite"

    def test_unsupported_db_type(self):
        with patch.dict(os.environ, {"DB_TYPE": "mysql"}, clear=False):
            db = DatabaseConnection()
            with pytest.raises(ValueError, match="Unsupported database type"):
                db.connect()

    def test_sqlite_no_path(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite"}, clear=False):
            os.environ.pop("DB_PATH", None)
            db = DatabaseConnection()
            with pytest.raises(ValueError, match="DB_PATH"):
                db.connect()

    def test_duckdb_no_path(self):
        with patch.dict(os.environ, {"DB_TYPE": "duckdb"}, clear=False):
            os.environ.pop("DB_PATH", None)
            db = DatabaseConnection()
            with pytest.raises(ValueError, match="DB_PATH"):
                db.connect()

    def test_safe_query_blocks_dangerous(self):
        """危険なクエリのブロック"""
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}, clear=False):
            db = DatabaseConnection()
            db.connect()
            try:
                for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE"]:
                    with pytest.raises(ValueError, match="Dangerous keyword"):
                        db.execute_safe_query(f"{keyword} TABLE test")
            finally:
                db.close()

    def test_context_manager(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}, clear=False):
            with DatabaseConnection() as db:
                assert db.connection is not None
            assert db.connection is None


class TestSQLiteConnection:
    """SQLiteの実際の接続テスト"""

    def test_sqlite_memory(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}, clear=False):
            with DatabaseConnection() as db:
                tables = db.get_tables()
                assert isinstance(tables, list)

    def test_execute_query(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}, clear=False):
            with DatabaseConnection() as db:
                df = db.execute_query("SELECT 1 as value")
                assert len(df) == 1
                assert df.iloc[0]["value"] == 1
