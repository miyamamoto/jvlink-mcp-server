# Claude Desktop セットアップガイド

JVLink MCP ServerをClaude Desktopで使用するための詳細な設定ガイドです。

## 設定ファイルの場所

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

フルパス例:
```
C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json
```

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## 基本的な設定（Windows）

### パターン1: 標準的な設定

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
        "DB_TYPE": "duckdb",
        "DB_PATH": "C:/Users/mitsu/JVData/race.duckdb"
      }
    }
  }
}
```

**重要ポイント:**
- パスは `/` (スラッシュ) を使用
- `\` (バックスラッシュ) は使わない
- `<username>` は実際のユーザー名に置き換える

### パターン2: 別の場所にデータベースがある場合

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
        "DB_TYPE": "duckdb",
        "DB_PATH": "D:/競馬データ/race.duckdb"
      }
    }
  }
}
```

### パターン3: SQLiteを使用する場合

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
        "DB_PATH": "C:/Users/mitsu/JVData/race.db"
      }
    }
  }
}
```

### パターン4: PostgreSQLを使用する場合

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
        "DB_TYPE": "postgresql",
        "DB_CONNECTION_STRING": "Host=localhost;Database=jvlink;Username=jvlink_user",
        "JVLINK_DB_PASSWORD": "your_password_here"
      }
    }
  }
}
```

## macOS / Linux の設定

### パターン1: macOS標準設定

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/mitsu/jvlink-mcp-server",
        "run",
        "python",
        "-m",
        "jvlink_mcp_server.server"
      ],
      "env": {
        "DB_TYPE": "duckdb",
        "DB_PATH": "/Users/mitsu/JVData/race.duckdb"
      }
    }
  }
}
```

### パターン2: Linux標準設定

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/mitsu/jvlink-mcp-server",
        "run",
        "python",
        "-m",
        "jvlink_mcp_server.server"
      ],
      "env": {
        "DB_TYPE": "duckdb",
        "DB_PATH": "/home/mitsu/JVData/race.duckdb"
      }
    }
  }
}
```

## 複数データベースの設定

### パターン1: 本番とテスト用で分ける

```json
{
  "mcpServers": {
    "jvlink-prod": {
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
        "DB_PATH": "C:/Users/mitsu/JVData/race_prod.duckdb"
      }
    },
    "jvlink-test": {
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
        "DB_PATH": "C:/Users/mitsu/JVData/race_test.duckdb"
      }
    }
  }
}
```

### パターン2: 年度別データベース

```json
{
  "mcpServers": {
    "jvlink-2024": {
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
        "DB_PATH": "C:/Users/mitsu/JVData/race_2024.duckdb"
      }
    },
    "jvlink-2023": {
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
        "DB_PATH": "C:/Users/mitsu/JVData/race_2023.duckdb"
      }
    }
  }
}
```

## 設定手順

### ステップ1: 設定ファイルを開く

#### Windows
```powershell
# メモ帳で開く
notepad %APPDATA%\Claude\claude_desktop_config.json

# VS Codeで開く
code %APPDATA%\Claude\claude_desktop_config.json
```

#### macOS
```bash
# テキストエディットで開く
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# VS Codeで開く
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Linux
```bash
# nanoで開く
nano ~/.config/Claude/claude_desktop_config.json

# VS Codeで開く
code ~/.config/Claude/claude_desktop_config.json
```

### ステップ2: 設定をコピー＆ペースト

上記のパターンから適切なものを選んでコピー＆ペーストします。

**重要:** パスを自分の環境に合わせて変更してください！

### ステップ3: ファイルを保存

エディタで保存します（Ctrl+S または Cmd+S）。

### ステップ4: Claude Desktopを再起動

設定を反映させるため、Claude Desktopを完全に終了して再起動します。

#### Windows
- システムトレイのClaude Desktopアイコンを右クリック → 終了
- Claude Desktopを再度起動

#### macOS
- Cmd+Q で完全終了
- Claude Desktopを再度起動

### ステップ5: 接続確認

Claude Desktopで以下のメッセージを送信：

```
データベースのテーブル一覧を教えてください
```

テーブル情報が返ってくれば成功です！

## トラブルシューティング

### エラー: MCPサーバーが認識されない

**確認事項:**
1. JSONの形式が正しいか（カンマ、カッコの対応）
2. パスにバックスラッシュ `\` を使っていないか
3. ユーザー名など、実際の環境に合わせて変更したか

**JSONチェック:**
- [JSONLint](https://jsonlint.com/) でJSON形式をチェック

### エラー: command not found: uv

**原因:** uvがインストールされていない、またはPATHが通っていない

**解決方法:**
```powershell
# uvをインストール
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### エラー: Cannot find module

**原因:** プロジェクトディレクトリのパスが間違っている

**解決方法:**
1. `--directory` のパスを確認
2. 絶対パスで指定しているか確認
3. パスが実際に存在するか確認

```powershell
# Windowsで確認
dir C:\Users\mitsu\jvlink-mcp-server

# macOS/Linuxで確認
ls -la ~/jvlink-mcp-server
```

### エラー: Database file not found

**原因:** データベースファイルのパスが間違っている

**解決方法:**
1. `DB_PATH` のパスを確認
2. ファイルが実際に存在するか確認
3. パスにスラッシュ `/` を使っているか確認

```powershell
# Windowsで確認
dir C:\Users\mitsu\JVData\race.duckdb

# macOS/Linuxで確認
ls -la ~/JVData/race.duckdb
```

## パスの書き方の注意

### ✅ 正しい書き方

```json
"DB_PATH": "C:/Users/mitsu/JVData/race.duckdb"
```

### ❌ 間違った書き方

```json
// バックスラッシュは使わない
"DB_PATH": "C:\Users\mitsu\JVData\race.duckdb"

// Windowsスタイルのパスは使わない
"DB_PATH": "C:\Users\mitsu\JVData\race.duckdb"

// 相対パスは使わない
"DB_PATH": "../JVData/race.duckdb"
```

## 設定例のダウンロード

このリポジトリには設定例ファイルが含まれています：

```bash
# リポジトリをクローン
git clone https://github.com/miyamamoto/jvlink-mcp-server.git
cd jvlink-mcp-server

# 設定例を表示
cat examples/claude_desktop_config_windows.json
cat examples/claude_desktop_config_macos.json
```

## 次のステップ

設定が完了したら：

1. [SAMPLE_QUESTIONS.md](SAMPLE_QUESTIONS.md) でサンプル質問を試す
2. [DATABASE_SETUP.md](DATABASE_SETUP.md) でデータベースセットアップを確認
3. Claude Desktopで自由に質問してみる

Claude Desktopから競馬データ分析を楽しんでください！
