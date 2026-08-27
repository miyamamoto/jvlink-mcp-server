"""Public-surface contract: JVLink MCP Server supports JRA only."""

import os
import sqlite3
from unittest.mock import patch

import pytest

from jvlink_mcp_server import server
from jvlink_mcp_server.database import high_level_api, query_templates, schema_info
from jvlink_mcp_server.database.connection import DatabaseConnection
from jvlink_mcp_server.database.utils import reject_unsupported_nar_table_reference


def test_nar_support_is_not_exposed() -> None:
    """NAR belongs to a separate provider and must not leak into this MCP."""
    tool_names = set(server.mcp._tool_manager._tools)
    resource_uris = {str(uri) for uri in server.mcp._resource_manager._resources}

    assert not {name for name in tool_names if name.startswith("nar_")}
    assert not {uri for uri in resource_uris if "nar" in uri.casefold()}
    assert not {
        name for name in query_templates.QUERY_TEMPLATES if name.startswith("nar_")
    }
    assert not {
        name
        for name in schema_info.ALL_TABLES
        if name.endswith("_NAR") or name.startswith("NAR_")
    }
    assert not hasattr(high_level_api, "get_nar_favorite_performance")
    assert not hasattr(high_level_api, "get_nar_jockey_stats")
    assert not hasattr(high_level_api, "get_nar_horse_history")


def test_nar_physical_tables_are_not_accessible_through_generic_tools(tmp_path) -> None:
    database_path = tmp_path / "mixed-provider.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE NL_RA (Year INTEGER)")
        connection.execute("CREATE TABLE NL_RA_NAR (Year TEXT)")

    with patch.dict(
        os.environ,
        {"DB_TYPE": "sqlite", "DB_PATH": str(database_path)},
        clear=False,
    ):
        with DatabaseConnection() as database:
            assert database.get_tables() == ["NL_RA"]
            assert database.execute_safe_query("SELECT COUNT(*) FROM NL_RA").iloc[0, 0] == 0
            assert database.execute_safe_query(
                "SELECT 'NL_RA_NAR' AS source FROM NL_RA"
            ).empty
            assert database.execute_safe_query(
                "SELECT COUNT(*) FROM NL_RA -- NL_RA_NAR is unsupported"
            ).iloc[0, 0] == 0
            assert database.execute_safe_query(
                "SELECT COUNT(*) AS NL_RA_NAR FROM NL_RA"
            ).iloc[0, 0] == 0
            with pytest.raises(ValueError, match="not a supported JRA table"):
                database.get_table_schema("NL_RA_NAR")
            with pytest.raises(ValueError, match="NAR tables are not supported"):
                database.execute_safe_query("SELECT COUNT(*) FROM NL_RA_NAR")

    validation = server.validate_sql_query("SELECT COUNT(*) FROM NL_RA_NAR")
    assert validation["can_execute"] is False
    assert validation["unsupported_provider_table"] is True
    assert "NAR" in validation["recommendation"]

    literal_validation = server.validate_sql_query(
        "SELECT 'NL_RA_NAR' AS source FROM NL_RA"
    )
    assert literal_validation["can_execute"] is True
    assert literal_validation["unsupported_provider_table"] is False

    with pytest.raises(ValueError, match="NAR tables are not supported"):
        reject_unsupported_nar_table_reference(
            "SELECT COUNT(*) FROM /* outer /* nested */ still outer */ NL_RA_NAR"
        )
    with pytest.raises(ValueError, match="NAR tables are not supported"):
        reject_unsupported_nar_table_reference("TABLE NL_RA_NAR")

    table_validation = server.validate_sql_query("TABLE NL_RA_NAR")
    assert table_validation["unsupported_provider_table"] is True
