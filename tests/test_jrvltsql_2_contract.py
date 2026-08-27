"""Public contracts that must match the stable jrvltsql 2.0.0 schema."""

from pathlib import Path
import sqlite3
import json
import tomllib

import pytest

from jvlink_mcp_server.database.schema_descriptions import (
    TABLE_DESCRIPTIONS,
    get_column_description,
    get_table_description,
)
from jvlink_mcp_server.database.schema_info import (
    ALL_TABLES,
    JVLINK_TABLES,
    REALTIME_TABLES,
    TIMESERIES_TABLES,
)
from jvlink_mcp_server.database.jrvltsql_2_contract import (
    JRVLTSQL_VERSION,
    validate_sqlite_schema,
)


# Changed/high-risk keys independently extracted from jrvltsql v2.0.0
# (tag target 4d3a89b382bb0a0b788d68093bc16f0f8dd950f5).
EXPECTED_PRIMARY_KEYS = {
    "NL_SE": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban", "KettoNum"],
    "NL_TK": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "RenbanNum"],
    "NL_HS": ["KettoNum", "SaleCode", "FromDate"],
    "NL_HY": ["KettoNum"],
    "NL_O2": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Kumi"],
    "NL_H1": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "BetType", "Kumi"],
    "NL_H6": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "SanrentanKumi"],
    "NL_JC": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "HappyoTime", "Umaban"],
    "NL_WE": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "HappyoTime", "HenkoID"],
    "NL_CS": ["JyoCD", "Kyori", "TrackCD", "KaishuDate"],
    "RT_SE": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban", "KettoNum"],
    "RT_HR": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    "RT_O6": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Kumi"],
    "RT_JC": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "HappyoTime", "Umaban"],
    "TS_O6": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Kumi", "HassoTime"],
    "TS_SOKUHO_O6": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Kumi", "HassoTime", "SourceSpec", "CollectedAt"],
}


@pytest.mark.parametrize(("table_name", "expected"), EXPECTED_PRIMARY_KEYS.items())
def test_public_primary_keys_match_jrvltsql_2(table_name, expected):
    assert ALL_TABLES[table_name]["primary_keys"] == expected
    assert TABLE_DESCRIPTIONS[table_name]["primary_keys"] == expected


def test_schema_descriptions_accept_postgresql_identifier_case():
    assert get_table_description("nl_se") == get_table_description("NL_SE")
    assert get_column_description("nl_se", "kakuteijyuni") == get_column_description(
        "NL_SE", "KakuteiJyuni"
    )


def test_parent_sync_uses_pull_request_not_protected_branch_push():
    workflow = Path(".github/workflows/sync-parent.yml").read_text(encoding="utf-8")
    assert "git push origin HEAD:master" not in workflow
    assert "gh pr create" in workflow
    assert "gh release download" in workflow
    assert "uv pip install" in workflow
    for version_surface in (
        "manifest.json",
        "src/jvlink_mcp_server/__init__.py",
        "src/jvlink_mcp_server/database/jrvltsql_2_contract.py",
        "uv.lock",
    ):
        assert version_surface in workflow
    assert "uv lock" in workflow
    assert workflow.rfind("uv run pytest -q") > workflow.index("Prepare update tree")
    assert workflow.rfind("uv build") > workflow.index("Prepare update tree")


def test_family_maps_do_not_contain_tables_from_other_families():
    assert "RT_RA" not in JVLINK_TABLES
    assert "TS_O1" not in JVLINK_TABLES
    assert "NL_RA" not in REALTIME_TABLES
    assert "TS_O1" not in REALTIME_TABLES
    assert "NL_RA" not in TIMESERIES_TABLES
    assert "RT_RA" not in TIMESERIES_TABLES
    assert ALL_TABLES["NL_SE"]["description"] == JVLINK_TABLES["NL_SE"]["description"]


def test_public_docs_exclude_unconfirmed_result_rows_and_lint_clean_fence():
    query_surfaces = (
        "QUERY_GUIDELINES.md",
        "data/feature_importance.json",
        "src/jvlink_mcp_server/database/high_level_api.py",
        "src/jvlink_mcp_server/database/query_templates.py",
        "src/jvlink_mcp_server/database/sample_data_provider.py",
        "src/jvlink_mcp_server/database/schema_info.py",
    )
    setup = Path("docs/DATABASE_SETUP.md").read_text(encoding="utf-8")
    for query_surface in query_surfaces:
        contents = Path(query_surface).read_text(encoding="utf-8")
        assert "KakuteiJyuni IS NOT NULL" not in contents, query_surface

    feature_data = json.loads(
        Path("data/feature_importance.json").read_text(encoding="utf-8")
    )
    for feature in feature_data["important_features"]:
        sql_example = feature["sql_example"]
        if "SUM(CASE WHEN s.KakuteiJyuni = 1" in sql_example:
            assert "s.KakuteiJyuni > 0" in sql_example, feature["name"]
        elif "SUM(CASE WHEN KakuteiJyuni = 1" in sql_example:
            assert "KakuteiJyuni > 0" in sql_example, feature["name"]
    assert "```\nC:/Users/mitsu/work/jrvltsql" not in setup


def test_public_feature_examples_do_not_reference_retired_logical_tables():
    feature_data = Path("data/feature_importance.json").read_text(encoding="utf-8")
    for retired_name in ("NL_RA_RACE", "NL_RA_RACE_UMA", "NL_UM_UMA"):
        assert retired_name not in feature_data


def test_executable_python_does_not_reference_retired_logical_tables():
    repository_root = Path(__file__).parents[1]
    retired_names = (
        "NL_RA_RACE",
        "NL_RA_RACE_UMA",
        "NL_SE_RACE_UMA",
        "NL_UM_UMA",
        "idYear",
        "idMonthDay",
        "idJyoCD",
        "idKaiji",
        "idNichiji",
        "idRaceNum",
        "idUmaban",
        "headRecordSpec",
        "headDataKubun",
        "headMakeDate",
    )
    violations = []
    for path in repository_root.rglob("*.py"):
        if path == Path(__file__) or any(
            part in {".git", ".venv", "__pycache__"} for part in path.parts
        ):
            continue
        contents = path.read_text(encoding="utf-8")
        for retired_name in retired_names:
            if retired_name in contents:
                violations.append(f"{path.relative_to(repository_root)}: {retired_name}")

    assert violations == []


def test_upstream_schema_validator_can_reject_and_accept(tmp_path):
    database_path = tmp_path / "schema.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE TEST_TABLE (Year INTEGER PRIMARY KEY, KettoNum TEXT)"
        )

    expected = {"TEST_TABLE": ("Year", "KettoNum")}
    errors = validate_sqlite_schema(database_path, expected)
    assert errors == [
        "TEST_TABLE: primary key mismatch: expected ['Year', 'KettoNum'], got ['Year']"
    ]

    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TABLE TEST_TABLE")
        connection.execute(
            "CREATE TABLE TEST_TABLE (Year INTEGER, KettoNum TEXT, "
            "PRIMARY KEY (Year, KettoNum))"
        )

    assert validate_sqlite_schema(database_path, expected) == []


def test_upstream_schema_validator_rejects_required_non_key_drift(tmp_path):
    database_path = tmp_path / "required-columns.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE NL_SE (Year INTEGER PRIMARY KEY, KakuteiJyuni TEXT, "
            "Odds TEXT)"
        )

    errors = validate_sqlite_schema(database_path, {"NL_SE": ("Year",)})
    assert "NL_SE: required column missing: Ninki" in errors
    assert (
        "NL_SE.KakuteiJyuni: type mismatch: expected INTEGER, got TEXT" in errors
    )
    assert "NL_SE: required column missing: HaronTimeL3" in errors
    assert "NL_SE.Odds: type mismatch: expected REAL, got TEXT" in errors


def test_release_versions_and_upstream_lock_are_consistent():
    project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
    project_version = project["version"]
    manifest_version = json.loads(Path("manifest.json").read_text())["version"]
    package_init = Path("src/jvlink_mcp_server/__init__.py").read_text()
    assert manifest_version == project_version
    assert f'__version__ = "{project_version}"' in package_init
    assert Path(".github/jrvltsql_version.txt").read_text().strip() == (
        f"v{JRVLTSQL_VERSION}"
    )
    assert any(
        dependency.startswith("mcp[cli]>=1.21") and "<2" in dependency
        for dependency in project["dependencies"]
    )
