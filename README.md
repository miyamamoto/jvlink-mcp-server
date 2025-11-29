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

## クイックスタート（Windows）

**3ステップで使い始められます**

### Step 1: 競馬データベースを作成

[jrvltsql](https://github.com/miyamamoto/jrvltsql) を使ってJRA-VANからデータを取得し、`keiba.db`を作成します。

### Step 2: MCPサーバーをインストール

[Releases](https://github.com/miyamamoto/jvlink-mcp-server/releases)から `.mcpb` ファイルをダウンロードしてダブルクリック。

### Step 3: データベースを指定

Claude Desktopのインストール画面で`keiba.db`のパスを指定して完了！

> **💡 初回起動時**に依存パッケージを自動インストールします（30〜60秒）。

---

## Mac / Linux で使う場合

JRA-VANのデータ取得（jrvltsql）はWindows専用ですが、**データベースをMac/Linuxに持ってくれば**このMCPサーバーは動作します。

### 方法1: SQLiteファイルをコピー

```
Windows                          Mac / Linux
┌─────────────┐                  ┌─────────────┐
│  jrvltsql   │                  │  keiba.db   │ ← コピー
│      ↓      │   ファイル共有    │      ↓      │
│  keiba.db   │ ───────────────▶ │ MCPサーバー  │
└─────────────┘   クラウド同期    │      ↓      │
                                 │Claude Desktop│
                                 └─────────────┘
```

Dropbox、Google Drive、USBメモリなどで`keiba.db`をコピーするだけ。
データ更新時は再度コピーが必要です。

### 方法2: PostgreSQL経由（リアルタイム更新）

```
Windows                          Mac / Linux
┌─────────────┐                  ┌─────────────┐
│  jrvltsql   │                  │ MCPサーバー  │
│      ↓      │    ネットワーク   │      ↓      │
│ PostgreSQL  │ ◀───────────────│Claude Desktop│
└─────────────┘                  └─────────────┘
```

jrvltsqlはPostgreSQLへの書き込みにも対応。
Mac/LinuxからWindowsのPostgreSQLに接続すればリアルタイムで最新データを利用できます。

### Mac / Linux でのセットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/miyamamoto/jvlink-mcp-server.git
cd jvlink-mcp-server

# 2. 依存関係をインストール
pip install uv
uv sync
```

`claude_desktop_config.json` に追加:

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

<details>
<summary>PostgreSQLを使う場合の設定</summary>

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/jvlink-mcp-server", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "postgresql",
        "DB_HOST": "your-windows-pc.local",
        "DB_PORT": "5432",
        "DB_NAME": "keiba",
        "DB_USER": "your_user",
        "DB_PASSWORD": "your_password"
      }
    }
  }
}
```

</details>

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

## JRA-VANデータの利用について

本ソフトウェアで分析するデータは[JRA-VAN](https://jra-van.jp/)から提供されるものです。

**禁止事項:** データの再配布、第三者への提供、データベースファイルの共有

**許可される利用:** 個人的な競馬分析・研究、自社内での利用

詳細は [JRA-VAN利用規約](https://jra-van.jp/info/rule.html) をご確認ください。

## ライセンス

Apache License 2.0
