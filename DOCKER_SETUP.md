# Docker セットアップガイド

JVLink MCP ServerをDockerで実行するための完全ガイドです。

## 前提条件

- Docker Desktop (Windows/Mac) または Docker Engine (Linux)
- Docker Compose v2.0以降
- 既存の競馬データベース（SQLite/DuckDB）またはPostgreSQLサーバー

## クイックスタート

### 方法1: SQLiteデータベース（最も簡単）

```bash
# 1. データディレクトリを作成
mkdir data

# 2. 既存のSQLiteデータベースをコピー
# Windows
copy C:\Users\<username>\JVData\race.db data\race.db

# macOS/Linux
cp ~/JVData/race.db data/race.db

# 3. Dockerイメージをビルド
docker compose build

# 4. サーバーを起動
docker compose up jvlink-sqlite
```

サーバーが起動したら、`http://localhost:8000/sse` でアクセスできます。

### 方法2: DuckDBデータベース（高速分析）

```bash
# DuckDBデータベースをコピー
cp ~/JVData/race.duckdb data/race.duckdb

# DuckDB版を起動
docker compose --profile duckdb up jvlink-duckdb
```

アクセス: `http://localhost:8001/sse`

### 方法3: PostgreSQL（本格運用）

```bash
# PostgreSQLコンテナとMCPサーバーを同時起動
docker compose --profile postgresql up
```

アクセス: `http://localhost:8002/sse`

**注意**: 初回起動時にPostgreSQLコンテナが起動するまで数秒かかります。

## Dockerイメージの詳細

### イメージサイズ最適化

マルチステージビルドを採用し、最終イメージサイズを削減：

```dockerfile
# ビルダーステージ: 依存関係をインストール
FROM python:3.11-slim AS builder
# ... dependencies installation

# ランタイムステージ: 実行に必要な最小限のファイルのみ
FROM python:3.11-slim
# ... copy only necessary files
```

### セキュリティ対策

- 非rootユーザー（`appuser`）で実行
- 最小限のシステムパッケージのみインストール
- 不要なファイルは`.dockerignore`で除外

### 環境変数

コンテナ内で使用できる環境変数：

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `DB_TYPE` | `sqlite` | データベースタイプ（sqlite/duckdb/postgresql） |
| `DB_PATH` | `/data/race.db` | データベースファイルパス（SQLite/DuckDB） |
| `DB_CONNECTION_STRING` | - | PostgreSQL接続文字列 |
| `JVLINK_DB_PASSWORD` | - | PostgreSQLパスワード |
| `MCP_HOST` | `0.0.0.0` | サーバーバインドアドレス |
| `MCP_PORT` | `8000` | サーバーポート |

## docker-compose.yml の詳細

### サービス一覧

#### 1. jvlink-sqlite（デフォルト）

```yaml
services:
  jvlink-sqlite:
    build: .
    environment:
      - DB_TYPE=sqlite
      - DB_PATH=/data/race.db
    volumes:
      - ./data:/data:rw
    ports:
      - "8000:8000"
```

**特徴**:
- 最もシンプルな構成
- ローカルのSQLiteファイルをマウント
- ポート8000で公開

**起動方法**:
```bash
docker compose up jvlink-sqlite
```

#### 2. jvlink-duckdb（分析用）

```yaml
services:
  jvlink-duckdb:
    environment:
      - DB_TYPE=duckdb
      - DB_PATH=/data/race.duckdb
    ports:
      - "8001:8001"
    profiles:
      - duckdb
```

**特徴**:
- DuckDBで高速な分析クエリ
- ポート8001で公開
- プロファイル指定が必要

**起動方法**:
```bash
docker compose --profile duckdb up jvlink-duckdb
```

#### 3. jvlink-postgresql（本格運用）

```yaml
services:
  jvlink-postgresql:
    environment:
      - DB_TYPE=postgresql
      - DB_CONNECTION_STRING=Host=postgres;Database=jvlink;Username=jvlink_user
    depends_on:
      postgres:
        condition: service_healthy
```

**特徴**:
- PostgreSQLコンテナと連携
- ヘルスチェックで起動順序を制御
- ポート8002で公開

**起動方法**:
```bash
docker compose --profile postgresql up
```

### プロファイル機能

Docker Composeのプロファイル機能を使用して、必要なサービスのみ起動：

```bash
# SQLiteのみ（デフォルト）
docker compose up

# DuckDBも起動
docker compose --profile duckdb up

# PostgreSQLも起動
docker compose --profile postgresql up

# すべて起動
docker compose --profile duckdb --profile postgresql up
```

## ボリュームマウント

### データディレクトリ

```yaml
volumes:
  - ./data:/data:rw
```

**説明**:
- ホストの`./data`ディレクトリをコンテナの`/data`にマウント
- `rw`（read-write）でデータベースファイルの読み書き可能

### 推奨ディレクトリ構造

```
jvlink-mcp-server/
├── data/
│   ├── race.db         # SQLiteデータベース
│   └── race.duckdb     # DuckDBデータベース
├── Dockerfile
├── docker-compose.yml
└── src/
```

## ネットワーク構成

```yaml
networks:
  jvlink-network:
    driver: bridge
```

すべてのサービスが`jvlink-network`に接続され、相互通信が可能：

- `jvlink-postgresql`サービスは`postgres`ホスト名でPostgreSQLにアクセス
- コンテナ間通信は内部ネットワークで高速

## 実行モード

### stdio モード（ローカル接続）

Claude Desktopなどのローカルクライアント向け：

```yaml
# docker-compose.ymlから command を削除
# または
command: python -m jvlink_mcp_server.server
```

**特徴**:
- 標準入出力でMCPプロトコル通信
- ポート公開不要
- Claude Desktop設定例:

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "docker",
      "args": ["exec", "-i", "jvlink-mcp-sqlite", "python", "-m", "jvlink_mcp_server.server"]
    }
  }
}
```

### SSE モード（リモート接続）

HTTPエンドポイントでリモートアクセス：

```yaml
command: python -m jvlink_mcp_server.server_sse
```

**特徴**:
- HTTP経由でMCPプロトコル通信
- ポート公開が必要
- ブラウザからアクセス可能

## トラブルシューティング

### エラー: Cannot connect to the Docker daemon

**原因**: Docker Desktopが起動していない

**解決方法**:
1. Docker Desktopを起動
2. 右下のトレイアイコンでDocker稼働確認

### エラー: Bind for 0.0.0.0:8000 failed: port is already allocated

**原因**: ポート8000が既に使用中

**解決方法**:
```yaml
# docker-compose.ymlのポート番号を変更
ports:
  - "8080:8000"  # ホスト側を8080に変更
```

### エラー: database file not found

**原因**: データベースファイルが`./data`ディレクトリに存在しない

**解決方法**:
```bash
# データベースファイルを正しい場所にコピー
cp /path/to/race.db data/race.db

# またはボリュームマウントパスを変更
volumes:
  - C:/Users/mitsu/JVData:/data:rw
```

### エラー: Permission denied

**原因**: データベースファイルの権限が不足

**解決方法**:
```bash
# Linuxの場合、ファイル権限を変更
chmod 644 data/race.db

# またはディレクトリ全体の権限を変更
chmod 755 data/
```

### PostgreSQL接続エラー

**原因**: PostgreSQLコンテナが完全に起動する前に接続試行

**解決方法**:
- `depends_on`でヘルスチェックを使用（既に設定済み）
- 手動で待機: `docker compose up postgres` → 起動完了後 → `docker compose --profile postgresql up jvlink-postgresql`

## 本番環境での運用

### 推奨設定

```yaml
services:
  jvlink-sqlite:
    restart: always  # 自動再起動
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### リバースプロキシ（Nginx）

```nginx
# nginx.conf
upstream jvlink {
    server localhost:8000;
}

server {
    listen 80;
    server_name jvlink.example.com;

    location / {
        proxy_pass http://jvlink;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### HTTPS対応（Let's Encrypt）

```bash
# Certbotで証明書取得
certbot --nginx -d jvlink.example.com
```

## データベースバックアップ

### SQLite/DuckDB

```bash
# コンテナからホストにコピー
docker compose cp jvlink-sqlite:/data/race.db ./backup/race_$(date +%Y%m%d).db

# または直接ホストのdataディレクトリをバックアップ
cp -r data/ backup_$(date +%Y%m%d)/
```

### PostgreSQL

```bash
# pg_dumpでバックアップ
docker compose exec postgres pg_dump -U jvlink_user jvlink > backup.sql

# リストア
docker compose exec -T postgres psql -U jvlink_user jvlink < backup.sql
```

## パフォーマンスチューニング

### メモリ制限

```yaml
services:
  jvlink-sqlite:
    mem_limit: 2g
    mem_reservation: 1g
```

### CPU制限

```yaml
services:
  jvlink-sqlite:
    cpus: "2.0"
```

### PostgreSQL最適化

```yaml
services:
  postgres:
    environment:
      - POSTGRES_SHARED_BUFFERS=256MB
      - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
      - POSTGRES_WORK_MEM=16MB
    shm_size: 256mb
```

## よくある質問（FAQ）

### Q: 複数のデータベースを同時に使えますか？

A: はい、プロファイル機能で複数サービスを同時起動できます：

```bash
docker compose --profile duckdb up
```

これでSQLite（ポート8000）とDuckDB（ポート8001）が両方起動します。

### Q: Docker内のデータベースファイルを更新するには？

A: ホストの`./data`ディレクトリに新しいファイルをコピーするだけです：

```bash
# コンテナを停止
docker compose down

# データベースを更新
cp ~/JVData/race.db data/race.db

# 再起動
docker compose up
```

### Q: ログを確認するには？

A:
```bash
# リアルタイムログ
docker compose logs -f jvlink-sqlite

# 過去のログ
docker compose logs --tail=100 jvlink-sqlite
```

### Q: コンテナ内でシェルを実行するには？

A:
```bash
docker compose exec jvlink-sqlite /bin/bash
```

### Q: イメージサイズを小さくするには？

A: 既にマルチステージビルドで最適化済みですが、さらに削減したい場合：

```dockerfile
# Alpine Linuxベースを使用
FROM python:3.11-alpine AS builder
```

ただし、一部ライブラリ（psycopg2など）のビルドに追加パッケージが必要になる可能性があります。

## 次のステップ

Dockerセットアップが完了したら：

1. [REMOTE_SETUP.md](REMOTE_SETUP.md) でリモート接続を設定
2. [SAMPLE_QUESTIONS.md](SAMPLE_QUESTIONS.md) でサンプル質問を試す
3. Claude DesktopでSSEエンドポイント（`http://localhost:8000/sse`）に接続

Docker環境での競馬データ分析を楽しんでください！

---

Generated: 2025-11-11
