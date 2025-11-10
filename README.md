# JVLink MCP Server

TARGET frontier JV風の競馬分析MCPサーバー（DuckDB推奨）

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

## 概要

JVLink MCP Serverは、[JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)で作成した競馬データベースにアクセスするためのModel Context Protocol (MCP)サーバーです。

**推奨データベース**: DuckDB（分析クエリが高速、セットアップが簡単）

### なぜDuckDBを推奨するのか？

- ✅ **高速な分析クエリ** - 集計・GROUP BYが2-10倍高速
- ✅ **簡単セットアップ** - サーバー不要、ファイル1つ
- ✅ **Pythonと相性良好** - pandas連携がスムーズ
- ✅ **メモリ効率的** - 大規模データも快適に処理

## データベースセットアップ

### ステップ1: JVLinkToSQLiteでDuckDB作成

'''bash
# DuckDB形式で競馬データをインポート
JVLinkToSQLite.exe --datasource race.duckdb --mode Exec
'''

### ステップ2: 環境変数設定

'''.env''' ファイルを作成：

'''bash
DB_TYPE=duckdb
DB_PATH=C:/Users/mitsu/JVData/race.duckdb
'''

### ステップ3: 接続テスト

'''bash
uv run python -c "from jvlink_mcp_server.database import DatabaseConnection; db = DatabaseConnection(); print(db.get_tables())"
'''

## 使用方法

### Claude Desktopで使用

'''json
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
        "DB_TYPE": "duckdb",
        "DB_PATH": "C:/Users/mitsu/JVData/race.duckdb"
      }
    }
  }
}
'''

## ライセンス

Apache License 2.0
