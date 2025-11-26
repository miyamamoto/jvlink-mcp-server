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

## データベース構成

### データベースファイル

jrvltsqlで作成されたSQLiteデータベース：

```
C:/Users/mitsu/work/jrvltsql/data/keiba.db
```

**データベースの特徴:**
- 形式: SQLite 3.x
- テーブル数: 約57テーブル（NL系38 + RT系19）
- データサイズ: 約300MB〜（データ量により変動）
- JV-Linkから取得したデータをjrvltsqlが変換・格納

### 主要テーブル構造

#### 1. NL_RA（レース情報テーブル）
レース単位の基本情報を格納

**主要カラム:**
- `Year`, `MonthDay`, `JyoCD`, `Kaiji`, `Nichiji`, `RaceNum`: 複合主キー
- `Kyori`: 距離（メートル）
- `TrackCD`: トラックコード（芝/ダート/障害）
- `BabaJotai`: 馬場状態
- `TenkoCD`: 天候コード

#### 2. NL_SE（出馬表・成績テーブル）
各馬のレース結果を格納

**主要カラム:**
- `Year`, `MonthDay`, `JyoCD`, `Kaiji`, `Nichiji`, `RaceNum`, `Umaban`: 複合主キー
- `KettoNum`: 血統登録番号（NL_UMとJOIN用）
- `KakuteijyuniJyuni`: 確定順位
- `Time`: 走破タイム
- `Ninki`: 人気順
- `Odds`: 単勝オッズ
- `KisyuCode`: 騎手コード（NL_KSとJOIN用）

#### 3. NL_UM（馬マスタテーブル）
馬の基本情報・血統情報を格納

**主要カラム:**
- `KettoNum`: 血統登録番号（主キー）
- `Bamei`: 馬名
- `UmaKigoCD`: 馬記号コード
- `SexCD`: 性別コード
- `HinsyuCD`: 品種コード
- `KeiroCD`: 毛色コード
- `Fukusyoku`: 服色
- `BreederName`: 生産者名
- `SanchiName`: 産地名

#### 4. NL_KS（騎手マスタテーブル）
騎手情報を格納

**主要カラム:**
- `KisyuCode`: 騎手コード（主キー）
- `KisyuName`: 騎手名
- `MinaraiCD`: 見習い区分

#### 5. NL_CH（調教師マスタテーブル）
調教師情報を格納

**主要カラム:**
- `ChokyosiCode`: 調教師コード（主キー）
- `ChokyosiName`: 調教師名
- `Syozoku`: 所属

### テーブル間のJOIN方法

主要なテーブル結合パターン：

#### パターン1: レース情報 + 成績 + 馬情報

```sql
SELECT
    ra.Year, ra.MonthDay, ra.JyoCD, ra.RaceNum,
    se.Umaban, se.KakuteijyuniJyuni, se.Time,
    um.Bamei AS 馬名, um.SexCD AS 性別
FROM NL_SE se
INNER JOIN NL_RA ra
    ON se.Year = ra.Year
    AND se.MonthDay = ra.MonthDay
    AND se.JyoCD = ra.JyoCD
    AND se.Kaiji = ra.Kaiji
    AND se.Nichiji = ra.Nichiji
    AND se.RaceNum = ra.RaceNum
LEFT JOIN NL_UM um
    ON se.KettoNum = um.KettoNum
WHERE ra.Year = 2024
```

#### パターン2: 成績 + 騎手情報

```sql
SELECT
    se.Year, se.MonthDay, se.RaceNum, se.Umaban,
    ks.KisyuName AS 騎手名,
    se.KakuteijyuniJyuni AS 着順
FROM NL_SE se
LEFT JOIN NL_KS ks ON se.KisyuCode = ks.KisyuCode
WHERE se.Year = 2024
```

#### パターン3: 馬の全成績を取得

```sql
SELECT
    se.Year, se.MonthDay, se.RaceNum,
    ra.Kyori AS 距離, ra.TrackCD AS トラック,
    se.KakuteijyuniJyuni AS 着順,
    um.Bamei AS 馬名
FROM NL_SE se
INNER JOIN NL_UM um ON se.KettoNum = um.KettoNum
INNER JOIN NL_RA ra
    ON se.Year = ra.Year
    AND se.MonthDay = ra.MonthDay
    AND se.JyoCD = ra.JyoCD
    AND se.Kaiji = ra.Kaiji
    AND se.Nichiji = ra.Nichiji
    AND se.RaceNum = ra.RaceNum
WHERE um.Bamei = 'ディープインパクト'
ORDER BY se.Year, se.MonthDay
```

**JOIN時の注意点:**
- NL_SEとNL_RAの結合には6つのカラムが必要（Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum）
- NL_SEとNL_UMの結合には`KettoNum`を使用（このカラムは正常に存在）
- 騎手・調教師は外部キー制約がないため、LEFT JOINを推奨

## 環境変数の設定

このMCPサーバーは以下の環境変数で動作を制御します：

### 必須環境変数

| 変数名 | 説明 | 設定例 |
|--------|------|--------|
| `DB_TYPE` | データベースの種類 | `sqlite` |
| `DB_PATH` | SQLiteデータベースファイルのパス | `C:/Users/mitsu/work/jrvltsql/data/keiba.db` |

### 設定例

**Windows (PowerShell):**
```powershell
$env:DB_TYPE="sqlite"
$env:DB_PATH="C:/Users/mitsu/work/jrvltsql/data/keiba.db"
```

**Windows (コマンドプロンプト):**
```cmd
set DB_TYPE=sqlite
set DB_PATH=C:/Users/mitsu/work/jrvltsql/data/keiba.db
```

**Linux/Mac (bash):**
```bash
export DB_TYPE=sqlite
export DB_PATH=/path/to/jrvltsql/data/keiba.db
```

**注意事項:**
- パスは絶対パスで指定してください
- Windowsでもスラッシュ `/` を使用（バックスラッシュ `\` は不可）
- 環境変数は`.env`ファイルにも記述可能

## JVLink MCP Serverのセットアップ

### ローカル環境

```bash
cd jvlink-mcp-server

# 環境変数を設定
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

## 主要テーブル一覧

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

**KettoNumカラムが見つからないエラー**
- このエラーは解消済みです
- NL_UM.KettoNumは正常に存在し、NL_SE.KettoNumとのJOINが可能です

**旧テーブル名（NL_RA_RACE等）が使えない**
- jrvltsqlではテーブル名が異なります
- NL_RA, NL_SE, NL_UM等を使用してください

**Claude Desktopで接続できない**
- Claude Desktopを完全に再起動
- JSONの記法が正しいか確認
- サーバーが起動しているか確認（`http://localhost:8000/sse`にアクセス）
