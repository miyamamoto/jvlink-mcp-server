# JVLink MCP Server

TARGET frontier JV風の競馬分析MCPサーバー

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

## 概要

JVLink MCP Serverは、JVLinkToSQLiteで作成した競馬データベースにアクセスするためのModel Context Protocol (MCP)サーバーです。

**デフォルトデータベース**: SQLite（標準的、互換性が高い）

### サポートデータベース

- ✅ **SQLite** - 標準的、設定不要、単一ファイル
- ✅ **DuckDB** - 分析クエリが高速（集計・GROUP BYが2-10倍高速）
- ✅ **PostgreSQL** - 本格的なRDBMS、複数ユーザー対応

### JVLinkToSQLiteについて

データベースの作成には以下のいずれかを使用してください：

- **公式版** (SQLiteのみ): [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
- **拡張版** (SQLite/DuckDB/PostgreSQL対応): [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## データベースセットアップ

### ステップ1: JVLinkToSQLiteでSQLite作成

```bash
# SQLite形式で競馬データをインポート
JVLinkToSQLite.exe --datasource race.db --mode Exec
```

### ステップ2: 環境変数設定

`.env` ファイルを作成：

```bash
DB_TYPE=sqlite
DB_PATH=C:/Users/<username>/JVData/race.db
```

### ステップ3: 接続テスト

```bash
uv run python -c "from jvlink_mcp_server.database import DatabaseConnection; db = DatabaseConnection(); print(db.get_tables())"
```

## 使用方法

### Claude Desktopで使用

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/<username>/jvlink-mcp-server",
        "run",
        "python",
        "-m",
        "jvlink_mcp_server.server"
      ],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "C:/Users/<username>/JVData/race.db"
      }
    }
  }
}
```

## データベース互換性

SQLite、DuckDB、PostgreSQLの3種類に対応しています。

- SQLite: デフォルト、設定不要、初心者向け
- DuckDB: 分析クエリが高速（集計・GROUP BYが2-10倍高速）
- PostgreSQL: 本格運用、複数ユーザー対応

詳細は [DB_COMPATIBILITY.md](DB_COMPATIBILITY.md) を参照してください。

## Docker サポート

Dockerで簡単にデプロイできます：

```bash
# JVDataディレクトリを環境変数で指定
export JVDATA_DIR=C:/Users/<username>/JVData  # Windows
export JVDATA_DIR=~/JVData                     # Linux/Mac

# Dockerイメージをビルド
docker compose build

# サーバーを起動（JVLinkToSQLiteのDBを直接マウント）
docker compose up jvlink-sqlite
```

アクセス: `http://localhost:8000/sse`

**注意**: JVLinkToSQLiteで作成したデータベースのみ対応しています。

詳細は [DOCKER_SETUP.md](DOCKER_SETUP.md) を参照してください。

## ライセンス

Apache License 2.0
