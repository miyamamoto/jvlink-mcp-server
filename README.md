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

## ワンラインインストール

対話式インストーラーで、クローン → 依存解決 → DB検索 → クライアント設定まで一発で完了します。

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/miyamamoto/jvlink-mcp-server/master/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/miyamamoto/jvlink-mcp-server/master/install.ps1 | iex
```

> **💡 keiba.db が見つからない場合**、JRA-VAN DataLabの契約ページをブラウザで自動的に開きます。jrvltsqlの同時インストールも選べます。

---

## 手動インストール

### Step 1: 競馬データベースを作成

[jrvltsql](https://github.com/miyamamoto/jrvltsql) を使ってJRA-VANからデータを取得し、`keiba.db`を作成します。

> **JRA-VAN DataLab** の契約が必要です → [https://jra-van.jp/dlb/](https://jra-van.jp/dlb/)

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

DuckDBは、このMCPサーバーが読み取り専用で接続できる互換入力です。
`jrvltsql 2.0.0` 自体の書き込み先はSQLiteまたはPostgreSQLです。DuckDBを使う場合は、
SQLite/PostgreSQLから利用者が別途変換したデータベースを指定してください。

### PostgreSQL

個別の環境変数で指定:

```
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=keiba
DB_USER=jvlink_writer
DB_PASSWORD=your_password
DB_READONLY_ROLE=jvlink_mcp_reader
```

または接続文字列で指定:

```
DB_TYPE=postgresql
DB_CONNECTION_STRING=host=localhost;port=5432;database=keiba;username=jvlink_writer;password=your_password
DB_READONLY_ROLE=jvlink_mcp_reader
```

PostgreSQLでは、書込みユーザーやスーパーユーザーをMCPの実効ロールとして
使用しないでください。`DB_READONLY_ROLE`には、JRAテーブルだけを`SELECT`できる
`NOLOGIN NOSUPERUSER NOBYPASSRLS`ロールを指定します。接続ユーザー自体が同じ
条件を満たす専用readerなら、この変数は省略できます。MCPは各クエリの計画前に
実効ロールを検証し、NARテーブルを読める場合、または非システムの
`SECURITY DEFINER`関数を実行できる場合は起動・実行を拒否します。

新規のDocker Compose環境では`docker/postgres-init/10-jvlink-mcp-reader.sql`が
このロールを作成します。既存PostgreSQLを使う場合は、DB管理者が同等のロールを
作成してJRAテーブルだけを付与してください。既存データを消す必要はありません。
混在DBで`GRANT SELECT ON ALL TABLES`を行うとNAR表も付与されてfail closedになるため、
JRA表を個別に付与するかJRA専用DBを使用してください。

---

## Mac / Linux で使う場合

JRA-VANのデータ取得（jrvltsql）はWindows専用ですが、**データベースをMac/Linuxに持ってくれば**このMCPサーバーは動作します。

**方法1: SQLiteファイルをコピー** — Dropbox、Google Driveなどで `keiba.db` をコピーするだけ。

**方法2: PostgreSQL経由** — jrvltsqlはPostgreSQLへの書き込みにも対応。Mac/LinuxからWindowsのPostgreSQLに接続すればリアルタイムで最新データを利用できます。

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

## 更新履歴

### v0.7.0（2026-08-27）

- stable `jrvltsql 2.0.0` の80 JRAテーブル・複合主キー契約へ同期
- PostgreSQLの識別子大小文字とpg8000パラメータ形式に対応
- 親リリース同期を、保護ブランチへの直接pushから実wheel検証済みPR作成へ変更
- 旧論理テーブル名とDuckDB生成に関する誤案内を修正
- 本MCPの対象外だったNAR用ツール・スキーマ・クエリテンプレートを公開面から削除

### v0.6.0（2026-06-16）

- jrvltsql v1.6.0 へスキーマ同期（当時の履歴）
- テーブル意味変更に追従: `NL_HC` 調教師賞金 → **坂路調教（HANRO）タイム**、`NL_AV`/`RT_AV` セリ市情報 → **出走取消・競走除外馬情報**
- `NL_RA`/`RT_RA` にコーナー通過順位（`Corner2-4`, `Syukaisu2-4`, `TsukaJyuni2-4`）の説明を追加
- `NL_HR`/`RT_HR`（払戻）の配当配列（複勝最大5件・ワイド最大7件・3連単最大6件等）に列説明を追加
- `NL_O1`/`RT_O1` の主キーに `Kumi` を追加
- 時系列オッズ `TS_O*` に `CollectedAt`（取得時刻）を反映、主キーを更新。速報時系列オッズ `TS_SOKUHO_O1-O6` を追加

### v0.5.0（2026-04-18）

- セキュリティ: テーブル名・カラム名のSQLインジェクション防止バリデーション（`validate_identifier()`）を追加
- セキュリティ: PostgreSQLの`get_table_schema()`でパラメータ化クエリを使用するよう改善
- バグ修正: `sample_data_provider.py`のNL_SEフィルタ条件を修正（`KakuteiJyuni > 0`、INTEGER型対応）
- バグ修正: `high_level_api.py`のGRADE_CODESの重複キーを削除
- バグ修正: `_horse_history_impl`の不要な型変換を`pd.to_numeric`に統一
- ツール名変更: MCPツール`generate_sql_from_natural_language` → `get_sql_generation_prompt`
- NAR（地方競馬）対応を当時追加（v0.7.0で対象外として削除）
- CI/CD: PRごとの自動テスト（`ci.yml`）とjrvltsqlスキーマ同期・自動リリース（`sync-parent.yml`）を追加

## ライセンス

- **商用利用:** 事前にお問い合わせください → oracle.datascientist@gmail.com
- **非商用利用:** Apache License 2.0
