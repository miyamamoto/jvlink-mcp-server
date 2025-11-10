#!/bin/bash
# JVLink MCP Server - Docker Quick Start Script (Linux/Mac)

set -e

echo "======================================"
echo "JVLink MCP Server - Docker 起動"
echo "======================================"
echo ""

# データディレクトリの確認
if [ ! -d "data" ]; then
    echo "❌ エラー: data/ ディレクトリが見つかりません"
    echo ""
    echo "以下のコマンドでデータディレクトリを作成してください："
    echo "  mkdir data"
    echo "  cp /path/to/race.db data/race.db"
    exit 1
fi

# データベースファイルの確認
DB_FILE=""
if [ -f "data/race.db" ]; then
    DB_FILE="data/race.db"
    DB_TYPE="SQLite"
elif [ -f "data/race.duckdb" ]; then
    DB_FILE="data/race.duckdb"
    DB_TYPE="DuckDB"
else
    echo "❌ エラー: データベースファイルが見つかりません"
    echo ""
    echo "以下のいずれかのファイルを data/ ディレクトリに配置してください："
    echo "  - race.db (SQLite)"
    echo "  - race.duckdb (DuckDB)"
    exit 1
fi

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
echo "アクセス URL: http://localhost:8000/sse"
echo ""
echo "停止するには Ctrl+C を押してください"
echo "======================================"
echo ""

docker compose up jvlink-sqlite
