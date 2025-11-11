# データベースセットアップ

## 前提条件

- JRA-VAN DataLab会員
- JVLinkToSQLiteをインストール済み
- ディスク空き容量 20GB以上

## JVLinkToSQLiteのインストール

**公式版（SQLiteのみ）:**
```bash
git clone https://github.com/urasandesu/JVLinkToSQLite.git
```

**拡張版（SQLite/DuckDB/PostgreSQL）:**
```bash
git clone https://github.com/miyamamoto/JVLinkToSQLite.git
```

**どちらを使う？**
- SQLiteのみ使用 → 公式版でOK
- **DuckDBやPostgreSQLを使いたい → 拡張版が必要**

ビルド方法は各リポジトリのREADMEを参照してください。

## データベース作成

```bash
# ディレクトリ作成
mkdir ~/JVData

# データ取得
JVLinkToSQLite --datasource ~/JVData/race.db --mode Exec
```

データ取得には時間がかかります（数時間〜1日程度）。

### ~/JVData/ ディレクトリの内容

データベース作成後、以下のファイルが生成されます：

```
~/JVData/
├── race.db              # SQLiteデータベース（公式版・拡張版）
├── race.duckdb          # DuckDBデータベース（拡張版のみ）
└── (JVLinkToSQLiteの設定・一時ファイル)
```

**race.db / race.duckdb の内容:**
- **レース情報**: 開催日、競馬場、距離、馬場状態など
- **馬情報**: 馬名、血統、生年月日など
- **成績情報**: 着順、タイム、オッズ、人気など
- **騎手・調教師情報**: 名前、所属、成績など
- **テーブル数**: 約22テーブル
- **データサイズ**: 2GB〜50GB（取得期間により変動）
  - 1年分: 約2-5GB
  - 3年分: 約5-15GB
  - 10年分: 約15-50GB

**重要**: このディレクトリはJVLinkToSQLiteが管理します。手動でファイルを編集・削除しないでください。

## JVLink MCP Serverのセットアップ

### ローカル環境

```bash
cd jvlink-mcp-server
export DB_TYPE=sqlite
export DB_PATH=~/JVData/race.db

# 接続テスト
uv run python -c "from jvlink_mcp_server.database import DatabaseConnection; db = DatabaseConnection(); print(db.get_tables())"
```

### Docker

```bash
export JVDATA_DIR=~/JVData
docker compose build
docker compose up jvlink-sqlite
```

アクセス: `http://localhost:8000/sse`

## Claude Desktopで使う

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

### 2. Claude Desktopに接続

`%APPDATA%\Claude\claude_desktop_config.json` に追加：

```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Claude Desktopを再起動して完了です。

## トラブルシューティング

**データベースが見つからない**
- パスを絶対パスで指定（`C:/Users/<username>/JVData/race.db`）
- スラッシュ `/` を使う（バックスラッシュ `\` はNG）

**テーブルが見つからない**
- JVLinkToSQLiteでデータ取得が完了しているか確認
- データベースファイルサイズが0バイトでないか確認

**Claude Desktopで接続できない**
- Claude Desktopを完全に再起動
- JSONの記法が正しいか確認
