# JVLink MCP Server

**Claudeに話しかけるだけで、競馬データを自由に分析できます。**

SQLを書く必要はありません。自然な日本語で質問すれば、過去のレース結果、騎手成績、血統傾向など、あらゆる競馬データを調べられます。

<img src="docs/images/demo.gif" width="800" alt="デモ動画">

## こんな質問ができます

### 「1番人気の勝率はどのくらい？」

| 出走数 | 勝利数 | 勝率 |
|--------|--------|------|
| 6,294 | 2,474 | 39.3% |

### 「今年勝ち星が多い騎手は？」

| 騎手 | 騎乗数 | 勝利 | 勝率 |
|------|--------|------|------|
| ルメール | 537 | 142 | 26.4% |
| 戸崎圭太 | 832 | 135 | 16.2% |
| 松山弘平 | 863 | 125 | 14.5% |
| 坂井瑠星 | 729 | 119 | 16.3% |
| 川田将雅 | 542 | 118 | 21.8% |

### 「産駒の勝ち星が多い種牡馬は？」

| 種牡馬 | 出走数 | 勝利 |
|--------|--------|------|
| キズナ | 1,717 | 207 |
| ロードカナロア | 1,633 | 178 |
| ドレフォン | 1,382 | 150 |
| エピファネイア | 1,488 | 138 |
| リアルスティール | 1,106 | 125 |

### 他にもこんな質問ができます

- 東京芝1600mで内枠と外枠、どっちが有利？
- G1レースで1番人気が飛んだレースを教えて
- ディープインパクト産駒の芝での成績は？
- 馬体重500kg以上の馬の成績は？
- 上がり3F最速で勝った馬を調べて

---

## クイックスタート

### Step 1: 競馬データベースを作成

[jrvltsql](https://github.com/miyamamoto/jrvltsql) を使ってJRA-VANからデータを取得し、`keiba.db`を作成します。

### Step 2: リポジトリをクローン

```bash
git clone https://github.com/miyamamoto/jvlink-mcp-server.git
cd jvlink-mcp-server
pip install uv
uv sync
```

### Step 3: MCPクライアントに設定

お使いのクライアントに合わせて以下のセクションを参照してください。

> **💡 初回起動時**に依存パッケージを自動インストールします（30〜60秒）。

---

## MCPクライアント別セットアップ

### Claude Desktop

`claude_desktop_config.json` に追加:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/jvlink-mcp-server", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "/path/to/keiba.db"
      }
    }
  }
}
```

> **Windows の場合**: `command` を `"uv.exe"` に変更してください。[Releases](https://github.com/miyamamoto/jvlink-mcp-server/releases) の `.mcpb` ファイルを使えば自動インストールも可能です。

---

### Claude Code (CLI)

```bash
claude mcp add jvlink \
  -e DB_TYPE=sqlite \
  -e DB_PATH=/path/to/keiba.db \
  -- uv run --directory /path/to/jvlink-mcp-server python -m jvlink_mcp_server.server
```

プロジェクトスコープに追加する場合は `-s project` を付けてください。

---

### Cursor

プロジェクトルートに `.cursor/mcp.json` を作成:

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/jvlink-mcp-server", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "/path/to/keiba.db"
      }
    }
  }
}
```

Cursor Settings → MCP でサーバーが認識されていることを確認してください。

---

### VS Code + GitHub Copilot

`.vscode/mcp.json` を作成:

```json
{
  "servers": {
    "jvlink": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/jvlink-mcp-server", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "/path/to/keiba.db"
      }
    }
  }
}
```

VS Codeの設定で `"chat.mcp.enabled": true` を有効にしてください。

---

### Windsurf

Windsurf Settings → MCP から「Add custom server」を選択し、`~/.codeium/windsurf/mcp_config.json` に追加:

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/jvlink-mcp-server", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "/path/to/keiba.db"
      }
    }
  }
}
```

---

### Codex CLI (OpenAI)

```bash
# codex の設定ファイル (~/.codex/config.yaml) に追加するか、
# MCP_SERVERS 環境変数で指定
export MCP_SERVERS='[{"name":"jvlink","transport":{"type":"stdio","command":"uv","args":["run","--directory","/path/to/jvlink-mcp-server","python","-m","jvlink_mcp_server.server"],"env":{"DB_TYPE":"sqlite","DB_PATH":"/path/to/keiba.db"}}}]'

codex
```

---

### その他のMCPクライアント

どのクライアントでも共通の設定パターン:

| 項目 | 値 |
|------|-----|
| **コマンド** | `uv` |
| **引数** | `run --directory /path/to/jvlink-mcp-server python -m jvlink_mcp_server.server` |
| **環境変数** | `DB_TYPE=sqlite`, `DB_PATH=/path/to/keiba.db` |
| **プロトコル** | stdio |

---

## データベース設定

### SQLite（推奨）

```
DB_TYPE=sqlite
DB_PATH=/path/to/keiba.db
```

### DuckDB

```
DB_TYPE=duckdb
DB_PATH=/path/to/keiba.duckdb
```

### PostgreSQL

個別の環境変数で指定:

```
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=keiba
DB_USER=postgres
DB_PASSWORD=your_password
```

または接続文字列で指定:

```
DB_TYPE=postgresql
DB_CONNECTION_STRING=host=localhost;port=5432;database=keiba;username=postgres;password=your_password
```

---

## Mac / Linux で使う場合

JRA-VANのデータ取得（jrvltsql）はWindows専用ですが、**データベースをMac/Linuxに持ってくれば**このMCPサーバーは動作します。

**方法1: SQLiteファイルをコピー** — Dropbox、Google Driveなどで `keiba.db` をコピーするだけ。

**方法2: PostgreSQL経由** — jrvltsqlはPostgreSQLへの書き込みにも対応。Mac/LinuxからWindowsのPostgreSQLに接続すればリアルタイムで最新データを利用できます。

---

## NAR（地方競馬）対応

`nar-support` ブランチで地方競馬データにも対応しています。大井・船橋・川崎・浦和・名古屋・園田など主要な地方競馬場のデータを分析できます。

地方競馬データの取得には [NV-Link](https://www.nvlink.jp/) が必要です。

---

## 使い方のコツ

| コツ | 説明 |
|-----|------|
| **気軽に質問** | 思いついたことをそのまま聞いてみてください |
| **条件を追加** | 「東京の」「芝の」「1600mの」など条件を絞ると詳細な分析に |
| **比較を依頼** | 「AとBを比較して」「年度別の推移を見せて」も得意です |
| **深掘りする** | 回答を見て気になったら続けて質問。会話で分析を深められます |

→ もっと質問例を見たい場合は [サンプル質問集](docs/SAMPLE_QUESTIONS.md)

---

## トラブルシューティング

### サーバーが起動しない

1. `uv` がインストールされているか確認: `uv --version`
2. パスが正しいか確認: `DB_PATH` のファイルが存在するか
3. 依存関係を再インストール: `cd /path/to/jvlink-mcp-server && uv sync`

### データが取得できない

1. `keiba.db` が正しく作成されているか確認
2. テーブルが存在するか: `sqlite3 keiba.db ".tables"` で確認
3. MCPクライアントのログを確認

### PostgreSQL接続エラー

1. PostgreSQLが起動しているか確認
2. ファイアウォールでポートが開いているか確認
3. `DB_CONNECTION_STRING` のフォーマットを確認（セミコロン区切り）

---

## JRA-VANデータの利用について

本ソフトウェアで分析するデータは[JRA-VAN](https://jra-van.jp/)から提供されるものです。

**禁止事項:** データの再配布、第三者への提供、データベースファイルの共有

**許可される利用:** 個人的な競馬分析・研究、自社内での利用

詳細は [JRA-VAN利用規約](https://jra-van.jp/info/rule.html) をご確認ください。

## ライセンス

- **商用利用:** 事前にお問い合わせください → oracle.datascientist@gmail.com
- **非商用利用:** Apache License 2.0
