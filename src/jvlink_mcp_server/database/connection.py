"""Database connection manager for JVLink databases"""

import os
import sqlite3
from typing import Any, Optional
import pandas as pd


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

        if self.db_type == "sqlite":
            return self._connect_sqlite()
        elif self.db_type == "duckdb":
            return self._connect_duckdb()
        elif self.db_type == "postgresql":
            return self._connect_postgresql()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _connect_sqlite(self):
        """SQLiteに接続"""
        import sqlite3
        if not self.db_path:
            raise ValueError("DB_PATH environment variable not set for SQLite")
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def _connect_duckdb(self):
        """DuckDBに接続"""
        import duckdb
        if not self.db_path:
            raise ValueError("DB_PATH environment variable not set for DuckDB")
        self.connection = duckdb.connect(self.db_path)
        return self.connection

    def _connect_postgresql(self):
        """PostgreSQLに接続"""
        import psycopg2
        if not self.db_connection_string:
            raise ValueError("DB_CONNECTION_STRING environment variable not set for PostgreSQL")

        # パスワードを環境変数から取得
        password = os.getenv("JVLINK_DB_PASSWORD")
        if password and "Password=" not in self.db_connection_string:
            self.db_connection_string += f";Password={password}"

        self.connection = psycopg2.connect(self.db_connection_string)
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
            return pd.read_sql_query(query, conn, params=params)

    def execute_safe_query(self, query: str) -> pd.DataFrame:
        """安全なクエリのみ実行（読み取り専用）

        Args:
            query: 実行するSQLクエリ

        Returns:
            pandas DataFrame with query results

        Raises:
            ValueError: 危険なクエリが検出された場合
        """
        # 危険なキーワードをチェック
        dangerous_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER",
            "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE"
        ]

        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Dangerous keyword '{keyword}' detected in query. Only SELECT queries are allowed.")

        return self.execute_query(query)

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
        return result.iloc[:, 0].tolist()

    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """テーブルのスキーマ情報を取得

        Args:
            table_name: テーブル名

        Returns:
            カラム情報を含むDataFrame (統一フォーマット: column_name, column_type)
        """
        conn = self.connect()

        if self.db_type == "sqlite":
            query = f"PRAGMA table_info({table_name})"
            df = self.execute_query(query)
            # SQLiteの結果を統一フォーマットに変換: name -> column_name, type -> column_type
            df = df.rename(columns={"name": "column_name", "type": "column_type"})

        elif self.db_type == "duckdb":
            query = f"DESCRIBE {table_name}"
            df = self.execute_query(query)
            # DuckDBは既に column_name, column_type を使用しているのでそのまま

        elif self.db_type == "postgresql":
            query = f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
            """
            df = self.execute_query(query)
            # PostgreSQLの結果を統一フォーマットに変換: data_type -> column_type
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
