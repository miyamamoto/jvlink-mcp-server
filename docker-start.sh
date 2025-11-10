#!/bin/bash
# JVLink MCP Server - Docker Quick Start Script (Linux/Mac)

set -e

echo "======================================"
echo "JVLink MCP Server - Docker 起動"
echo "======================================"
echo ""

# JVDataディレクトリの確認
if [ -z "$JVDATA_DIR" ]; then
    JVDATA_DIR="$HOME/JVData"
    echo "⚠️  環境変数 JVDATA_DIR が設定されていません"
    echo "   デフォルト: $JVDATA_DIR を使用します"
    echo ""
fi

if [ ! -d "$JVDATA_DIR" ]; then
    echo "❌ エラー: JVDataディレクトリが見つかりません: $JVDATA_DIR"
    echo ""
    echo "JVLinkToSQLiteでデータベースを作成してください："
    echo "  mkdir ~/JVData"
    echo "  JVLinkToSQLite --datasource ~/JVData/race.db --mode Exec"
    echo ""
    echo "または環境変数を設定してください："
    echo "  export JVDATA_DIR=/path/to/JVData"
    exit 1
fi

# データベースファイルの確認
DB_FILE=""
DB_TYPE=""
if [ -f "$JVDATA_DIR/race.db" ]; then
    DB_FILE="$JVDATA_DIR/race.db"
    DB_TYPE="SQLite"
elif [ -f "$JVDATA_DIR/race.duckdb" ]; then
    DB_FILE="$JVDATA_DIR/race.duckdb"
    DB_TYPE="DuckDB"
else
    echo "❌ エラー: データベースファイルが見つかりません: $JVDATA_DIR"
    echo ""
    echo "JVLinkToSQLiteで以下のいずれかを作成してください："
    echo "  - race.db (SQLite)"
    echo "  - race.duckdb (DuckDB)"
    echo ""
    echo "例："
    echo "  JVLinkToSQLite --datasource $JVDATA_DIR/race.db --mode Exec"
    exit 1
fi

echo "✅ JVDataディレクトリ: $JVDATA_DIR"
echo "✅ データベースファイル: $DB_FILE"
echo "✅ データベースタイプ: $DB_TYPE"
echo ""

# Dockerイメージの確認
if ! docker images | grep -q "jvlink-mcp-server"; then
    echo "🔨 Dockerイメージをビルド中..."
    docker compose build
    echo ""
fi

# サーバー起動
echo "🚀 JVLink MCP Server を起動中..."
echo ""
echo "📁 マウント: $JVDATA_DIR -> /data (リアルタイム更新対応)"
echo "🌐 アクセス URL: http://localhost:8000/sse"
echo ""
echo "💡 JVLinkToSQLiteでデータを更新すると即座に反映されます"
echo "   コンテナの再起動は不要です"
echo ""
echo "停止するには Ctrl+C を押してください"
echo "======================================"
echo ""

export JVDATA_DIR
docker compose up jvlink-sqlite
