@echo off
REM JVLink MCP Server - Docker Quick Start Script (Windows)

echo ======================================
echo JVLink MCP Server - Docker 起動
echo ======================================
echo.

REM JVDataディレクトリの確認
if "%JVDATA_DIR%"=="" (
    set JVDATA_DIR=%USERPROFILE%\JVData
    echo 環境変数 JVDATA_DIR が設定されていません
    echo デフォルト: %JVDATA_DIR% を使用します
    echo.
)

if not exist "%JVDATA_DIR%" (
    echo エラー: JVDataディレクトリが見つかりません: %JVDATA_DIR%
    echo.
    echo JVLinkToSQLiteでデータベースを作成してください：
    echo   mkdir %USERPROFILE%\JVData
    echo   JVLinkToSQLite.exe --datasource %USERPROFILE%\JVData\race.db --mode Exec
    echo.
    echo または環境変数を設定してください：
    echo   set JVDATA_DIR=C:\path\to\JVData
    exit /b 1
)

REM データベースファイルの確認
set DB_FILE=
set DB_TYPE=
if exist "%JVDATA_DIR%\race.db" (
    set DB_FILE=%JVDATA_DIR%\race.db
    set DB_TYPE=SQLite
) else if exist "%JVDATA_DIR%\race.duckdb" (
    set DB_FILE=%JVDATA_DIR%\race.duckdb
    set DB_TYPE=DuckDB
) else (
    echo エラー: データベースファイルが見つかりません: %JVDATA_DIR%
    echo.
    echo JVLinkToSQLiteで以下のいずれかを作成してください：
    echo   - race.db (SQLite)
    echo   - race.duckdb (DuckDB)
    echo.
    echo 例：
    echo   JVLinkToSQLite.exe --datasource %JVDATA_DIR%\race.db --mode Exec
    exit /b 1
)

echo JVDataディレクトリ: %JVDATA_DIR%
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
echo マウント: %JVDATA_DIR% -^> /data (リアルタイム更新対応)
echo アクセス URL: http://localhost:8000/sse
echo.
echo JVLinkToSQLiteでデータを更新すると即座に反映されます
echo コンテナの再起動は不要です
echo.
echo 停止するには Ctrl+C を押してください
echo ======================================
echo.

docker compose up jvlink-sqlite
