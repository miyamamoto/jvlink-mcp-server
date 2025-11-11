# JVLink MCP Server

JVLinkToSQLiteで作成した競馬データベースにアクセスするためのMCPサーバー

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

## 前提条件

- **JVLinkToSQLiteで作成したデータベース**（必須）
  - 公式版（SQLiteのみ）: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
  - 拡張版（SQLite/DuckDB/PostgreSQL）: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)
  - **注意**: DuckDBやPostgreSQLを使いたい場合は拡張版が必要です
- 対応DB: SQLite（デフォルト）、DuckDB、PostgreSQL

### データベースに含まれるもの
- レース情報（開催日、競馬場、距離、馬場状態）
- 馬情報（馬名、血統、生年月日）
- 成績情報（着順、タイム、オッズ、人気）
- 騎手・調教師情報
- 約22テーブル、2GB〜50GB

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

## ドキュメント

- [データベースセットアップ](docs/DATABASE_SETUP.md)
- [Docker セットアップ](docs/DOCKER_SETUP.md)
- [Claude Desktop セットアップ](docs/CLAUDE_DESKTOP_SETUP.md)
- [接続セットアップ](docs/REMOTE_SETUP.md)
- [データベース互換性](docs/DB_COMPATIBILITY.md)
- [サンプル質問](docs/SAMPLE_QUESTIONS.md)
- [スキーマドキュメント](docs/SCHEMA_DOCUMENTATION.md)
- [スキーマカバレッジレポート](docs/SCHEMA_COVERAGE_REPORT.md)

## よくある質問

**Q: データベースはどこで作る？**
A: JVLinkToSQLiteで作成してください。他のツールで作成したDBには対応していません。

**Q: DuckDBを使いたい**
A: 拡張版JVLinkToSQLiteでDBを作成し、`DB_TYPE=duckdb` に設定してください。

**Q: データが更新されない**
A: Dockerを使っている場合、`JVDATA_DIR`環境変数でJVLinkToSQLiteのディレクトリを直接マウントしてください。リアルタイムで反映されます。

## ライセンス

Apache License 2.0
