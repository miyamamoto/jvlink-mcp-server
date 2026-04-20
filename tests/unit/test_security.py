"""Security tests: SQL injection prevention"""

import pytest
from unittest.mock import patch, MagicMock
import os

from jvlink_mcp_server.database.utils import validate_identifier


class TestValidateIdentifier:
    """validate_identifier のテスト"""

    def test_valid_table_names(self):
        assert validate_identifier("NL_SE") == "NL_SE"
        assert validate_identifier("NL_RA") == "NL_RA"
        assert validate_identifier("NL_UM") == "NL_UM"
        assert validate_identifier("my_table_123") == "my_table_123"
        assert validate_identifier("_private") == "_private"

    def test_valid_column_names(self):
        assert validate_identifier("KakuteiJyuni", "column name") == "KakuteiJyuni"
        assert validate_identifier("JyoCD", "column name") == "JyoCD"
        assert validate_identifier("Year", "column name") == "Year"

    def test_rejects_semicolon_injection(self):
        with pytest.raises(ValueError, match="Invalid table name"):
            validate_identifier("NL_SE; DROP TABLE NL_SE; --", "table name")

    def test_rejects_single_quote(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("'; DROP TABLE NL_SE; --")

    def test_rejects_space(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("NL SE")

    def test_rejects_hyphen(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("NL-SE")

    def test_rejects_dot_notation(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("main.NL_SE")

    def test_rejects_parentheses(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("NL_SE(1=1)")

    def test_rejects_comment_injection(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("NL_SE--")

    def test_rejects_union_injection(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("NL_SE UNION SELECT")

    def test_empty_string_rejected(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_identifier("")

    def test_error_message_includes_kind(self):
        with pytest.raises(ValueError, match="column name"):
            validate_identifier("bad col!", "column name")


class TestSafeQueryBlocking:
    """execute_safe_query の危険クエリブロックテスト"""

    def test_blocks_all_dangerous_keywords(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}):
            from jvlink_mcp_server.database.connection import DatabaseConnection
            db = DatabaseConnection()
            db.connect()
            try:
                dangerous = [
                    "DROP TABLE NL_SE",
                    "DELETE FROM NL_SE",
                    "UPDATE NL_SE SET x=1",
                    "INSERT INTO NL_SE VALUES(1)",
                    "CREATE TABLE hack(id INT)",
                    "ALTER TABLE NL_SE ADD col INT",
                    "TRUNCATE TABLE NL_SE",
                ]
                for stmt in dangerous:
                    with pytest.raises(ValueError, match="Dangerous keyword"):
                        db.execute_safe_query(stmt)
            finally:
                db.close()

    def test_allows_select(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}):
            from jvlink_mcp_server.database.connection import DatabaseConnection
            with DatabaseConnection() as db:
                df = db.execute_safe_query("SELECT 42 as answer")
                assert df.iloc[0]["answer"] == 42


class TestGetTableSchemaValidation:
    """get_table_schema がテーブル名を検証することを確認"""

    def test_rejects_injection_in_table_name(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}):
            from jvlink_mcp_server.database.connection import DatabaseConnection
            with DatabaseConnection() as db:
                with pytest.raises(ValueError, match="Invalid table name"):
                    db.get_table_schema("NL_SE; DROP TABLE NL_SE; --")

    def test_rejects_quote_in_table_name(self):
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}):
            from jvlink_mcp_server.database.connection import DatabaseConnection
            with DatabaseConnection() as db:
                with pytest.raises(ValueError, match="Invalid table name"):
                    db.get_table_schema("' OR '1'='1")


class TestSampleDataProviderValidation:
    """sample_data_provider の入力バリデーションテスト"""

    def test_get_sample_data_rejects_bad_table(self):
        from jvlink_mcp_server.database.sample_data_provider import get_sample_data
        mock_db = MagicMock()
        with pytest.raises(ValueError, match="Invalid table name"):
            get_sample_data(mock_db, "NL_SE; --")

    def test_get_column_examples_rejects_bad_table(self):
        from jvlink_mcp_server.database.sample_data_provider import get_column_value_examples
        mock_db = MagicMock()
        with pytest.raises(ValueError, match="Invalid table name"):
            get_column_value_examples(mock_db, "'; DROP TABLE--", "JyoCD")

    def test_get_column_examples_rejects_bad_column(self):
        from jvlink_mcp_server.database.sample_data_provider import get_column_value_examples
        mock_db = MagicMock()
        with pytest.raises(ValueError, match="Invalid column name"):
            get_column_value_examples(mock_db, "NL_SE", "'; DROP TABLE--")
