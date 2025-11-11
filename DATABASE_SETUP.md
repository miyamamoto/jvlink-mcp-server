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

ビルド方法は各リポジトリのREADMEを参照してください。

## データベース作成

```bash
# ディレクトリ作成
mkdir ~/JVData

# データ取得
JVLinkToSQLite --datasource ~/JVData/race.db --mode Exec
```

データ取得には時間がかかります（数時間〜1日程度）。

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

`%APPDATA%\Claude\claude_desktop_config.json` に追加：

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
