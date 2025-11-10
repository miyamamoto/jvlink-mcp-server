# データベースセットアップガイド

このガイドでは、JVLink MCP Serverで使用するデータベースのセットアップ方法を詳しく説明します。

## 前提条件

- JVLinkToSQLite がインストールされていること
- JRA-VAN DataLab会員であること（データ取得のため）
- 十分なディスク空き容量（推奨: 20GB以上）

## ステップ1: JVLinkToSQLiteのインストール

### 重要: どのバージョンを使うか

以下のいずれかを選択してください：

**公式版（SQLiteのみ対応）**
```bash
git clone https://github.com/urasandesu/JVLinkToSQLite.git
cd JVLinkToSQLite
```

**拡張版（SQLite/DuckDB/PostgreSQL対応）**
```bash
git clone https://github.com/miyamamoto/JVLinkToSQLite.git
cd JVLinkToSQLite
```

### 1-1. ビルド（必要に応じて）

詳細は以下のREADMEを参照してください：
- 公式版: [urasandesu/JVLinkToSQLite](https://github.com/urasandesu/JVLinkToSQLite)
- 拡張版: [miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite)

## ステップ2: SQLiteデータベースの作成

### 2-1. データベース保存ディレクトリの作成

```bash
# Windows
mkdir C:\Users\<username>\JVData

# macOS/Linux
mkdir ~/JVData
```

### 2-2. JVLinkToSQLiteでデータをインポート

```bash
# Windows
cd C:\path\to\JVLinkToSQLite
JVLinkToSQLite.exe --datasource C:\Users\<username>\JVData\race.db --mode Exec

# macOS/Linux
./JVLinkToSQLite --datasource ~/JVData/race.db --mode Exec
```

**オプション:**
- `--mode Exec`: 過去データの一括取得
- `--mode Event`: リアルタイム更新モード
- `--setting setting.xml`: カスタム設定ファイル使用

### 2-3. データ取得の確認

データベースファイルが作成されたことを確認：

```bash
# Windows
dir C:\Users\<username>\JVData\race.db

# macOS/Linux
ls -lh ~/JVData/race.db
```

ファイルサイズが0バイトでなければ成功です。

## ステップ3: JVLink MCP Serverの設定

### 3-1. 環境変数ファイルの作成

```bash
cd /path/to/jvlink-mcp-server
cp .env.example .env
```

### 3-2. .envファイルの編集

```bash
# SQLite設定（デフォルト）
DB_TYPE=sqlite
DB_PATH=C:/Users/<username>/JVData/race.db
```

**重要なポイント:**
- パスの区切りはスラッシュ `/` を使用
- Windowsでも `C:/Users/...` の形式
- バックスラッシュ `\` は使わない

### 3-3. 接続テスト

```bash
uv run python -c "from jvlink_mcp_server.database import DatabaseConnection; db = DatabaseConnection(); print('テーブル一覧:'); print(db.get_tables())"
```

テーブル一覧が表示されれば成功です！

## ステップ4: Claude Desktopへの登録

### 4-1. 設定ファイルの場所

Windows: `%APPDATA%\Claude\claude_desktop_config.json`

存在しない場合は新規作成してください。

### 4-2. 設定の追加

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/<username>/jvlink-mcp-server",
        "run",
        "python",
        "-m",
        "jvlink_mcp_server.server"
      ],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "C:/Users/<username>/JVData/race.db"
      }
    }
  }
}
```

**注意:** `<username>` を実際のユーザー名に置き換えてください。

### 4-3. Claude Desktopの再起動

設定を反映するため、Claude Desktopを完全に終了して再起動します。

### 4-4. 動作確認

Claude Desktopで以下のメッセージを送信：

```
データベースのテーブル一覧を教えてください
```

テーブル情報が返ってくれば成功です！

## ステップ5: Docker でのデプロイ（オプション）

Dockerを使用すると、環境構築が簡単になります。

### 5-1. データディレクトリの準備

```bash
# プロジェクトディレクトリでdataフォルダを作成
cd C:\Users\<username>\jvlink-mcp-server
mkdir data

# データベースファイルをコピー
copy C:\Users\<username>\JVData\race.db data\race.db
```

### 5-2. Dockerイメージのビルドと起動

```bash
# イメージをビルド
docker compose build

# サーバーを起動
docker compose up jvlink-sqlite
```

### 5-3. Claude Desktop での接続

HTTP経由で接続する場合：

```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

詳細は [DOCKER_SETUP.md](DOCKER_SETUP.md) を参照してください。

## トラブルシューティング

### エラー: DB_PATH environment variable not set

**原因:** 環境変数が設定されていない

**解決方法:**
1. `.env`ファイルが存在するか確認
2. `DB_TYPE=sqlite` と `DB_PATH=/path/to/race.db` が記載されているか確認
3. Claude Desktop設定の`env`セクションに同じ設定があるか確認

### エラー: Unable to open database file

**原因:** データベースファイルのパスが間違っている

**解決方法:**
1. ファイルが実際に存在するか確認
2. パスのスラッシュ方向を確認（`/`を使用）
3. 絶対パスで指定しているか確認

```bash
# 正しい例
DB_PATH=C:/Users/mitsu/JVData/race.db

# 間違った例
DB_PATH=race.db  # 相対パスはNG
DB_PATH=C:\Users\mitsu\JVData\race.db  # バックスラッシュはNG
```

### エラー: テーブルが見つからない

**原因:** データベースが空、またはテーブルが作成されていない

**解決方法:**
1. JVLinkToSQLiteで正しくデータがインポートされたか確認
2. データベースファイルサイズを確認（0バイトでないこと）
3. 再度データをインポート

### エラー: Permission denied

**原因:** ファイルアクセス権限の問題

**解決方法:**
1. データベースファイルの読み取り権限を確認
2. ディレクトリの書き込み権限を確認（ロックファイル作成のため）

## データの更新

### 定期的なデータ更新

```bash
# 最新データを追加取得
JVLinkToSQLite.exe --datasource C:\Users\<username>\JVData\race.db --mode Exec
```

### リアルタイム更新

```bash
# イベントモードで起動（レース結果をリアルタイム取得）
JVLinkToSQLite.exe --datasource C:\Users\<username>\JVData\race.db --mode Event
```

## データベースのバックアップ

定期的にデータベースファイルをバックアップすることを推奨します：

```bash
# Windows
copy C:\Users\<username>\JVData\race.db C:\Users\<username>\JVData\race_backup.db

# macOS/Linux
cp ~/JVData/race.db ~/JVData/race_backup_$(date +%Y%m%d).db
```

## パフォーマンス最適化

### インデックスの確認

SQLiteのインデックスを確認：

```sql
-- SQLite CLIで実行
.schema
.indexes
```

### データベースの最適化

```bash
# データベースを最適化（VACUUM）
sqlite3 race.db "VACUUM;"
```

## よくある質問（FAQ）

### Q: DuckDBに移行できますか？

A: はい、可能です。DuckDBの方が分析クエリが高速です。

**方法1: 拡張版JVLinkToSQLiteで新規作成**

[miyamamoto/JVLinkToSQLite](https://github.com/miyamamoto/JVLinkToSQLite) を使用：

```bash
# 拡張版をクローン
git clone https://github.com/miyamamoto/JVLinkToSQLite.git
cd JVLinkToSQLite

# DuckDBを直接作成
JVLinkToSQLite.exe --datasource C:/Users/<username>/JVData/race.duckdb --mode Exec
```

**方法2: SQLiteから移行**

```bash
# DuckDB CLIでSQLiteをインポート
duckdb race.duckdb "INSTALL sqlite; LOAD sqlite; ATTACH 'race.db' AS sqlite_db (TYPE SQLITE); CREATE TABLE new_table AS SELECT * FROM sqlite_db.old_table;"
```

詳細は [DB_COMPATIBILITY.md](DB_COMPATIBILITY.md) を参照してください。

### Q: データベースファイルのサイズはどのくらいになりますか？

A: データ量によりますが、一般的には以下の通りです：
- 1年分のデータ: 約2-5GB
- 3年分のデータ: 約5-15GB
- 10年分のデータ: 約15-50GB

### Q: 複数のデータベースを切り替えて使えますか？

A: はい、.envファイルまたはClaude Desktop設定で`DB_PATH`を変更することで可能です。

### Q: PostgreSQLも使えますか？

A: はい、対応しています。PostgreSQLを使う場合は別途サーバーのセットアップが必要です。

## 次のステップ

データベースのセットアップが完了したら：

1. [SAMPLE_QUESTIONS.md](SAMPLE_QUESTIONS.md) でサンプル質問を試す
2. [README.md](README.md) で提供ツールを確認
3. Claude Desktopで自由に質問してみる

データベースのセットアップに成功したら、競馬データ分析を楽しんでください！
