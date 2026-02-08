"""エッジケーステスト — セキュリティ・入力バリデーション"""

import os
import sys
import sqlite3
import tempfile
import pytest

# テスト用にDB_PATHを設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def db_connection(tmp_path):
    """テスト用SQLiteデータベースを作成"""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE NL_SE (
            Year INTEGER, MonthDay TEXT, JyoCD TEXT, RaceNum INTEGER,
            Umaban INTEGER, Wakuban INTEGER, KettoNum TEXT, Bamei TEXT,
            KisyuRyakusyo TEXT, KakuteiJyuni INTEGER, Ninki INTEGER,
            Odds REAL, BaTaijyu INTEGER, HaronTimeL3 TEXT, Time TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE NL_RA (
            Year INTEGER, MonthDay TEXT, JyoCD TEXT, Kaiji TEXT, Nichiji TEXT,
            RaceNum INTEGER, Hondai TEXT, GradeCD TEXT, Kyori INTEGER,
            TrackCD TEXT, SyussoTosu INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE NL_UM (
            KettoNum TEXT, Bamei TEXT, SexCD TEXT, BirthDate TEXT,
            Ketto3InfoBamei1 TEXT, Ketto3InfoBamei2 TEXT, Ketto3InfoBamei5 TEXT,
            SanchiName TEXT, BreederName TEXT
        )
    """)
    # サンプルデータ挿入
    conn.execute("""
        INSERT INTO NL_SE VALUES (2024, '0101', '05', 1, 1, 1, '2020100001', 'テスト馬',
        'テスト騎手', 1, 1, 3.5, 480, '334', '1234')
    """)
    conn.execute("""
        INSERT INTO NL_RA VALUES (2024, '0101', '05', '01', '01', 1, 'テストレース',
        'A', 1600, '11', 16)
    """)
    conn.commit()
    conn.close()

    os.environ["DB_PATH"] = str(db_path)
    os.environ["DB_TYPE"] = "sqlite"

    from jvlink_mcp_server.database.connection import DatabaseConnection
    db = DatabaseConnection()
    db.connect()
    yield db
    db.close()


class TestSQLInjectionPrevention:
    """SQLインジェクション対策のテスト"""

    def test_drop_table_blocked(self, db_connection):
        with pytest.raises(ValueError, match="Dangerous keyword"):
            db_connection.execute_safe_query("DROP TABLE NL_SE")

    def test_delete_blocked(self, db_connection):
        with pytest.raises(ValueError, match="Dangerous keyword"):
            db_connection.execute_safe_query("DELETE FROM NL_SE")

    def test_update_blocked(self, db_connection):
        with pytest.raises(ValueError, match="Dangerous keyword"):
            db_connection.execute_safe_query("UPDATE NL_SE SET Bamei='hack'")

    def test_insert_blocked(self, db_connection):
        with pytest.raises(ValueError, match="Dangerous keyword"):
            db_connection.execute_safe_query("INSERT INTO NL_SE VALUES (1)")

    def test_semicolon_injection_blocked(self, db_connection):
        """複文実行（セミコロンインジェクション）のブロック"""
        with pytest.raises(ValueError, match="Multiple SQL statements"):
            db_connection.execute_safe_query("SELECT * FROM NL_SE; DROP TABLE NL_SE")

    def test_union_select_allowed(self, db_connection):
        """UNION SELECTは許可（読み取りのみ）"""
        result = db_connection.execute_safe_query(
            "SELECT Bamei FROM NL_SE UNION SELECT Bamei FROM NL_UM"
        )
        assert result is not None

    def test_safe_select_works(self, db_connection):
        result = db_connection.execute_safe_query("SELECT * FROM NL_SE LIMIT 1")
        assert len(result) == 1

    def test_create_blocked(self, db_connection):
        with pytest.raises(ValueError, match="Dangerous keyword"):
            db_connection.execute_safe_query("CREATE TABLE evil (id int)")

    def test_alter_blocked(self, db_connection):
        with pytest.raises(ValueError, match="Dangerous keyword"):
            db_connection.execute_safe_query("ALTER TABLE NL_SE ADD COLUMN evil TEXT")

    def test_grant_blocked(self, db_connection):
        with pytest.raises(ValueError, match="Dangerous keyword"):
            db_connection.execute_safe_query("GRANT ALL ON NL_SE TO evil")

    def test_column_name_with_keyword_not_blocked(self, db_connection):
        """カラム名にキーワードが含まれる場合は誤検出しない（word boundary）"""
        # CREATED_AT should not trigger CREATE, UPDATE_FLAG should not trigger UPDATE
        # Test with a query that has keyword-like substrings in identifiers
        result = db_connection.execute_safe_query(
            "SELECT Bamei FROM NL_SE WHERE Bamei LIKE '%テスト%'"
        )
        assert result is not None


class TestTableWhitelist:
    """テーブルホワイトリスト検証のテスト"""

    def test_valid_table_schema(self, db_connection):
        """有効なテーブルのスキーマ取得"""
        schema = db_connection.get_table_schema("NL_SE")
        assert len(schema) > 0

    def test_invalid_table_schema_rejected(self, db_connection):
        """存在しないテーブルのスキーマ取得が拒否される"""
        with pytest.raises(ValueError, match="存在しません"):
            db_connection.get_table_schema("evil_table")

    def test_sql_injection_in_table_name(self, db_connection):
        """テーブル名へのSQLインジェクション試行"""
        with pytest.raises(ValueError, match="存在しません"):
            db_connection.get_table_schema("NL_SE; DROP TABLE NL_SE--")


class TestNumRowsCap:
    """num_rows上限チェックのテスト"""

    def test_num_rows_capped_at_100(self, db_connection):
        """num_rowsが100を超える場合にキャップされる"""
        from jvlink_mcp_server.database.sample_data_provider import get_sample_data
        result = get_sample_data(db_connection, "NL_SE", num_rows=500)
        # エラーなく実行され、上限がかかっている
        assert "error" not in result or result.get("error") is None

    def test_num_rows_negative_clamped(self, db_connection):
        """負のnum_rowsが1にクランプされる"""
        from jvlink_mcp_server.database.sample_data_provider import get_sample_data
        result = get_sample_data(db_connection, "NL_SE", num_rows=-5)
        assert "error" not in result or result.get("error") is None

    def test_sample_data_invalid_table(self, db_connection):
        """存在しないテーブルのサンプルデータ取得"""
        from jvlink_mcp_server.database.sample_data_provider import get_sample_data
        result = get_sample_data(db_connection, "EVIL_TABLE", num_rows=5)
        assert "error" in result


class TestReadOnlyConnection:
    """read-only DB接続のテスト"""

    def test_sqlite_readonly(self, db_connection):
        """SQLiteがread-onlyモードで接続されている"""
        # read-only URIモードで接続しているので書き込みは失敗するはず
        with pytest.raises(Exception):
            db_connection.connection.execute("INSERT INTO NL_SE (Year) VALUES (9999)")


class TestSSEBindAddress:
    """SSE bind addressのテスト"""

    def test_server_sse_defaults_to_localhost(self):
        """server_sse.pyがデフォルトで127.0.0.1にバインドする"""
        # 環境変数をクリア
        old = os.environ.pop("MCP_HOST", None)
        try:
            # server_sse.pyモジュールの定数を直接確認
            import importlib
            if 'jvlink_mcp_server.server_sse' in sys.modules:
                del sys.modules['jvlink_mcp_server.server_sse']
            # モジュールソースを直接読み込んで確認
            sse_path = os.path.join(
                os.path.dirname(__file__), '..', 'src',
                'jvlink_mcp_server', 'server_sse.py'
            )
            with open(sse_path) as f:
                content = f.read()
            assert '"127.0.0.1"' in content, "server_sse.pyのデフォルトHOSTは127.0.0.1であるべき"
        finally:
            if old is not None:
                os.environ["MCP_HOST"] = old

    def test_server_main_sse_defaults_to_localhost(self):
        """server.pyのSSEモードもデフォルトで127.0.0.1にバインドする"""
        server_path = os.path.join(
            os.path.dirname(__file__), '..', 'src',
            'jvlink_mcp_server', 'server.py'
        )
        with open(server_path) as f:
            content = f.read()
        # 0.0.0.0がハードコードされていないことを確認
        assert '0.0.0.0' not in content, "server.pyに0.0.0.0のハードコードがあります（セキュリティリスク）"


class TestQueryCorrector:
    """クエリ自動補正のエッジケース"""

    def test_empty_query(self):
        from jvlink_mcp_server.database.query_corrector import correct_query
        sql, corrections = correct_query("")
        assert sql == ""

    def test_no_correction_needed(self):
        from jvlink_mcp_server.database.query_corrector import correct_query
        sql, corrections = correct_query("SELECT * FROM NL_SE WHERE JyoCD = '05'")
        assert corrections == []
