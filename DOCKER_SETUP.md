# Docker セットアップガイド

JVLink MCP ServerをDockerで実行するための完全ガイドです。

## 前提条件

- Docker Desktop (Windows/Mac) または Docker Engine (Linux)
- Docker Compose v2.0以降
- **重要**: JVLinkToSQLiteで作成した競馬データベース
  - このサーバーは**JVLinkToSQLiteが生成したデータベースのみ**に対応しています
  - 対応バージョン:
    - 公式版（SQLiteのみ）: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
    - 拡張版（SQLite/DuckDB/PostgreSQL）: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## 重要: リアルタイムDB更新対応

データベースはJVLinkToSQLiteによってリアルタイムで更新されます。そのため、**外部のデータベースディレクトリを直接マウント**します。

## クイックスタート

### 方法1: 外部DBディレクトリをマウント（推奨）

JVLinkToSQLiteが管理するディレクトリを直接マウントします：

```bash
# 1. 環境変数でJVDataディレクトリを指定
export JVDATA_DIR=C:/Users/<username>/JVData  # Windows
export JVDATA_DIR=~/JVData                     # Linux/Mac

# 2. Dockerイメージをビルド
docker compose build

# 3. サーバーを起動
docker compose up jvlink-sqlite

# 4. JVLinkToSQLiteでデータ更新すると即座に反映
```

**イメージ名**: `jvlink-mcp-server:sqlite`

サーバーが起動したら、`http://localhost:8000/sse` でアクセスできます。

### 方法2: docker-compose.ymlを直接編集

```yaml
services:
  jvlink-sqlite:
    image: jvlink-mcp-server:sqlite
    volumes:
      # JVLinkToSQLiteのデータディレクトリを直接マウント
      - C:/Users/<username>/JVData:/data:rw  # Windows
      # または
      - ~/JVData:/data:rw                    # Linux/Mac
```

### 方法3: DuckDBデータベース（高速分析）

```bash
# 環境変数設定
export JVDATA_DIR=~/JVData

# DuckDB版を起動
docker compose --profile duckdb up jvlink-duckdb
```

**イメージ名**: `jvlink-mcp-server:duckdb`

アクセス: `http://localhost:8001/sse`

### 方法4: PostgreSQL（本格運用）

PostgreSQLの場合、データはコンテナ内で管理されます：

```bash
# PostgreSQLコンテナとMCPサーバーを同時起動
docker compose --profile postgresql up
```

**イメージ名**: `jvlink-mcp-server:postgresql`

アクセス: `http://localhost:8002/sse`

**注意**: 初回起動時にPostgreSQLコンテナが起動するまで数秒かかります。

## Dockerイメージの詳細

### イメージ命名規則

すべてのイメージ名に **"mcp"** が含まれています：

- `jvlink-mcp-server:sqlite` - SQLite版
- `jvlink-mcp-server:duckdb` - DuckDB版
- `jvlink-mcp-server:postgresql` - PostgreSQL版

### イメージサイズ最適化

マルチステージビルドを採用し、最終イメージサイズを削減：

```dockerfile
# ビルダーステージ: 依存関係をインストール
FROM python:3.11-slim AS builder
RUN uv pip install --system -r pyproject.toml

# ランタイムステージ: 実行に必要な最小限のファイルのみ
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages ...
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
    image: jvlink-mcp-server:sqlite
    environment:
      - DB_TYPE=sqlite
      - DB_PATH=/data/race.db
    volumes:
      - ${JVDATA_DIR:-./data}:/data:rw
    ports:
      - "8000:8000"
```

**特徴**:
- 最もシンプルな構成
- JVLinkToSQLiteが管理する外部ディレクトリを直接マウント
- リアルタイムDB更新に対応
- ポート8000で公開

**起動方法**:
```bash
export JVDATA_DIR=~/JVData
docker compose up jvlink-sqlite
```

#### 2. jvlink-duckdb（分析用）

```yaml
services:
  jvlink-duckdb:
    image: jvlink-mcp-server:duckdb
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
- 外部DBディレクトリを直接マウント
- ポート8001で公開
- プロファイル指定が必要

**起動方法**:
```bash
export JVDATA_DIR=~/JVData
docker compose --profile duckdb up jvlink-duckdb
```

#### 3. jvlink-postgresql（本格運用）

```yaml
services:
  jvlink-postgresql:
    image: jvlink-mcp-server:postgresql
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

## ボリュームマウント（重要）

### リアルタイム更新対応の外部マウント

**推奨方法**: JVLinkToSQLiteが管理するディレクトリを直接マウント

```yaml
volumes:
  # 環境変数で指定（推奨）
  - ${JVDATA_DIR:-./data}:/data:rw

  # または直接指定
  - C:/Users/<username>/JVData:/data:rw  # Windows
  - ~/JVData:/data:rw                    # Linux/Mac
```

**利点**:
- JVLinkToSQLiteがデータを更新すると即座にMCPサーバーに反映
- コピー不要でディスク容量を節約
- `rw`（read-write）でデータベースファイルの読み書き可能

### ディレクトリ構造例

```
JVData/                       # JVLinkToSQLiteが管理
├── race.db                   # SQLiteデータベース
├── race.duckdb               # DuckDBデータベース
└── (JVLinkToSQLiteの設定ファイル等)
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

**原因**: マウントしたディレクトリにデータベースファイルが存在しない

**解決方法**:
```bash
# JVLinkToSQLiteでデータベースを作成
cd /path/to/JVLinkToSQLite
JVLinkToSQLite.exe --datasource ~/JVData/race.db --mode Exec

# マウントパスを確認
echo $JVDATA_DIR
ls -la $JVDATA_DIR/race.db
```

### エラー: Permission denied

**原因**: データベースファイルの権限が不足

**解決方法**:
```bash
# Linuxの場合、ファイル権限を変更
chmod 644 ~/JVData/race.db

# またはディレクトリ全体の権限を変更
chmod 755 ~/JVData/
```

### PostgreSQL接続エラー

**原因**: PostgreSQLコンテナが完全に起動する前に接続試行

**解決方法**:
- `depends_on`でヘルスチェックを使用（既に設定済み）
- 手動で待機: `docker compose up postgres` → 起動完了後 → `docker compose --profile postgresql up jvlink-postgresql`

### エラー: JVLinkToSQLiteで作成されたDBではない

**原因**: 他のツールで作成されたデータベースを使用しようとしている

**解決方法**:
- JVLinkToSQLite（公式版または拡張版）でデータベースを作成してください
- このサーバーは**JVLinkToSQLiteが生成したスキーマのみ**をサポートしています

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

JVDataディレクトリを直接バックアップ：

```bash
# ホストのJVDataディレクトリをバックアップ
cp -r ~/JVData ~/JVData_backup_$(date +%Y%m%d)

# または特定のDBファイルのみ
cp ~/JVData/race.db ~/JVData/race_backup_$(date +%Y%m%d).db
```

**注意**: コンテナを停止せずにバックアップ可能です（外部マウント方式のため）

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

### Q: JVLinkToSQLiteでデータを更新したら自動的に反映されますか？

A: はい、外部ディレクトリを直接マウントしているため、JVLinkToSQLiteがデータを更新すると即座にMCPサーバーに反映されます。コンテナの再起動は不要です。

```bash
# JVLinkToSQLiteでデータ更新（別ターミナル）
JVLinkToSQLite.exe --datasource ~/JVData/race.db --mode Exec

# MCPサーバーは自動的に最新データを参照
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

### Q: イメージ名を確認するには？

A:
```bash
# ビルドされたイメージ一覧
docker images | grep jvlink-mcp-server

# 出力例:
# jvlink-mcp-server   sqlite       xxx   xxx   xxxMB
# jvlink-mcp-server   duckdb       xxx   xxx   xxxMB
# jvlink-mcp-server   postgresql   xxx   xxx   xxxMB
```

### Q: JVLinkToSQLite以外で作成したDBは使えますか？

A: いいえ、このサーバーは**JVLinkToSQLiteが生成したデータベーススキーマのみ**をサポートしています。以下のバージョンで作成してください：

- 公式版（SQLiteのみ）: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
- 拡張版（SQLite/DuckDB/PostgreSQL）: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## 次のステップ

Dockerセットアップが完了したら：

1. [REMOTE_SETUP.md](REMOTE_SETUP.md) でリモート接続を設定
2. [SAMPLE_QUESTIONS.md](SAMPLE_QUESTIONS.md) でサンプル質問を試す
3. Claude DesktopでSSEエンドポイント（`http://localhost:8000/sse`）に接続

Docker環境での競馬データ分析を楽しんでください！

---

Generated: 2025-11-11
