# JVLink MCP Server

TARGET frontier JV風の競馬分析MCPサーバー

## 概要

JVLink MCP Serverは、[JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)で作成した競馬データベース（SQLite/DuckDB/PostgreSQL）にアクセスするためのModel Context Protocol (MCP)サーバーです。

TARGET frontier JVの機能を参考に、競馬データの検索・分析・予測に必要な機能を提供します。

## 主な機能

### 1. データベーススキーマ情報
- テーブル一覧取得
- スキーマ情報取得
- TARGET frontier JVとの対応表

### 2. 特徴量知見提供
- 20種類以上の重要特徴量の説明
- 各特徴量の統計的影響
- TARGET frontier JVでの活用方法
- 特徴量の組み合わせパターン

### 3. 自然言語SQL生成
- 自然言語からSQLクエリを動的生成
- 安全なクエリ実行（読み取り専用）
- SQLクエリの検証

### 4. TARGET風レース検索
- 競馬場、距離、馬場状態、グレード等で検索
- 人気別成績分析
- 条件別統計

## インストール

### 前提条件

- Python 3.11以上
- [uv](https://github.com/astral-sh/uv)がインストールされていること
- JVLinkToSQLiteで作成したデータベース

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/jvlink-mcp-server.git
cd jvlink-mcp-server

# 依存関係をインストール
uv sync

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してデータベースパスを設定
```

### 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定してください：

```bash
# SQLiteの場合
DB_TYPE=sqlite
DB_PATH=C:/Users/mitsu/JVLinkToSQLite/race.db

# DuckDBの場合
DB_TYPE=duckdb
DB_PATH=C:/Users/mitsu/JVLinkToSQLite/race.duckdb

# PostgreSQLの場合
DB_TYPE=postgresql
DB_CONNECTION_STRING=Host=localhost;Database=jvlink;Username=jvlink_user
JVLINK_DB_PASSWORD=your_password
```

## 使用方法

### MCPサーバーとして起動

```bash
uv run python -m jvlink_mcp_server.server
```

### Claude Desktopで使用

Claude Desktopの設定ファイル（`claude_desktop_config.json`）に以下を追加：

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/mitsu/jvlink-mcp-server",
        "run",
        "python",
        "-m",
        "jvlink_mcp_server.server"
      ],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "C:/Users/mitsu/JVLinkToSQLite/race.db"
      }
    }
  }
}
```

## ライセンス

このプロジェクトは、JVLinkToSQLiteと同じライセンス（GNU GPLv3）の下で公開されています。
