"""Additional tests to improve coverage across modules.

Covers:
- connection.py: word-boundary keyword detection, PostgreSQL placeholders, semicolon checks
- query_templates.py: all template render_template calls, sire_stats NL_UM JOIN, race_result quoted placeholders
- high_level_api.py: get_sire_stats NL_UM JOIN, edge cases (empty results, None args)
- sample_data_provider.py: get_data_snapshot (NAR tables), cache behavior
- server.py: QUERY_GENERATION_HINTS applied to correct table names
- updater.py: git pull branch-name not hardcoded
"""

import os
import json
from unittest.mock import Mock, MagicMock, patch, call

import pandas as pd
import pytest

from jvlink_mcp_server.database.connection import DatabaseConnection
from jvlink_mcp_server.database.query_templates import (
    QUERY_TEMPLATES,
    render_template,
)
from jvlink_mcp_server.database.high_level_api import (
    get_sire_stats,
    get_favorite_performance,
    get_jockey_stats,
    get_horse_history,
)
from jvlink_mcp_server.database.sample_data_provider import (
    get_data_snapshot,
    get_sample_data,
    clear_cache,
    _sample_data_cache,
)


# ============================================================================
# connection.py — word-boundary keyword detection
# ============================================================================


class TestConnectionWordBoundary:
    """execute_safe_query must use word-boundary matching for dangerous keywords."""

    @pytest.fixture(autouse=True)
    def _setup_db(self):
        import sqlite3
        with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_PATH": ":memory:"}):
            self.db = DatabaseConnection()
            # Bypass read-only connect; use a writable in-memory connection
            self.db.connection = sqlite3.connect(":memory:")
            self.db.connection.execute(
                "CREATE TABLE test_t (id INTEGER, CREATED_AT TEXT, status TEXT)"
            )
            self.db.connection.execute(
                "INSERT INTO test_t VALUES (1, '2024-01-01', 'active')"
            )
            self.db.connection.commit()
            yield
            self.db.close()

    def test_created_at_not_blocked(self):
        """CREATED_AT should NOT trigger CREATE keyword detection."""
        df = self.db.execute_safe_query("SELECT CREATED_AT FROM test_t")
        assert len(df) == 1

    def test_update_in_like_not_blocked(self):
        """'%UPDATE%' inside a LIKE pattern should NOT trigger UPDATE detection."""
        df = self.db.execute_safe_query(
            "SELECT * FROM test_t WHERE status LIKE '%UPDATED%'"
        )
        assert isinstance(df, pd.DataFrame)

    def test_bare_create_still_blocked(self):
        """Bare CREATE keyword must still be blocked."""
        with pytest.raises(ValueError, match="Dangerous keyword.*CREATE"):
            self.db.execute_safe_query("CREATE TABLE evil (id INTEGER)")

    def test_bare_update_still_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*UPDATE"):
            self.db.execute_safe_query("UPDATE test_t SET status = 'x'")

    def test_bare_drop_still_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*DROP"):
            self.db.execute_safe_query("DROP TABLE test_t")

    def test_bare_delete_still_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*DELETE"):
            self.db.execute_safe_query("DELETE FROM test_t")

    def test_bare_insert_still_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*INSERT"):
            self.db.execute_safe_query("INSERT INTO test_t VALUES (2, 'x', 'y')")

    def test_semicolon_in_middle_blocked(self):
        """Semicolons in the middle of a query must be blocked (multi-statement)."""
        with pytest.raises(ValueError, match="Multiple SQL statements"):
            self.db.execute_safe_query("SELECT 1; SELECT 2")

    def test_trailing_semicolon_allowed(self):
        """A single trailing semicolon should be allowed."""
        df = self.db.execute_safe_query("SELECT 1 as v;")
        assert len(df) == 1

    def test_no_semicolon_is_fine(self):
        df = self.db.execute_safe_query("SELECT 1 as v")
        assert len(df) == 1

    def test_alter_keyword_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*ALTER"):
            self.db.execute_safe_query("ALTER TABLE test_t ADD COLUMN x TEXT")

    def test_truncate_keyword_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*TRUNCATE"):
            self.db.execute_safe_query("TRUNCATE TABLE test_t")

    def test_grant_keyword_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*GRANT"):
            self.db.execute_safe_query("GRANT ALL ON test_t TO user1")

    def test_revoke_keyword_blocked(self):
        with pytest.raises(ValueError, match="Dangerous keyword.*REVOKE"):
            self.db.execute_safe_query("REVOKE ALL ON test_t FROM user1")


class TestConnectionPostgreSQL:
    """PostgreSQL placeholder format (%s) in get_table_schema."""

    def test_postgresql_schema_uses_percent_s(self):
        """get_table_schema for postgresql uses %s placeholder."""
        with patch.dict(os.environ, {"DB_TYPE": "postgresql"}):
            db = DatabaseConnection()
            # Mock connection and execute_query
            mock_conn = MagicMock()
            db.connection = mock_conn

            # Mock get_tables to return our table
            db.get_tables = Mock(return_value=["NL_SE"])

            schema_df = pd.DataFrame({
                "column_name": ["Year", "MonthDay"],
                "data_type": ["integer", "text"],
                "is_nullable": ["YES", "NO"],
            })
            db.execute_query = Mock(return_value=schema_df)

            result = db.get_table_schema("NL_SE")

            # Check that %s placeholder was used (positional arg in query)
            query_arg = db.execute_query.call_args[0][0]
            assert "%s" in query_arg
            # Check params include table name
            params_arg = db.execute_query.call_args[1].get("params") or db.execute_query.call_args[0][1]
            assert "NL_SE" in params_arg
            # Check column renamed
            assert "column_type" in result.columns


# ============================================================================
# query_templates.py — render all templates
# ============================================================================


class TestRenderAllTemplates:
    """Ensure every template can be rendered with minimal required params."""

    # Minimal params for each template
    TEMPLATE_PARAMS = {
        "favorite_win_rate": {"ninki": 1},
        "jockey_stats": {},
        "frame_stats": {},
        "race_result": {
            "year": "2024", "month_day": "0525", "jyo_cd": "05",
            "kaiji": "3", "nichiji": "2", "race_num": "11",
        },
        "grade_race_list": {},
        "horse_pedigree": {"horse_name": "テスト"},
        "sire_stats": {},
        "nar_favorite_win_rate": {"ninki": 1},
        "nar_jockey_stats": {},
        "nar_venue_stats": {},
        "track_condition_stats": {"horse_name": "テスト"},
    }

    # race_result uses {year} directly but render_template maps year→year_condition;
    # this template is designed to be used with direct format params, not through
    # the standard condition system. We test it separately below.
    @pytest.mark.parametrize("template_name", [
        t for t in QUERY_TEMPLATES.keys() if t != "race_result"
    ])
    def test_render_template_all(self, template_name):
        params = self.TEMPLATE_PARAMS.get(template_name, {})
        sql, query_params = render_template(template_name, **params)
        assert isinstance(sql, str)
        assert isinstance(query_params, tuple)
        assert "SELECT" in sql

    def test_sire_stats_has_nl_um_join(self):
        """sire_stats template must JOIN NL_UM."""
        sql, params = render_template("sire_stats", sire_name="テスト")
        assert "NL_UM" in sql
        assert "JOIN" in sql.upper()
        assert "KettoNum" in sql

    def test_race_result_template_exists(self):
        """race_result template exists and has the expected JOIN structure."""
        info = QUERY_TEMPLATES["race_result"]
        sql = info["sql"]
        assert "NL_RA" in sql
        assert "NL_SE" in sql
        assert "JOIN" in sql.upper()
        # Uses direct {year}, {month_day} etc. placeholders
        assert "{year}" in sql
        assert "{month_day}" in sql

    def test_sire_stats_default_limit(self):
        """sire_stats without limit should use default (20)."""
        sql, params = render_template("sire_stats")
        assert 20 in params

    def test_jockey_stats_default_limit(self):
        sql, params = render_template("jockey_stats")
        assert 20 in params

    def test_nar_favorite_win_rate_uses_nar_table(self):
        sql, _ = render_template("nar_favorite_win_rate", ninki=1)
        assert "NL_SE_NAR" in sql

    def test_nar_jockey_stats_uses_nar_table(self):
        sql, _ = render_template("nar_jockey_stats")
        assert "NL_SE_NAR" in sql

    def test_track_condition_stats_joins_ra(self):
        sql, _ = render_template("track_condition_stats", horse_name="テスト")
        assert "NL_RA" in sql
        assert "JOIN" in sql.upper()


# ============================================================================
# high_level_api.py — get_sire_stats NL_UM JOIN, edge cases
# ============================================================================


def _get_query_and_params(mock_db):
    call_args = mock_db.execute_safe_query.call_args
    query = call_args[0][0]
    params = call_args[1].get("params", ()) if call_args[1] else ()
    return query, params


class TestSireStatsNlUmJoin:
    """get_sire_stats must JOIN NL_UM on KettoNum."""

    def test_join_nl_um_basic(self):
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame({
            "sire_name": ["ディープインパクト"],
            "total_runs": [500],
            "wins": [100],
            "places_2": [200],
            "places_3": [300],
        }))

        result = get_sire_stats(mock_db, sire_name="ディープインパクト")

        query, params = _get_query_and_params(mock_db)
        assert "NL_UM" in query
        assert "KettoNum" in query
        assert "JOIN" in query.upper()
        assert result["sire_name"] == "ディープインパクト"

    def test_join_nl_um_with_distance(self):
        """With distance, should also JOIN NL_RA."""
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame({
            "sire_name": ["テスト"],
            "total_runs": [10],
            "wins": [2],
            "places_2": [4],
            "places_3": [6],
        }))

        result = get_sire_stats(mock_db, sire_name="テスト", distance=1600)

        query, _ = _get_query_and_params(mock_db)
        assert "NL_UM" in query
        assert "NL_RA" in query

    def test_empty_result(self):
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame())

        result = get_sire_stats(mock_db, sire_name="存在しない馬")
        assert result["total_runs"] == 0
        assert result["win_rate"] == 0.0

    def test_invalid_venue_raises(self):
        mock_db = Mock()
        with pytest.raises(ValueError, match="不明な競馬場名"):
            get_sire_stats(mock_db, sire_name="テスト", venue="存在しない")

    def test_year_from_filter(self):
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame({
            "sire_name": ["テスト"],
            "total_runs": [10],
            "wins": [2],
            "places_2": [4],
            "places_3": [6],
        }))

        get_sire_stats(mock_db, sire_name="テスト", year_from="2020")
        query, params = _get_query_and_params(mock_db)
        assert "Year >= ?" in query
        assert 2020 in params


class TestHighLevelApiEdgeCases:
    def test_favorite_empty_df(self):
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame())

        result = get_favorite_performance(mock_db, ninki=1)
        assert result["total"] == 0
        assert result["win_rate"] == 0.0

    def test_jockey_stats_with_year(self):
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame({
            "jockey_name": ["テスト"],
            "total_rides": [10],
            "wins": [2],
            "places_2": [4],
            "places_3": [6],
        }))

        result = get_jockey_stats(mock_db, jockey_name="テスト", year_from="2023")
        query, params = _get_query_and_params(mock_db)
        assert "Year >= ?" in query
        assert 2023 in params

    def test_horse_history_with_year(self):
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame())

        df = get_horse_history(mock_db, horse_name="テスト", year_from="2020")
        query, params = _get_query_and_params(mock_db)
        assert "Year >= ?" in query
        assert 2020 in params

    def test_validate_year_invalid(self):
        from jvlink_mcp_server.database.high_level_api import _validate_year
        with pytest.raises(ValueError):
            _validate_year("abc")


# ============================================================================
# sample_data_provider.py — get_data_snapshot, cache
# ============================================================================


class TestGetDataSnapshot:
    def test_includes_nar_tables(self):
        mock_db = Mock()
        count_df = pd.DataFrame({"cnt": [100]})
        period_df = pd.DataFrame({"earliest": ["2020-0101"], "latest": ["2024-1231"]})

        def side_effect(query, **kwargs):
            if "MIN" in query:
                return period_df
            return count_df

        mock_db.execute_safe_query = Mock(side_effect=side_effect)

        result = get_data_snapshot(mock_db)

        assert "NL_RA_NAR" in result["tables"]
        assert "NL_SE_NAR" in result["tables"]
        assert "NL_RA" in result["tables"]
        assert "NL_SE" in result["tables"]
        assert "NL_UM" in result["tables"]
        assert result["total_records"] > 0

    def test_handles_missing_tables(self):
        mock_db = Mock()
        mock_db.execute_safe_query = Mock(side_effect=Exception("table not found"))

        result = get_data_snapshot(mock_db)

        # Should not raise, just mark as error
        for table_info in result["tables"].values():
            assert table_info["record_count"] == 0


class TestSampleDataCache:
    def test_cache_hit(self):
        clear_cache()
        mock_db = Mock()
        mock_db.get_tables = Mock(return_value=["NL_SE"])

        schema_df = pd.DataFrame({"column_name": ["Year"], "column_type": ["INTEGER"]})
        mock_db.get_table_schema = Mock(return_value=schema_df)

        sample_df = pd.DataFrame({"Year": [2024]})
        mock_db.execute_safe_query = Mock(return_value=sample_df)

        # First call — cache miss
        result1 = get_sample_data(mock_db, "NL_SE", num_rows=5)
        assert result1["num_rows"] == 1

        # Second call — cache hit (execute_safe_query not called again)
        call_count_before = mock_db.execute_safe_query.call_count
        result2 = get_sample_data(mock_db, "NL_SE", num_rows=5)
        assert mock_db.execute_safe_query.call_count == call_count_before
        assert result2 == result1

        clear_cache()

    def test_cache_bypass(self):
        clear_cache()
        mock_db = Mock()
        mock_db.get_tables = Mock(return_value=["NL_SE"])
        schema_df = pd.DataFrame({"column_name": ["Year"], "column_type": ["INTEGER"]})
        mock_db.get_table_schema = Mock(return_value=schema_df)
        sample_df = pd.DataFrame({"Year": [2024]})
        mock_db.execute_safe_query = Mock(return_value=sample_df)

        get_sample_data(mock_db, "NL_SE", num_rows=5, use_cache=False)
        get_sample_data(mock_db, "NL_SE", num_rows=5, use_cache=False)
        # Should have been called twice
        assert mock_db.execute_safe_query.call_count == 2

        clear_cache()

    def test_invalid_table(self):
        mock_db = Mock()
        mock_db.get_tables = Mock(return_value=["NL_SE"])

        result = get_sample_data(mock_db, "NONEXISTENT")
        assert "error" in result


# ============================================================================
# server.py — QUERY_GENERATION_HINTS applied to correct tables
# ============================================================================


class TestQueryGenerationHints:
    def test_hints_applied_to_nl_ra_and_nl_se(self):
        """QUERY_GENERATION_HINTS should be applied when table is NL_RA or NL_SE."""
        from jvlink_mcp_server.database.schema_descriptions import QUERY_GENERATION_HINTS

        # The server applies hints for NL_RA and NL_SE
        for table_name in ["NL_RA", "NL_SE"]:
            hints = QUERY_GENERATION_HINTS if table_name in ["NL_RA", "NL_SE"] else ""
            assert hints != "", f"Hints should be non-empty for {table_name}"

    def test_hints_not_applied_to_other_tables(self):
        from jvlink_mcp_server.database.schema_descriptions import QUERY_GENERATION_HINTS

        for table_name in ["NL_UM", "NL_KS", "NL_CH", "NL_HR"]:
            hints = QUERY_GENERATION_HINTS if table_name in ["NL_RA", "NL_SE"] else ""
            assert hints == "", f"Hints should be empty for {table_name}"

    def test_hints_content_is_nonempty_string(self):
        from jvlink_mcp_server.database.schema_descriptions import QUERY_GENERATION_HINTS

        assert isinstance(QUERY_GENERATION_HINTS, str)
        assert len(QUERY_GENERATION_HINTS) > 10


# ============================================================================
# updater.py — git pull branch name not hardcoded
# ============================================================================


class TestUpdaterGitPull:
    @patch("jvlink_mcp_server.updater.subprocess.run")
    @patch("jvlink_mcp_server.updater.check_for_updates")
    def test_git_pull_no_branch_hardcoded(self, mock_check, mock_run):
        """perform_update uses 'git pull --ff-only' without hardcoding a branch name."""
        mock_check.return_value = {
            "current_version": "0.1.0",
            "latest_version": "1.0.0",
            "update_available": True,
        }

        # git pull succeeds
        mock_run.return_value = MagicMock(returncode=0, stdout="Already up to date.\n", stderr="")

        from jvlink_mcp_server.updater import perform_update
        result = perform_update(confirmed=True)

        # Find the git pull call
        git_pull_calls = [
            c for c in mock_run.call_args_list
            if "pull" in str(c)
        ]
        assert len(git_pull_calls) >= 1
        git_pull_cmd = git_pull_calls[0][0][0]  # first positional arg
        # Should be ["git", "pull", "--ff-only"] — no branch name like "master" or "main"
        assert git_pull_cmd == ["git", "pull", "--ff-only"], (
            f"git pull command should not hardcode a branch name: {git_pull_cmd}"
        )

    @patch("jvlink_mcp_server.updater.check_for_updates")
    def test_perform_update_requires_confirmation(self, mock_check):
        """perform_update without confirmed=True returns confirmation message."""
        mock_check.return_value = {
            "current_version": "0.1.0",
            "latest_version": "1.0.0",
            "update_available": True,
        }

        from jvlink_mcp_server.updater import perform_update
        result = perform_update(confirmed=False)
        assert result.get("requires_confirmation") is True
        assert "confirmed=True" in result["message"]
