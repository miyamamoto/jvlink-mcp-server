# リモート接続セットアップ

## 前提条件

- [jrvltsql](https://github.com/miyamamoto/jrvltsql) で作成した競馬データベース

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
export DB_PATH=~/JVData/keiba.db
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

## Mac / Linux からWindowsのデータベースに接続

JRA-VANのデータ取得（jrvltsql）はWindows専用ですが、データベースをMac/Linuxに持ってくればMCPサーバーは動作します。

### 方法1: SQLiteファイルをコピー

```
Windows                          Mac / Linux
┌─────────────┐                  ┌─────────────┐
│  jrvltsql   │                  │  keiba.db   │ ← コピー
│      ↓      │   ファイル共有    │      ↓      │
│  keiba.db   │ ───────────────▶ │ MCPサーバー  │
└─────────────┘   クラウド同期    │      ↓      │
                                 │Claude Desktop│
                                 └─────────────┘
```

Dropbox、Google Drive、USBメモリなどで`keiba.db`をコピーするだけ。
データ更新時は再度コピーが必要です。

### 方法2: PostgreSQL経由（リアルタイム更新）

```
Windows                          Mac / Linux
┌─────────────┐                  ┌─────────────┐
│  jrvltsql   │                  │ MCPサーバー  │
│      ↓      │    ネットワーク   │      ↓      │
│ PostgreSQL  │ ◀───────────────│Claude Desktop│
└─────────────┘                  └─────────────┘
```

jrvltsqlはPostgreSQLへの書き込みにも対応。
Mac/LinuxからWindowsのPostgreSQLに接続すればリアルタイムで最新データを利用できます。

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
