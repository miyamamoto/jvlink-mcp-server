# Claude Desktop セットアップ

## 前提条件

- JVLinkToSQLiteで作成したデータベース
  - 公式版（SQLiteのみ）: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
  - 拡張版（SQLite/DuckDB/PostgreSQL）: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## 設定ファイルの場所

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

ファイルが存在しない場合は新規作成してください。

## セットアップ手順

### 1. サーバー起動

#### Docker（推奨）

**SQLite:**
```bash
export JVDATA_DIR=~/JVData
docker compose up jvlink-sqlite
```

**DuckDB:**
```bash
export JVDATA_DIR=~/JVData
docker compose --profile duckdb up jvlink-duckdb
```

**PostgreSQL:**
```bash
docker compose --profile postgresql up
```

#### ローカル環境

**SQLite:**
```bash
export DB_TYPE=sqlite
export DB_PATH=~/JVData/race.db
uv run python -m jvlink_mcp_server.server_sse
```

**DuckDB:**
```bash
export DB_TYPE=duckdb
export DB_PATH=~/JVData/race.duckdb
uv run python -m jvlink_mcp_server.server_sse
```

### 2. Claude Desktop設定

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

**DuckDBの場合:** ポート8001
```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8001/sse"
    }
  }
}
```

**PostgreSQLの場合:** ポート8002
```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8002/sse"
    }
  }
}
```

## 確認

1. 設定ファイルを保存
2. Claude Desktopを完全に終了
3. Claude Desktopを再起動
4. 新しいチャットで「データベースのテーブル一覧を教えてください」と質問

テーブル一覧が表示されれば成功です。

## トラブルシューティング

**MCPサーバーが表示されない**
- JSONの記法が正しいか確認
- パスが正しいか確認（絶対パス、スラッシュ `/` 使用）
- Claude Desktopを完全に再起動

**接続エラー**
- データベースファイルが存在するか確認
- uvがインストールされているか確認
