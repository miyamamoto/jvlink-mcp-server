# High-level API ガイド

## 概要

`high_level_api.py`は、JVLinkデータベースでよく使われる分析パターンを簡単に実行できる高レベルAPIを提供します。SQLクエリを直接書く必要がなく、Pythonの関数を呼び出すだけで複雑な集計が可能です。

## インストール

```bash
pip install -e .
```

## 基本的な使い方

```python
from jvlink_mcp_server.database.connection import DatabaseConnection
from jvlink_mcp_server.database.high_level_api import get_favorite_performance

# データベース接続（環境変数から設定を読み込み）
db = DatabaseConnection()

# 1番人気の成績を取得
result = get_favorite_performance(db, ninki=1)
print(f"勝率: {result['win_rate']:.1f}%")

# 接続を閉じる
db.close()
```

## 提供される関数

### 1. `get_favorite_performance()` - 人気別成績

指定した人気順位の成績を集計します。

**パラメータ:**
- `db_connection`: DatabaseConnectionインスタンス（必須）
- `ninki`: 人気順位（1-18）、デフォルト: 1
- `venue`: 競馬場名（例: '東京', '中山'）
- `grade`: グレード（例: 'G1', 'G2', 'G3', 'A', 'B', 'C'）
- `year_from`: 集計開始年（例: '2023'）
- `distance`: 距離（メートル、例: 1600）

**返り値（dict）:**
```python
{
    'total': 総レース数,
    'wins': 1着回数,
    'places_2': 2着以内回数,
    'places_3': 3着以内回数,
    'win_rate': 勝率（%）,
    'place_rate_2': 連対率（%）,
    'place_rate_3': 複勝率（%）,
    'conditions': 適用した条件の説明,
    'query': 実行されたSQLクエリ
}
```

**使用例:**
```python
# 東京競馬場G1での1番人気成績（2020年以降）
result = get_favorite_performance(
    db,
    venue='東京',
    ninki=1,
    grade='G1',
    year_from='2020'
)

print(f"勝率: {result['win_rate']:.1f}%")
# 出力: 勝率: 45.2%

# 中山競馬場1600mでの2番人気成績
result = get_favorite_performance(
    db,
    venue='中山',
    ninki=2,
    distance=1600
)
```

### 2. `get_jockey_stats()` - 騎手成績

指定した騎手の成績を集計します（部分一致検索）。

**パラメータ:**
- `db_connection`: DatabaseConnectionインスタンス（必須）
- `jockey_name`: 騎手名（部分一致、例: 'ルメール', '武豊'）（必須）
- `venue`: 競馬場名（例: '東京', '中山'）
- `year_from`: 集計開始年（例: '2023'）
- `distance`: 距離（メートル、例: 1600）

**返り値（dict）:**
```python
{
    'jockey_name': 騎手名（マッチした中で最も騎乗回数が多い騎手）,
    'total_rides': 総騎乗回数,
    'wins': 1着回数,
    'places_2': 2着以内回数,
    'places_3': 3着以内回数,
    'win_rate': 勝率（%）,
    'place_rate_2': 連対率（%）,
    'place_rate_3': 複勝率（%）,
    'conditions': 適用した条件の説明,
    'matched_jockeys': マッチした騎手のリスト,
    'query': 実行されたSQLクエリ
}
```

**使用例:**
```python
# ルメール騎手の東京競馬場成績（2023年以降）
result = get_jockey_stats(
    db,
    jockey_name='ルメール',
    venue='東京',
    year_from='2023'
)

print(f"{result['jockey_name']}: 勝率 {result['win_rate']:.1f}%")
# 出力: ルメール: 勝率 28.5%

# 武豊騎手の全成績
result = get_jockey_stats(db, jockey_name='武豊')
```

### 3. `get_frame_stats()` - 枠番別成績

枠番別の成績を集計します。

**パラメータ:**
- `db_connection`: DatabaseConnectionインスタンス（必須）
- `venue`: 競馬場名（例: '東京', '中山'）
- `distance`: 距離（メートル、例: 1600）
- `year_from`: 集計開始年（例: '2023'）

**返り値（DataFrame）:**
```
wakuban  total  wins  places_2  places_3  win_rate  place_rate_2  place_rate_3
1        100    12    30        50        12.0      30.0          50.0
2        100    15    32        52        15.0      32.0          52.0
...
```

DataFrameの`.attrs['conditions']`と`.attrs['query']`に条件とクエリが格納されます。

**使用例:**
```python
# 東京競馬場1600mの枠番別成績
df = get_frame_stats(
    db,
    venue='東京',
    distance=1600
)

print(df.to_string(index=False))
# 出力:
# wakuban  total  wins  places_2  places_3  win_rate  place_rate_2  place_rate_3
#      1    150    18        45        70     12.00         30.00         46.67
#      2    150    20        48        72     13.33         32.00         48.00
#      ...
```

### 4. `get_horse_history()` - 馬の戦績

指定した馬の戦績を取得します。

**パラメータ:**
- `db_connection`: DatabaseConnectionインスタンス（必須）
- `horse_name`: 馬名（部分一致、例: 'ディープインパクト'）（必須）
- `year_from`: 集計開始年（例: '2023'）

**返り値（DataFrame）:**
```
race_date   venue  race_name      distance  finish  popularity  jockey      time
2023-0521   東京   日本ダービー     2400      1       3          ルメール    022434
2023-0430   中山   皐月賞          2000      2       2          武豊        020112
...
```

**使用例:**
```python
# ディープインパクトの戦績（2005年以降）
df = get_horse_history(
    db,
    horse_name='ディープインパクト',
    year_from='2005'
)

print(f"総レース数: {len(df)}")
print(df.head().to_string(index=False))
```

### 5. `get_sire_stats()` - 種牡馬成績

指定した種牡馬（父馬）の産駒成績を集計します。

**パラメータ:**
- `db_connection`: DatabaseConnectionインスタンス（必須）
- `sire_name`: 種牡馬名（部分一致、例: 'ディープインパクト'）（必須）
- `venue`: 競馬場名（例: '東京', '中山'）
- `distance`: 距離（メートル、例: 1600）
- `year_from`: 集計開始年（例: '2023'）

**返り値（dict）:**
```python
{
    'sire_name': 種牡馬名,
    'total_runs': 総出走数,
    'wins': 1着回数,
    'places_2': 2着以内回数,
    'places_3': 3着以内回数,
    'win_rate': 勝率（%）,
    'place_rate_2': 連対率（%）,
    'place_rate_3': 複勝率（%）,
    'conditions': 適用した条件の説明,
    'matched_sires': マッチした種牡馬のリスト,
    'query': 実行されたSQLクエリ
}
```

**使用例:**
```python
# ディープインパクト産駒の東京1600m成績（2020年以降）
result = get_sire_stats(
    db,
    sire_name='ディープインパクト',
    venue='東京',
    distance=1600,
    year_from='2020'
)

print(f"{result['sire_name']}産駒: 勝率 {result['win_rate']:.1f}%")
# 出力: ディープインパクト産駒: 勝率 15.3%
```

## 競馬場コード

以下の競馬場名（日本語）が使用可能です：

| 競馬場名 | コード |
|---------|-------|
| 札幌    | 01    |
| 函館    | 02    |
| 福島    | 03    |
| 新潟    | 04    |
| 東京    | 05    |
| 中山    | 06    |
| 中京    | 07    |
| 京都    | 08    |
| 阪神    | 09    |
| 小倉    | 10    |

## グレードコード

以下のグレード表記が使用可能です：

| 入力      | 内部コード | 説明           |
|-----------|-----------|---------------|
| G1, GI    | A         | G1（最高峰）   |
| G2, GII   | B         | G2            |
| G3, GIII  | C         | G3            |
| A         | A         | G1（直接指定） |
| B         | B         | G2（直接指定） |
| C         | C         | G3（直接指定） |
| リステッド | D         | リステッド競走 |
| オープン特別 | E       | オープン特別   |
| 3勝      | F         | 3勝クラス      |
| 2勝      | G         | 2勝クラス      |
| 1勝      | H         | 1勝クラス      |
| 未勝利    | I         | 未勝利         |
| 新馬      | J         | 新馬           |

## 完全な実装例

```python
#!/usr/bin/env python3
"""High-level API使用例"""

from jvlink_mcp_server.database.connection import DatabaseConnection
from jvlink_mcp_server.database.high_level_api import (
    get_favorite_performance,
    get_jockey_stats,
    get_frame_stats,
    get_horse_history,
    get_sire_stats
)

def main():
    # データベース接続
    db = DatabaseConnection()

    try:
        # 例1: 東京競馬場G1での1番人気成績
        print("=" * 80)
        print("東京競馬場G1での1番人気成績（2020年以降）")
        print("=" * 80)
        result = get_favorite_performance(
            db,
            venue='東京',
            ninki=1,
            grade='G1',
            year_from='2020'
        )
        print(f"総レース数: {result['total']}")
        print(f"勝率: {result['win_rate']:.1f}%")
        print(f"連対率: {result['place_rate_2']:.1f}%")
        print()

        # 例2: 騎手成績
        print("=" * 80)
        print("ルメール騎手の東京競馬場成績（2023年以降）")
        print("=" * 80)
        result = get_jockey_stats(
            db,
            jockey_name='ルメール',
            venue='東京',
            year_from='2023'
        )
        print(f"騎手名: {result['jockey_name']}")
        print(f"騎乗回数: {result['total_rides']}")
        print(f"勝率: {result['win_rate']:.1f}%")
        print()

        # 例3: 枠番別成績
        print("=" * 80)
        print("東京競馬場1600mの枠番別成績")
        print("=" * 80)
        df = get_frame_stats(
            db,
            venue='東京',
            distance=1600
        )
        print(df.to_string(index=False))
        print()

        # 例4: 馬の戦績
        print("=" * 80)
        print("ディープインパクトの戦績（上位10件）")
        print("=" * 80)
        df = get_horse_history(
            db,
            horse_name='ディープインパクト',
            year_from='2005'
        )
        print(df.head(10).to_string(index=False))
        print()

        # 例5: 種牡馬成績
        print("=" * 80)
        print("ディープインパクト産駒の東京1600m成績")
        print("=" * 80)
        result = get_sire_stats(
            db,
            sire_name='ディープインパクト',
            venue='東京',
            distance=1600,
            year_from='2020'
        )
        print(f"種牡馬名: {result['sire_name']}")
        print(f"出走数: {result['total_runs']}")
        print(f"勝率: {result['win_rate']:.1f}%")

    finally:
        # 必ず接続を閉じる
        db.close()

if __name__ == '__main__':
    main()
```

## エラーハンドリング

```python
from jvlink_mcp_server.database.high_level_api import get_favorite_performance

try:
    result = get_favorite_performance(db, venue='無効な競馬場')
except ValueError as e:
    print(f"エラー: {e}")
    # 出力: エラー: 不明な競馬場名: 無効な競馬場. 有効な値: ['札幌', '函館', ...]
```

## デバッグ

すべての関数は、返り値に実行されたSQLクエリを含んでいます。デバッグ時に確認できます：

```python
result = get_favorite_performance(db, venue='東京', ninki=1)
print("実行されたクエリ:")
print(result['query'])
```

## テスト

```bash
# テストを実行
pytest tests/test_high_level_api.py -v

# カバレッジを確認
pytest tests/test_high_level_api.py --cov=jvlink_mcp_server.database.high_level_api
```

## パフォーマンス最適化のヒント

1. **インデックスの活用**: よく使うカラム（Year, JyoCD, Ninki, KakuteiJyuni）にはインデックスを作成しておくと高速化します。

2. **年範囲の指定**: 大量のデータがある場合は、`year_from`パラメータで範囲を絞ると高速化します。

3. **接続の再利用**: DatabaseConnectionオブジェクトは再利用できます。毎回作り直すのは避けましょう。

```python
# 良い例
db = DatabaseConnection()
result1 = get_favorite_performance(db, venue='東京')
result2 = get_jockey_stats(db, jockey_name='ルメール')
db.close()

# 悪い例（非効率）
db1 = DatabaseConnection()
result1 = get_favorite_performance(db1, venue='東京')
db1.close()

db2 = DatabaseConnection()
result2 = get_jockey_stats(db2, jockey_name='ルメール')
db2.close()
```

## トラブルシューティング

### Q: "不明な競馬場名" エラーが出る
A: 競馬場名は日本語で指定してください（例: '東京', '中山'）。英語やローマ字は使用できません。

### Q: 結果が0件になる
A: 以下を確認してください：
- データベースにデータが入っているか
- 年の範囲が適切か
- 競馬場名やグレードコードが正しいか

### Q: 複数の騎手/馬/種牡馬がマッチする
A: 部分一致検索のため、より詳細な名前を指定してください。または、`matched_jockeys`等のフィールドで確認できます。

## 今後の拡張予定

- [ ] 馬場状態別の成績集計
- [ ] トラックタイプ（芝/ダート）別の成績
- [ ] クラス別の成績集計
- [ ] 脚質別の成績分析
- [ ] オッズ範囲別の成績
- [ ] 調教師成績の集計

## 関連ドキュメント

- [DATABASE_SETUP.md](./DATABASE_SETUP.md) - データベースのセットアップ
- [QUERY_GUIDELINES.md](../QUERY_GUIDELINES.md) - SQLクエリガイドライン
- [README.md](../README.md) - プロジェクト全体の説明
