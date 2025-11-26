# JVLink MCP Server

jrvltsqlで作成した競馬データベースにアクセスするためのMCPサーバー

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

## 前提条件

- **jrvltsqlで作成したデータベース**（必須）
  - [miyamamoto/jrvltsql](https://github.com/miyamamoto/jrvltsql)
  - DBパス: `C:/Users/mitsu/work/jrvltsql/data/keiba.db`
- 対応DB: SQLite（デフォルト）、DuckDB、PostgreSQL

### データベースに含まれるもの
- レース情報（開催日、競馬場、距離、馬場状態）
- 馬情報（馬名、血統、生年月日）
- 成績情報（着順、タイム、オッズ、人気）
- 騎手・調教師情報
- 約57テーブル（NL_38 + RT_19）、300MB〜

### 主要テーブル
| テーブル | 説明 |
|---------|------|
| NL_RA | レース情報 |
| NL_SE | 出馬表・レース結果 |
| NL_UM | 馬マスタ |
| NL_KS | 騎手マスタ |
| NL_CH | 調教師マスタ |
| NL_HR | 払戻情報 |
| NL_O1 | 単勝・複勝オッズ |

## インストール

### 方法1: ローカル環境

```bash
# リポジトリをクローン
git clone https://github.com/miyamamoto/jvlink-mcp-server.git
cd jvlink-mcp-server

# 環境変数を設定
export DB_TYPE=sqlite
export DB_PATH=C:/Users/mitsu/work/jrvltsql/data/keiba.db

# 接続テスト
uv run python -c "from jvlink_mcp_server.database import DatabaseConnection; db = DatabaseConnection(); print(db.get_tables())"
```

### 方法2: Docker（推奨）

```bash
# データディレクトリを指定
export JVDATA_DIR=C:/Users/mitsu/work/jrvltsql/data

# イメージをビルドして起動
docker compose build
docker compose up jvlink-sqlite
```

アクセス: `http://localhost:8000/sse`

## Claude Desktopで使う

### 1. サーバーを起動

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

`claude_desktop_config.json` に以下を追加：

```json
{
  "mcpServers": {
    "jvlink": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Claude Desktopを再起動してください。

## クエリ例

### レース情報の取得
```sql
SELECT Year, MonthDay, Hondai, GradeCD, Kyori, TrackCD
FROM NL_RA
WHERE GradeCD = 'A'
ORDER BY Year DESC, MonthDay DESC
LIMIT 50
```

### 騎手の成績
```sql
SELECT se.KisyuRyakusyo, se.Bamei, se.KakuteiJyuni, se.Ninki
FROM NL_SE se
WHERE se.KisyuRyakusyo LIKE '%ルメール%'
  AND se.KakuteiJyuni IS NOT NULL
ORDER BY se.Year DESC, se.MonthDay DESC
LIMIT 200
```

### レース結果詳細
```sql
SELECT ra.Hondai, se.Umaban, se.Bamei, se.KisyuRyakusyo, se.KakuteiJyuni, se.Odds
FROM NL_RA ra
JOIN NL_SE se ON ra.Year = se.Year AND ra.MonthDay = se.MonthDay
  AND ra.JyoCD = se.JyoCD AND ra.Kaiji = se.Kaiji
  AND ra.Nichiji = se.Nichiji AND ra.RaceNum = se.RaceNum
WHERE ra.Hondai LIKE '%ダービー%'
ORDER BY se.KakuteiJyuni
```

## High-level API

よくある分析パターンを簡単に実行できる高レベルAPIを提供しています：

```python
from jvlink_mcp_server.database.connection import DatabaseConnection
from jvlink_mcp_server.database.high_level_api import get_favorite_performance

db = DatabaseConnection()

# 東京競馬場G1での1番人気成績
result = get_favorite_performance(
    db, venue='東京', ninki=1, grade='G1', year_from='2020'
)
print(f"勝率: {result['win_rate']:.1f}%")

db.close()
```

詳細は [High-level APIガイド](docs/HIGH_LEVEL_API.md) を参照してください。

提供される関数：
- `get_favorite_performance()` - 人気別成績
- `get_jockey_stats()` - 騎手成績
- `get_frame_stats()` - 枠番別成績
- `get_horse_history()` - 馬の戦績
- `get_sire_stats()` - 種牡馬成績

## ドキュメント

- [High-level APIガイド](docs/HIGH_LEVEL_API.md) - 簡単なPython APIの使い方
- [データベースセットアップ](docs/DATABASE_SETUP.md)
- [Docker セットアップ](docs/DOCKER_SETUP.md)
- [Claude Desktop セットアップ](docs/CLAUDE_DESKTOP_SETUP.md)
- [接続セットアップ](docs/REMOTE_SETUP.md)
- [サンプル質問](docs/SAMPLE_QUESTIONS.md)
- [スキーマドキュメント](docs/SCHEMA_DOCUMENTATION.md)

## よくある質問

**Q: データベースはどこで作る？**
A: jrvltsqlで作成してください。

**Q: 旧テーブル名（NL_RA_RACE等）が使えない**
A: jrvltsqlではテーブル名が異なります。NL_RA, NL_SE, NL_UM等を使用してください。

**Q: カラムがすべてTEXT型？**
A: jrvltsqlの設計により、すべてのカラムがTEXT型になっています。数値比較時はCASTが必要な場合があります。

## ライセンス

Apache License 2.0
