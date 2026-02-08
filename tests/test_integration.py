"""Integration tests with real keiba.db

These tests require a real keiba.db at /tmp/keiba.db.
Skip if not available.
"""

import os
import pytest
from unittest.mock import patch

KEIBA_DB = "/tmp/keiba.db"
skip_no_db = pytest.mark.skipif(
    not os.path.exists(KEIBA_DB),
    reason=f"keiba.db not found at {KEIBA_DB}"
)


@skip_no_db
class TestIntegrationSQLite:
    """keiba.dbを使った統合テスト"""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": KEIBA_DB}, clear=False):
            yield

    def test_list_tables(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        with DatabaseConnection() as db:
            tables = db.get_tables()
            assert len(tables) > 0
            # 主要テーブルの存在確認
            assert "NL_SE" in tables or "NL_SE_RACE_UMA" in tables

    def test_get_table_schema(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        with DatabaseConnection() as db:
            tables = db.get_tables()
            nl_tables = [t for t in tables if t.startswith("NL_")]
            assert len(nl_tables) > 0
            schema = db.get_table_schema(nl_tables[0])
            assert "column_name" in schema.columns
            assert "column_type" in schema.columns

    def test_execute_safe_query(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        with DatabaseConnection() as db:
            tables = db.get_tables()
            if "NL_SE" in tables:
                df = db.execute_safe_query("SELECT COUNT(*) as cnt FROM NL_SE")
                assert df.iloc[0]["cnt"] > 0

    def test_favorite_performance(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        from jvlink_mcp_server.database.high_level_api import get_favorite_performance
        with DatabaseConnection() as db:
            result = get_favorite_performance(db, ninki=1)
            assert result["total"] > 0
            assert 0 <= result["win_rate"] <= 100

    def test_jockey_stats(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        from jvlink_mcp_server.database.high_level_api import get_jockey_stats
        with DatabaseConnection() as db:
            result = get_jockey_stats(db, jockey_name="ルメール")
            # ルメールのデータがあるかは不明だが、エラーなく実行できること
            assert isinstance(result, dict)
            assert "total_rides" in result

    def test_frame_stats(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        from jvlink_mcp_server.database.high_level_api import get_frame_stats
        with DatabaseConnection() as db:
            df = get_frame_stats(db)
            if not df.empty:
                assert "wakuban" in df.columns
                assert "win_rate" in df.columns

    def test_sample_data(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        from jvlink_mcp_server.database.sample_data_provider import get_sample_data
        with DatabaseConnection() as db:
            tables = db.get_tables()
            if "NL_SE" in tables:
                result = get_sample_data(db, "NL_SE", num_rows=3)
                assert result["num_rows"] <= 3
                assert len(result["sample_rows"]) <= 3

    def test_data_snapshot(self):
        from jvlink_mcp_server.database.connection import DatabaseConnection
        from jvlink_mcp_server.database.sample_data_provider import get_data_snapshot
        with DatabaseConnection() as db:
            result = get_data_snapshot(db)
            assert "tables" in result
            assert "total_records" in result
