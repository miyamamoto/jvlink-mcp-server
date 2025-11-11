# Docker セットアップ

## 前提条件

- Docker Desktop または Docker Engine
- JVLinkToSQLiteで作成したデータベース
  - 公式版（SQLiteのみ）: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
  - 拡張版（SQLite/DuckDB/PostgreSQL）: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## クイックスタート

### 1. サーバー起動

```bash
# JVDataディレクトリを環境変数で指定
export JVDATA_DIR=~/JVData                        # Linux/Mac
set JVDATA_DIR=C:\Users\<username>\JVData         # Windows

# イメージをビルド
docker compose build

# サーバー起動
docker compose up jvlink-sqlite
```

サーバーが起動したら `http://localhost:8000/sse` でアクセスできます。

**重要**: `JVDATA_DIR` にJVLinkToSQLiteが管理するディレクトリを指定してください。JVLinkToSQLiteでデータを更新すると即座に反映されます。

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

## イメージ

ビルドすると以下のイメージが作成されます：

```bash
docker images | grep jvlink-mcp-server
# jvlink-mcp-server:sqlite
# jvlink-mcp-server:duckdb
# jvlink-mcp-server:postgresql
```

## DuckDBを使う

```bash
export JVDATA_DIR=~/JVData
docker compose --profile duckdb up jvlink-duckdb
```

アクセス: `http://localhost:8001/sse`

## PostgreSQLを使う

```bash
docker compose --profile postgresql up
```

アクセス: `http://localhost:8002/sse`

## トラブルシューティング

**データベースが見つからない**
- `JVDATA_DIR` が正しく設定されているか確認
- JVLinkToSQLiteでデータベースを作成済みか確認

**ポートが使われている**
- `docker-compose.yml` のポート番号を変更してください

**JVLinkToSQLiteで更新したのに反映されない**
- `JVDATA_DIR` 環境変数が設定されているか確認
- JVLinkToSQLiteのデータディレクトリを直接マウントしてください
