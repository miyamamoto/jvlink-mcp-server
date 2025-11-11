# リモート接続セットアップ

## 前提条件

- JVLinkToSQLiteで作成したデータベース
  - 公式版（SQLiteのみ）: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
  - 拡張版（SQLite/DuckDB/PostgreSQL）: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## ローカル接続（stdio）

Claude Desktopが自動起動します。設定不要。

`claude_desktop_config.json`:
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

## リモート接続（SSE）

### サーバー起動

```bash
# ローカル環境
cd /path/to/jvlink-mcp-server
uv run python -m jvlink_mcp_server.server_sse

# Docker（推奨）
export JVDATA_DIR=~/JVData
docker compose up jvlink-sqlite
```

### Claude Desktop設定

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
