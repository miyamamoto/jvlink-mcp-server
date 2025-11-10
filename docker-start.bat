@echo off
REM JVLink MCP Server - Docker Quick Start Script (Windows)

echo ======================================
echo JVLink MCP Server - Docker 起動
echo ======================================
echo.

REM データディレクトリの確認
if not exist "data" (
    echo エラー: data\ ディレクトリが見つかりません
    echo.
    echo 以下のコマンドでデータディレクトリを作成してください：
    echo   mkdir data
    echo   copy C:\path\to\race.db data\race.db
    exit /b 1
)

REM データベースファイルの確認
set DB_FILE=
set DB_TYPE=
if exist "data\race.db" (
    set DB_FILE=data\race.db
    set DB_TYPE=SQLite
) else if exist "data\race.duckdb" (
    set DB_FILE=data\race.duckdb
    set DB_TYPE=DuckDB
) else (
    echo エラー: データベースファイルが見つかりません
    echo.
    echo 以下のいずれかのファイルを data\ ディレクトリに配置してください：
    echo   - race.db (SQLite)
    echo   - race.duckdb (DuckDB)
    exit /b 1
)

echo データベースファイル: %DB_FILE%
echo データベースタイプ: %DB_TYPE%
echo.

REM Dockerイメージの確認
docker images | findstr jvlink-mcp-server >nul 2>&1
if %errorlevel% neq 0 (
    echo Dockerイメージをビルド中...
    docker compose build
    echo.
)

REM サーバー起動
echo JVLink MCP Server を起動中...
echo.
echo アクセス URL: http://localhost:8000/sse
echo.
echo 停止するには Ctrl+C を押してください
echo ======================================
echo.

docker compose up jvlink-sqlite
