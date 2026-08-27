"""Stable jrvltsql 2.0.0 JRA storage contract.

The primary-key registry below is derived from the executable ``SCHEMAS``
mapping in jrvltsql v2.0.0 (tag target
``4d3a89b382bb0a0b788d68093bc16f0f8dd950f5``).  Keep this as the single
source used by all MCP schema-description surfaces.
"""

from pathlib import Path
import re
import sqlite3

JRVLTSQL_VERSION = "2.0.0"
JRVLTSQL_GIT_SHA = "4d3a89b382bb0a0b788d68093bc16f0f8dd950f5"

RACE = ("Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum")

# Columns read directly by the public high-level analysis APIs. Primary-key
# identity alone is insufficient for the automated upstream compatibility
# gate: a renamed result or grouping column would otherwise pass the gate and
# fail only after the generated support PR was merged.
JRVLTSQL_2_REQUIRED_COLUMNS: dict[str, dict[str, str]] = {
    "NL_RA": {
        "Year": "INTEGER",
        "MonthDay": "INTEGER",
        "JyoCD": "TEXT",
        "Kaiji": "INTEGER",
        "Nichiji": "INTEGER",
        "RaceNum": "INTEGER",
        "Hondai": "TEXT",
        "GradeCD": "TEXT",
        "Kyori": "INTEGER",
    },
    "NL_SE": {
        "Year": "INTEGER",
        "MonthDay": "INTEGER",
        "JyoCD": "TEXT",
        "Kaiji": "INTEGER",
        "Nichiji": "INTEGER",
        "RaceNum": "INTEGER",
        "Wakuban": "INTEGER",
        "Umaban": "INTEGER",
        "KettoNum": "TEXT",
        "Bamei": "TEXT",
        "KisyuRyakusyo": "TEXT",
        "KakuteiJyuni": "INTEGER",
        "Time": "REAL",
        "Ninki": "INTEGER",
    },
    "NL_UM": {
        "KettoNum": "TEXT",
        "Ketto3InfoBamei1": "TEXT",
    },
}

JRVLTSQL_2_PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "NL_AV": (*RACE, "Umaban"),
    "NL_BN": ("BanusiCode",),
    "NL_BR": ("BreederCode",),
    "NL_BT": ("HansyokuNum",),
    "NL_CC": RACE,
    "NL_CH": ("ChokyosiCode",),
    "NL_CH_SEISEKI": ("ChokyosiCode", "Num"),
    "NL_CK": (*RACE, "KettoNum"),
    "NL_CK_CHAKU": (*RACE, "KettoNum", "EntityKubun", "PeriodNum", "MetricKubun", "BucketNum"),
    "NL_CK_RUIKEI": (*RACE, "KettoNum", "EntityKubun", "PeriodNum"),
    "NL_CS": ("JyoCD", "Kyori", "TrackCD", "KaishuDate"),
    "NL_DM": (*RACE, "Umaban"),
    "NL_H1": (*RACE, "BetType", "Kumi"),
    "NL_H6": (*RACE, "SanrentanKumi"),
    "NL_HA": ("KaisaiDate", "JyoCD", "Kaiji", "Nichiji", "RaceNum"),
    "NL_HC": ("TresenKubun", "ChokyoDate", "ChokyoTime", "KettoNum"),
    "NL_HN": ("HansyokuNum",),
    "NL_HR": RACE,
    "NL_HS": ("KettoNum", "SaleCode", "FromDate"),
    "NL_HY": ("KettoNum",),
    "NL_JC": (*RACE, "HappyoTime", "Umaban"),
    "NL_JG": (*RACE, "KettoNum", "Num"),
    "NL_KS": ("KisyuCode",),
    "NL_KS_SEISEKI": ("KisyuCode", "Num"),
    "NL_NC": ("JyoCD",),
    "NL_NU": ("UmaID",),
    "NL_O1": (*RACE, "Umaban", "Kumi"),
    "NL_O2": (*RACE, "Kumi"),
    "NL_O3": (*RACE, "Kumi"),
    "NL_O4": (*RACE, "Kumi"),
    "NL_O5": (*RACE, "Kumi"),
    "NL_O6": (*RACE, "Kumi"),
    "NL_OA": ("KaisaiDate", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "OddsType", "Kumi"),
    "NL_RA": RACE,
    "NL_RC": ("RecInfoKubun", *RACE, "TokuNum", "SyubetuCD", "Kyori", "TrackCD"),
    "NL_SE": (*RACE, "Umaban", "KettoNum"),
    "NL_SK": ("KettoNum",),
    "NL_TC": RACE,
    "NL_TK": (*RACE, "RenbanNum"),
    "NL_TK_RACE": RACE,
    "NL_TM": (*RACE, "Umaban"),
    "NL_UM": ("KettoNum",),
    "NL_WC": ("TresenKubun", "ChokyoDate", "ChokyoTime", "KettoNum"),
    "NL_WE": ("Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "HappyoTime", "HenkoID"),
    "NL_WF": ("Year", "MonthDay"),
    "NL_WH": (*RACE, "Umaban"),
    "NL_YS": ("Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji"),
    "RT_AV": (*RACE, "Umaban"),
    "RT_CC": RACE,
    "RT_DM": (*RACE, "Umaban"),
    "RT_H1": (*RACE, "BetType", "Kumi"),
    "RT_H6": (*RACE, "SanrentanKumi"),
    "RT_HR": RACE,
    "RT_JC": (*RACE, "HappyoTime", "Umaban"),
    "RT_O1": (*RACE, "Umaban", "Kumi"),
    "RT_O2": (*RACE, "Kumi"),
    "RT_O3": (*RACE, "Kumi"),
    "RT_O4": (*RACE, "Kumi"),
    "RT_O5": (*RACE, "Kumi"),
    "RT_O6": (*RACE, "Kumi"),
    "RT_RA": RACE,
    "RT_RC": (*RACE, "Umaban"),
    "RT_SE": (*RACE, "Umaban", "KettoNum"),
    "RT_TC": RACE,
    "RT_TM": (*RACE, "Umaban"),
    "RT_WE": ("Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "HappyoTime", "HenkoID"),
    "RT_WF": ("Year", "MonthDay"),
    "RT_WH": (*RACE, "Umaban"),
    "TS_O1": (*RACE, "Umaban", "Kumi", "HassoTime"),
    "TS_O2": (*RACE, "Kumi", "HassoTime"),
    "TS_O3": (*RACE, "Kumi", "HassoTime"),
    "TS_O4": (*RACE, "Kumi", "HassoTime"),
    "TS_O5": (*RACE, "Kumi", "HassoTime"),
    "TS_O6": (*RACE, "Kumi", "HassoTime"),
    "TS_SOKUHO_O1": (*RACE, "Umaban", "Kumi", "HassoTime", "SourceSpec", "CollectedAt"),
    "TS_SOKUHO_O2": (*RACE, "Kumi", "HassoTime", "SourceSpec", "CollectedAt"),
    "TS_SOKUHO_O3": (*RACE, "Kumi", "HassoTime", "SourceSpec", "CollectedAt"),
    "TS_SOKUHO_O4": (*RACE, "Kumi", "HassoTime", "SourceSpec", "CollectedAt"),
    "TS_SOKUHO_O5": (*RACE, "Kumi", "HassoTime", "SourceSpec", "CollectedAt"),
    "TS_SOKUHO_O6": (*RACE, "Kumi", "HassoTime", "SourceSpec", "CollectedAt"),
}

JRVLTSQL_2_ADDITIONAL_TABLES = {
    "NL_CH_SEISEKI": "調教師成績明細",
    "NL_CK_CHAKU": "競走馬成績・着度数明細",
    "NL_CK_RUIKEI": "競走馬成績・累計明細",
    "NL_HA": "開催別票数情報",
    "NL_KS_SEISEKI": "騎手成績明細",
    "NL_NC": "競馬場マスタ",
    "NL_NU": "競走馬識別情報",
    "NL_OA": "開催別オッズ情報",
    "NL_TK_RACE": "特別登録レース情報",
    "RT_WF": "WIN5情報（速報）",
}


def apply_jrvltsql_2_contract(table_map: dict[str, dict]) -> None:
    """Add 2.0 tables and replace JRA primary keys in a public table map."""
    for table_name, primary_keys in JRVLTSQL_2_PRIMARY_KEYS.items():
        table_map.setdefault(
            table_name,
            {
                "description": JRVLTSQL_2_ADDITIONAL_TABLES.get(
                    table_name, f"jrvltsql 2.0 {table_name}テーブル"
                ),
                "key_columns": {},
            },
        )
        table_map[table_name]["primary_keys"] = list(primary_keys)


def validate_sqlite_schema(
    database_path: str | Path,
    expected: dict[str, tuple[str, ...]] | None = None,
) -> list[str]:
    """Return deterministic errors for a generated jrvltsql SQLite schema."""
    expected = expected or JRVLTSQL_2_PRIMARY_KEYS
    errors: list[str] = []
    uri = f"file:{Path(database_path).resolve()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        actual_tables = {
            row[0].casefold(): row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        for table_name, expected_key in expected.items():
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
                errors.append(f"invalid expected table identifier: {table_name!r}")
                continue
            actual_name = actual_tables.get(table_name.casefold())
            if actual_name is None:
                errors.append(f"{table_name}: table missing")
                continue
            rows = connection.execute(f'PRAGMA table_info("{actual_name}")').fetchall()
            actual_columns = {row[1].casefold(): (row[1], row[2].upper()) for row in rows}
            actual_key = [
                row[1]
                for row in sorted(rows, key=lambda row: row[5] or 10**6)
                if row[5]
            ]
            if actual_key != list(expected_key):
                errors.append(
                    f"{table_name}: primary key mismatch: "
                    f"expected {list(expected_key)!r}, got {actual_key!r}"
                )
            for column_name, expected_type in JRVLTSQL_2_REQUIRED_COLUMNS.get(
                table_name, {}
            ).items():
                actual_column = actual_columns.get(column_name.casefold())
                if actual_column is None:
                    errors.append(
                        f"{table_name}: required column missing: {column_name}"
                    )
                    continue
                actual_column_name, actual_type = actual_column
                if actual_type != expected_type:
                    errors.append(
                        f"{table_name}.{actual_column_name}: type mismatch: "
                        f"expected {expected_type}, got {actual_type or '<empty>'}"
                    )
    return errors
