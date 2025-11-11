# 接続セットアップ

## 前提条件

- JVLinkToSQLiteで作成したデータベース
  - 公式版（SQLiteのみ）: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
  - 拡張版（SQLite/DuckDB/PostgreSQL）: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## 標準接続（API経由）

### 1. サーバー起動

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

### 2. Claude Desktop設定

`claude_desktop_config.json` に追加：

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

## リモート接続

リモートサーバーで起動する場合、ホスト名を変更してください：

```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://your-server-ip:8000/sse"
    }
  }
}
```

## セキュリティ注意

現在の実装は認証なしです。本番環境では以下を実装してください：
- 認証機能（API Key、Bearer Token）
- HTTPS/TLS
- ファイアウォール設定
- IPアドレス制限

## トラブルシューティング

**ポートが使用中**
- 別のポートに変更: `.env` で `MCP_PORT=8001`

**接続できない**
- サーバーが起動しているか確認
- Claude Desktopを再起動
