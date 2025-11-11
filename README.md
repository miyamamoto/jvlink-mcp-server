# JVLink MCP Server

JVLinkToSQLiteで作成した競馬データベースにアクセスするためのMCPサーバー

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

## 前提条件

- **JVLinkToSQLiteで作成したデータベース**（必須）
  - 公式版: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
  - 拡張版: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)
- 対応DB: SQLite（デフォルト）、DuckDB、PostgreSQL

## インストール

### 方法1: ローカル環境

```bash
# リポジトリをクローン
git clone https://github.com/miyamamoto/jvlink-mcp-server.git
cd jvlink-mcp-server

# 環境変数を設定
export DB_TYPE=sqlite
export DB_PATH=~/JVData/race.db

# 接続テスト
uv run python -c "from jvlink_mcp_server.database import DatabaseConnection; db = DatabaseConnection(); print(db.get_tables())"
```

### 方法2: Docker（推奨）

```bash
# JVDataディレクトリを指定
export JVDATA_DIR=~/JVData

# イメージをビルドして起動
docker compose build
docker compose up jvlink-sqlite
```

アクセス: `http://localhost:8000/sse`

## Claude Desktopで使う

### 1. サーバーを起動

**Docker（推奨）:**
```bash
export JVDATA_DIR=~/JVData
docker compose up jvlink-sqlite
```

**ローカル環境:**
```bash
export DB_TYPE=sqlite
export DB_PATH=~/JVData/race.db
uv run python -m jvlink_mcp_server.server_sse
```

### 2. Claude Desktopに接続

`claude_desktop_config.json` に以下を追加：

```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Claude Desktopを再起動してください。

## よくある質問

**Q: データベースはどこで作る？**
A: JVLinkToSQLiteで作成してください。他のツールで作成したDBには対応していません。

**Q: DuckDBを使いたい**
A: 拡張版JVLinkToSQLiteでDBを作成し、`DB_TYPE=duckdb` に設定してください。

**Q: データが更新されない**
A: Dockerを使っている場合、`JVDATA_DIR`環境変数でJVLinkToSQLiteのディレクトリを直接マウントしてください。リアルタイムで反映されます。

## ライセンス

Apache License 2.0
