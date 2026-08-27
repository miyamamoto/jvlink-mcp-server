"""Database connection manager for JVLink databases"""

import json
import logging
import os
import re
from typing import Any, Optional
import warnings
import pandas as pd

from .jrvltsql_2_contract import JRVLTSQL_2_PRIMARY_KEYS
from .utils import (
    is_unsupported_nar_table_name,
    reject_unsupported_nar_table_reference,
    validate_identifier,
)

logger = logging.getLogger(__name__)

# Suppress pandas DuckDB connection warning
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy')


def _resolved_relation_names(plan, relation_keys: set[str]):
    """Yield physical relation names from an engine-produced JSON plan."""
    if isinstance(plan, dict):
        for key, value in plan.items():
            if key in relation_keys and isinstance(value, str):
                yield value
            yield from _resolved_relation_names(value, relation_keys)
    elif isinstance(plan, list):
        for value in plan:
            yield from _resolved_relation_names(value, relation_keys)


def _adapt_qmark_parameters(query: str) -> str:
    """Convert unquoted DB-API qmark placeholders to pg8000 format markers."""
    result = []
    quote = None
    dollar_quote = None
    index = 0
    while index < len(query):
        if dollar_quote:
            if query.startswith(dollar_quote, index):
                result.append(dollar_quote)
                index += len(dollar_quote)
                dollar_quote = None
            else:
                result.append(query[index])
                index += 1
            continue

        char = query[index]
        if quote:
            result.append(char)
            if char == quote:
                if index + 1 < len(query) and query[index + 1] == quote:
                    result.append(query[index + 1])
                    index += 1
                else:
                    quote = None
        elif char in ("'", '"'):
            quote = char
            result.append(char)
        elif char == "$":
            match = re.match(r"\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$", query[index:])
            if match:
                dollar_quote = match.group(0)
                result.append(dollar_quote)
                index += len(dollar_quote)
                continue
            result.append(char)
        elif char == "?":
            result.append("%s")
        else:
            result.append(char)
        index += 1
    return "".join(result)


class DatabaseConnection:
    """JVLinkデータベースへの接続を管理するクラス

    SQLite, DuckDB, PostgreSQLの3種類のデータベースに対応
    """

    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        self.db_path = os.getenv("DB_PATH")
        self.db_connection_string = os.getenv("DB_CONNECTION_STRING")
        self.connection = None

    def connect(self) -> Any:
        """データベースに接続"""
        if self.connection is not None:
            return self.connection

        logger.info(f"Connecting to {self.db_type} database...")

        if self.db_type == "sqlite":
            return self._connect_sqlite()
        elif self.db_type == "duckdb":
            return self._connect_duckdb()
        elif self.db_type == "postgresql":
            return self._connect_postgresql()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}. Supported: sqlite, duckdb, postgresql")

    def _connect_sqlite(self):
        """SQLiteに接続"""
        import sqlite3
        if not self.db_path:
            raise ValueError("DB_PATH environment variable not set for SQLite")
        self.connection = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)

        def authorize(action, first_arg, _second_arg, _database, _trigger):
            if (
                action == sqlite3.SQLITE_READ
                and isinstance(first_arg, str)
                and is_unsupported_nar_table_name(first_arg)
            ):
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        self.connection.set_authorizer(authorize)
        return self.connection

    def _connect_duckdb(self):
        """DuckDBに接続"""
        import duckdb
        if not self.db_path:
            raise ValueError("DB_PATH environment variable not set for DuckDB")
        self.connection = duckdb.connect(self.db_path, read_only=True)
        return self.connection

    def _connect_postgresql(self):
        """PostgreSQLに接続（pg8000を使用）"""
        import pg8000.dbapi
        
        # 環境変数から接続情報を取得
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        database = os.getenv("DB_NAME", "keiba")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", os.getenv("JVLINK_DB_PASSWORD", ""))
        
        # DB_CONNECTION_STRINGが設定されている場合はそちらを優先（後方互換性）
        if self.db_connection_string:
            # key=value形式のパース（セミコロン区切り対応、値にスペース含む場合も正しくパース）
            params = {}
            for part in self.db_connection_string.split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k.strip().lower()] = v.strip()
            host = params.get("host", host)
            port = int(params.get("port", port))
            database = params.get("database", params.get("dbname", database))
            user = params.get("username", params.get("user", user))
            password = params.get("password", password)
        
        self.connection = pg8000.dbapi.connect(
            host=host, port=port, database=database,
            user=user, password=password
        )
        # 読み取り専用モードに設定
        cursor = self.connection.cursor()
        cursor.execute("SET default_transaction_read_only = on")
        self.connection.commit()
        cursor.close()
        return self.connection

    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """SQLクエリを実行してDataFrameで結果を返す

        Args:
            query: 実行するSQLクエリ
            params: クエリパラメータ

        Returns:
            pandas DataFrame with query results
        """
        conn = self.connect()

        if self.db_type in ["sqlite", "duckdb"]:
            return pd.read_sql_query(query, conn, params=params)
        elif self.db_type == "postgresql":
            if params and "?" in query:
                query = _adapt_qmark_parameters(query)
            return pd.read_sql_query(query, conn, params=params)

    def execute_safe_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """安全なクエリのみ実行（読み取り専用）

        Args:
            query: 実行するSQLクエリ
            params: クエリパラメータ

        Returns:
            pandas DataFrame with query results

        Raises:
            ValueError: 危険なクエリが検出された場合
        """
        reject_unsupported_nar_table_reference(query)

        # 複文実行をブロック（セミコロンによる複数SQL文の実行を防止）
        if ';' in query.strip().rstrip(';'):
            raise ValueError("Multiple SQL statements are not allowed.")

        # 危険なキーワードをチェック
        dangerous_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER",
            "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE"
        ]

        query_upper = query.upper()
        import re
        for keyword in dangerous_keywords:
            # Use word boundary matching to avoid false positives
            # e.g. "CREATED_AT" should not trigger "CREATE", "Bamei LIKE '%UPDATE%'" should not trigger "UPDATE"
            if re.search(r'\b' + keyword + r'\b', query_upper):
                raise ValueError(f"Dangerous keyword '{keyword}' detected in query. Only SELECT queries are allowed.")

        self._assert_engine_provider_isolation(query, params)
        return self.execute_query(query, params=params)

    def _assert_engine_provider_isolation(
        self, query: str, params: Optional[tuple]
    ) -> None:
        """Ask the selected engine which physical relations the query binds."""
        connection = self.connect()
        relation_names = []

        if self.db_type == "sqlite":
            import sqlite3

            try:
                connection.execute(f"EXPLAIN QUERY PLAN {query}", params or ())
            except sqlite3.DatabaseError as exc:
                if "prohibited" in str(exc) or "not authorized" in str(exc):
                    raise ValueError(
                        "NAR tables are not supported by JVLink MCP Server."
                    ) from None
                raise
            return

        if self.db_type == "duckdb":
            rows = connection.execute(
                f"EXPLAIN (FORMAT JSON) {query}", params or ()
            ).fetchall()
            for row in rows:
                if len(row) > 1 and isinstance(row[1], str):
                    plan = json.loads(row[1])
                    relation_names.extend(
                        _resolved_relation_names(plan, {"Table"})
                    )

        elif self.db_type == "postgresql":
            explain_query = query
            if params and "?" in explain_query:
                explain_query = _adapt_qmark_parameters(explain_query)
            cursor = connection.cursor()
            try:
                if params:
                    cursor.execute(f"EXPLAIN (FORMAT JSON) {explain_query}", params)
                else:
                    cursor.execute(f"EXPLAIN (FORMAT JSON) {explain_query}")
                plan = cursor.fetchone()[0]
            finally:
                cursor.close()
            relation_names.extend(
                _resolved_relation_names(plan, {"Relation Name"})
            )

        if any(is_unsupported_nar_table_name(name) for name in relation_names):
            raise ValueError("NAR tables are not supported by JVLink MCP Server.")

    def get_tables(self) -> list[str]:
        """データベース内のテーブル一覧を取得"""
        conn = self.connect()

        if self.db_type == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table'"
        elif self.db_type == "duckdb":
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
        elif self.db_type == "postgresql":
            query = "SELECT tablename FROM pg_tables WHERE schemaname='public'"

        result = self.execute_query(query)
        physical_tables = {
            str(table).casefold(): str(table) for table in result.iloc[:, 0].tolist()
        }
        return [
            table_name
            for table_name in JRVLTSQL_2_PRIMARY_KEYS
            if table_name.casefold() in physical_tables
        ]

    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """テーブルのスキーマ情報を取得

        Args:
            table_name: テーブル名

        Returns:
            カラム情報を含むDataFrame (統一フォーマット: column_name, column_type)
        """
        validate_identifier(table_name, "table name")
        self.connect()

        supported_table_lookup = {
            name.casefold(): name for name in JRVLTSQL_2_PRIMARY_KEYS
        }
        canonical_table_name = supported_table_lookup.get(table_name.casefold())
        if canonical_table_name is None:
            raise ValueError(
                f"テーブル '{table_name}' は存在しません"
                "（not a supported JRA table）。"
            )

        # テーブル名のホワイトリスト検証
        valid_tables = self.get_tables()
        valid_table_lookup = {name.casefold(): name for name in valid_tables}
        actual_table_name = valid_table_lookup.get(canonical_table_name.casefold())
        if actual_table_name is None:
            raise ValueError(f"テーブル '{table_name}' は存在しません。有効なテーブル: {valid_tables}")

        if self.db_type == "sqlite":
            query = f"PRAGMA table_info({actual_table_name})"
            df = self.execute_query(query)
            df = df.rename(columns={"name": "column_name", "type": "column_type"})

        elif self.db_type == "duckdb":
            query = f"DESCRIBE {actual_table_name}"
            df = self.execute_query(query)

        elif self.db_type == "postgresql":
            query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """
            df = self.execute_query(query, params=(actual_table_name.lower(),))
            df = df.rename(columns={"data_type": "column_type"})

        return df

    def close(self):
        """データベース接続を閉じる"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """コンテキストマネージャーのエントリ"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーの終了"""
        self.close()
