# データベースセットアップ (jrvltsql版)

## 前提条件

- JRA-VAN DataLab会員
- jrvltsqlをインストール済み
- ディスク空き容量 1GB以上

## jrvltsqlのインストール

```bash
git clone https://github.com/miyamamoto/jrvltsql.git
cd jrvltsql
```

ビルド方法はリポジトリのREADMEを参照してください。

## データベース場所

jrvltsqlで作成されたデータベース：

```
C:/Users/mitsu/work/jrvltsql/data/keiba.db
```

**keiba.db の内容:**
- **レース情報 (NL_RA)**: 開催日、競馬場、距離、馬場状態など
- **馬情報 (NL_UM)**: 馬名、血統、生年月日など
- **成績情報 (NL_SE)**: 着順、タイム、オッズ、人気など
- **騎手・調教師情報 (NL_KS, NL_CH)**: 名前、所属、成績など
- **オッズ情報 (NL_O1〜NL_O6)**: 単勝、複勝、馬連、ワイド等
- **払戻情報 (NL_HR)**: 各種払戻金
- **テーブル数**: 約57テーブル（NL_38 + RT_19）
- **データサイズ**: 約300MB〜

## JVLink MCP Serverのセットアップ

### ローカル環境

```bash
cd jvlink-mcp-server
export DB_TYPE=sqlite
export DB_PATH=C:/Users/mitsu/work/jrvltsql/data/keiba.db

# 接続テスト
uv run python -c "from jvlink_mcp_server.database import DatabaseConnection; db = DatabaseConnection(); print(db.get_tables())"
```

### Docker

```bash
export JVDATA_DIR=C:/Users/mitsu/work/jrvltsql/data
docker compose build
docker compose up jvlink-sqlite
```

アクセス: `http://localhost:8000/sse`

## Claude Desktopで使う

### 1. サーバー起動

**Docker（推奨）:**
```bash
export JVDATA_DIR=C:/Users/mitsu/work/jrvltsql/data
docker compose up jvlink-sqlite
```

**ローカル環境:**
```bash
export DB_TYPE=sqlite
export DB_PATH=C:/Users/mitsu/work/jrvltsql/data/keiba.db
uv run python -m jvlink_mcp_server.server_sse
```

### 2. Claude Desktopに接続

`%APPDATA%\Claude\claude_desktop_config.json` に追加：

```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Claude Desktopを再起動して完了です。

## 主要テーブル

| テーブル | 説明 | 主キー |
|---------|------|--------|
| NL_RA | レース情報 | Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum |
| NL_SE | 出馬表・結果 | Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Umaban |
| NL_UM | 馬マスタ | KettoNum |
| NL_KS | 騎手マスタ | KisyuCode |
| NL_CH | 調教師マスタ | ChokyosiCode |
| NL_HR | 払戻 | Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum |
| NL_O1 | 単勝・複勝オッズ | Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Umaban |

## トラブルシューティング

**データベースが見つからない**
- パスを絶対パスで指定（`C:/Users/mitsu/work/jrvltsql/data/keiba.db`）
- スラッシュ `/` を使う（バックスラッシュ `\` はNG）

**テーブルが見つからない**
- jrvltsqlでデータ取得が完了しているか確認
- データベースファイルサイズが0バイトでないか確認

**旧テーブル名（NL_RA_RACE等）が使えない**
- jrvltsqlではテーブル名が異なります
- NL_RA, NL_SE, NL_UM等を使用してください

**Claude Desktopで接続できない**
- Claude Desktopを完全に再起動
- JSONの記法が正しいか確認
