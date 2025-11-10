# JVLink MCP Server - リモート接続セットアップガイド

## 概要

JVLink MCP Serverは**ローカル接続**と**リモート接続**の両方をサポートしています。

### 接続方式

| 方式 | プロトコル | 用途 | セキュリティ |
|------|-----------|------|-------------|
| **stdio** | 標準入出力 | ローカルのみ | プロセス分離 |
| **SSE** | HTTP/SSE | ローカル・リモート | 要認証実装 |

## ローカル接続（stdio）

### 起動方法

サーバーを起動せずに、Claude Desktopが自動起動します。

### Claude Desktop 設定

```json
{
  "mcpServers": {
    "jvlink-mcp-server": {
      "command": "C:/Users/mitsu/.local/bin/uv.exe",
      "args": [
        "--directory",
        "C:/Users/mitsu/jvlink-mcp-server",
        "run",
        "python",
        "-m",
        "jvlink_mcp_server"
      ],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "C:/Users/mitsu/JVData/race.db"
      }
    }
  }
}
```

## リモート接続（SSE）✨

### 1. サーバー起動

**Windowsの場合:**
```cmd
cd C:\Users\mitsu\jvlink-mcp-server
start_server.bat
```

**Linux/Mac の場合:**
```bash
cd /path/to/jvlink-mcp-server
./start_server.sh
```

**手動起動:**
```bash
uv run python -m jvlink_mcp_server.server_sse
```

### 2. サーバー設定（.env）

```bash
# Database configuration
DB_TYPE=sqlite
DB_PATH=C:/Users/mitsu/JVData/race.db

# MCP Server configuration
MCP_HOST=0.0.0.0    # リモートからアクセス可能にする場合
MCP_PORT=8000
```

### 3. Claude Desktop 設定

```json
{
  "mcpServers": {
    "jvlink-mcp-server": {
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

### 4. 動作確認

サーバーが起動していることを確認：

```bash
curl http://127.0.0.1:8000/sse
```

正常に接続されると、SSEストリームが開始されます。

## リモートサーバーへのデプロイ

### 設定例（リモートサーバー）

#### サーバー側 .env
```bash
DB_TYPE=sqlite
DB_PATH=/path/to/race.db
MCP_HOST=0.0.0.0    # 全IPから接続可能
MCP_PORT=8000
```

#### Claude Desktop 設定
```json
{
  "mcpServers": {
    "jvlink-mcp-server": {
      "url": "http://your-server-ip:8000/sse"
    }
  }
}
```

### セキュリティ注意事項 ⚠️

現在の実装は**認証なし**です。本番環境では以下の対策が必要です：

1. **認証の実装** - Bearer Token、API Key等
2. **HTTPS/TLS の使用** - Let's Encrypt等
3. **ファイアウォール設定** - 必要なポートのみ開放
4. **アクセス制御** - IPアドレス制限

## アーキテクチャ図

```
┌─────────────────┐
│ Claude Desktop  │
│   (ローカル)     │
└────────┬────────┘
         │ HTTP/SSE
         │ http://host:8000/sse
         ▼
┌─────────────────────────┐
│ JVLink MCP Server       │
│ (ローカル or リモート)    │
├─────────────────────────┤
│ - server_sse.py (SSE)   │
│ - server.py (stdio)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Database (SQLite/DuckDB)│
│ (ローカル or リモート)    │
└─────────────────────────┘
```

## 利用可能なMCPツール（12個）

1. `get_database_schema` - スキーマ情報
2. `get_query_examples` - クエリ例
3. `list_tables` - テーブル一覧
4. `get_table_info` - テーブル詳細
5. `get_important_features` - 重要特徴量
6. `get_feature_by_category` - カテゴリ別特徴量
7. `search_features` - 特徴量検索
8. `generate_sql_from_natural_language` - SQL生成
9. `execute_safe_query` - 安全なクエリ実行
10. `validate_sql_query` - クエリ検証
11. `search_races` - レース検索
12. `analyze_popularity_stats` - 人気別成績分析

## トラブルシューティング

### ポートが既に使用されている

```bash
# ポート8000を使用しているプロセスを確認
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac
```

.envファイルで別のポートを指定：
```bash
MCP_PORT=8001
```

### データベース接続エラー

.envファイルのDB_PATHが正しいか確認：
```bash
DB_PATH=C:/Users/mitsu/JVData/race.db  # Windowsの場合
DB_PATH=/path/to/race.db               # Linux/Macの場合
```

### Claude Desktopで接続できない

1. サーバーが起動しているか確認
2. ポートが開いているか確認
3. Claude Desktopを再起動
4. 設定ファイルのJSON文法を確認

## 今後の拡張予定

- [ ] 認証機能（API Key、Bearer Token）
- [ ] HTTPS/TLS サポート
- [ ] リクエストレート制限
- [ ] ログ記録と監視
- [ ] Docker対応
- [ ] Kubernetes対応
