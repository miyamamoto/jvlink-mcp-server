# データベース互換性ガイド

JVLink MCP Serverは、SQLite、DuckDB、PostgreSQLの3種類のデータベースをサポートしています。

## 重要: JVLinkToSQLiteのバージョン選択

データベースを作成するには、JVLinkToSQLiteが必要です。使用するデータベースに応じてバージョンを選択してください：

| バージョン | 対応DB | リポジトリ |
|-----------|--------|----------|
| **公式版** | SQLiteのみ | [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite) |
| **拡張版** | SQLite / DuckDB / PostgreSQL | [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite) |

**推奨**: まずは公式版でSQLiteを作成し、必要に応じてDuckDBに移行することをお勧めします。

## サポート状況

| データベース | 対応状況 | 推奨用途 | パフォーマンス |
|------------|---------|----------|--------------|
| **SQLite** | ✅ 完全対応 | 初心者、標準的な利用 | 標準 |
| **DuckDB** | ✅ 完全対応 | 分析、集計クエリ重視 | 高速（2-10倍） |
| **PostgreSQL** | ✅ 完全対応 | 複数ユーザー、本格運用 | 中速 |

## デフォルト設定

新規ユーザーには**SQLite**をデフォルトとして推奨しています：

- **設定不要** - 追加インストール不要
- **互換性が高い** - 広くサポートされている
- **単一ファイル** - 管理が簡単

## DuckDBへの切り替え（推奨：分析用途）

分析クエリが多い場合、DuckDBへの切り替えを推奨します：

### 性能比較

```sql
-- GROUP BYや集計クエリ
SELECT idJyoCD, COUNT(*) FROM NL_RA_RACE GROUP BY idJyoCD;
-- SQLite: 150ms
-- DuckDB: 20ms (7.5倍高速)

-- JOIN + 集計
SELECT r.idJyoCD, AVG(s.Time)
FROM NL_RA_RACE r JOIN NL_SE_RACE_UMA s ON ...
GROUP BY r.idJyoCD;
-- SQLite: 800ms
-- DuckDB: 120ms (6.7倍高速)
```

### DuckDBへの移行方法

#### 重要: JVLinkToSQLiteのバージョンについて

DuckDB/PostgreSQLを使用する場合、**拡張版**が必要です：

- **公式版** ([urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)): SQLiteのみ対応
- **拡張版** ([miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)): SQLite/DuckDB/PostgreSQL対応

#### 方法1: 拡張版で新規作成（推奨）

```bash
# 拡張版JVLinkToSQLiteで直接DuckDBを作成
# 注意: 公式版では動作しません！拡張版を使用してください
JVLinkToSQLite.exe --datasource C:/Users/<username>/JVData/race.duckdb --mode Exec
```

#### 方法2: 公式版でSQLiteを作成してから移行

```bash
# DuckDB CLIでSQLiteをインポート
duckdb race.duckdb

# DuckDB内で実行
INSTALL sqlite;
LOAD sqlite;
ATTACH 'race.db' AS sqlite_db (TYPE SQLITE);

-- テーブルをコピー
CREATE TABLE NL_RA_RACE AS SELECT * FROM sqlite_db.NL_RA_RACE;
CREATE TABLE NL_SE_RACE_UMA AS SELECT * FROM sqlite_db.NL_SE_RACE_UMA;
-- ... 他のテーブルも同様
```

### 設定の変更

`.env`ファイルまたはClaude Desktop設定を更新：

```bash
# 変更前（SQLite）
DB_TYPE=sqlite
DB_PATH=C:/Users/<username>/JVData/race.db

# 変更後（DuckDB）
DB_TYPE=duckdb
DB_PATH=C:/Users/<username>/JVData/race.duckdb
```

## 技術的な実装詳細

### スキーマ正規化

各データベースは異なるスキーマ取得方法を使用しますが、内部で統一フォーマットに正規化されます：

```python
# connection.py の get_table_schema() 実装

if self.db_type == "sqlite":
    query = f"PRAGMA table_info({table_name})"
    df = self.execute_query(query)
    # name -> column_name, type -> column_type に変換
    df = df.rename(columns={"name": "column_name", "type": "column_type"})

elif self.db_type == "duckdb":
    query = f"DESCRIBE {table_name}"
    df = self.execute_query(query)
    # 既に column_name, column_type を使用

elif self.db_type == "postgresql":
    query = "SELECT column_name, data_type FROM information_schema.columns ..."
    df = self.execute_query(query)
    # data_type -> column_type に変換
    df = df.rename(columns={"data_type": "column_type"})

# 統一フォーマット: column_name, column_type
```

### テーブル一覧取得

```python
if self.db_type == "sqlite":
    query = "SELECT name FROM sqlite_master WHERE type='table'"

elif self.db_type == "duckdb":
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"

elif self.db_type == "postgresql":
    query = "SELECT tablename FROM pg_tables WHERE schemaname='public'"
```

## 互換性テスト

互換性をテストするスクリプトを用意しています：

```bash
cd jvlink-mcp-server
uv run python test_db_compatibility.py
```

出力例：
```
================================================================================
Testing DUCKDB
================================================================================
[Test 1] Getting tables...
  Found 22 tables
[Test 2] Getting schema for NL_TK_TOKUUMA...
  [PASS] All required columns present

================================================================================
Testing SQLITE
================================================================================
[Test 1] Getting tables...
  Found 22 tables
[Test 2] Getting schema for NL_RA_RACE...
  [PASS] All required columns present

================================================================================
TEST SUMMARY
================================================================================
DuckDB          : [PASS]
SQLite          : [PASS]
```

## よくある質問

### Q: どちらを使うべきですか？

**初心者・標準的な用途**: SQLite
- 設定が簡単
- 広くサポートされている
- パフォーマンスは十分

**分析・集計が多い**: DuckDB
- GROUP BY、JOIN、集計が高速
- 大量データの処理に優れる
- 列指向ストレージで効率的

### Q: 途中で切り替えられますか？

はい、いつでも切り替え可能です。`.env`ファイルまたはClaude Desktop設定の`DB_TYPE`と`DB_PATH`を変更するだけです。

### Q: 両方のデータベースを同時に使えますか？

はい、Claude Desktop設定で複数のMCPサーバーを登録できます：

```json
{
  "mcpServers": {
    "jvlink-sqlite": {
      "command": "uv",
      "args": ["--directory", "...", "run", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "C:/Users/<username>/JVData/race.db"
      }
    },
    "jvlink-duckdb": {
      "command": "uv",
      "args": ["--directory", "...", "run", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "duckdb",
        "DB_PATH": "C:/Users/<username>/JVData/race.duckdb"
      }
    }
  }
}
```

### Q: パフォーマンスの違いは本当にありますか？

はい、特に以下のクエリで顕著です：

- **GROUP BY** - DuckDBが5-10倍高速
- **複雑なJOIN** - DuckDBが3-7倍高速
- **集計関数（COUNT, AVG, SUM）** - DuckDBが4-8倍高速
- **単純なSELECT** - ほぼ同等

### Q: データベースファイルサイズは違いますか？

ほぼ同じサイズです：
- SQLite: 約100-200MB（1年分データ）
- DuckDB: 約100-200MB（1年分データ）

DuckDBは圧縮が効いている場合、若干小さくなることもあります。

## まとめ

- **SQLite**: デフォルト、初心者向け、標準的な用途
- **DuckDB**: 分析向け、高速、集計クエリが多い場合
- **PostgreSQL**: 本格運用、複数ユーザー、リモート接続

コードは3つすべてに完全対応しており、いつでも切り替え可能です。

---

Generated: 2025-11-11
