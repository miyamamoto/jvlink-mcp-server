# Claude Desktop セットアップ

## 設定ファイルの場所

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

ファイルが存在しない場合は新規作成してください。

## 基本設定

### SQLite（デフォルト）

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

### DuckDB

`DB_TYPE` と `DB_PATH` を変更：

```json
"env": {
  "DB_TYPE": "duckdb",
  "DB_PATH": "C:/Users/<username>/JVData/race.duckdb"
}
```

### PostgreSQL

```json
"env": {
  "DB_TYPE": "postgresql",
  "DB_CONNECTION_STRING": "Host=localhost;Database=jvlink;Username=jvlink_user",
  "JVLINK_DB_PASSWORD": "your_password"
}
```

## Dockerを使う場合

```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Dockerコンテナを起動してから使用してください。

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
