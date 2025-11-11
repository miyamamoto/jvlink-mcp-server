# JVLink MCP Server - スキーマドキュメント機能

## 概要

LLMがより正確にSQLクエリを生成できるように、データベーススキーマに**詳細な説明文**を追加しました。

## 実装内容

### 1. スキーマ説明の追加

`schema_descriptions.py` - データベースのテーブル・カラムの説明を一元管理

### 2. 強化された `get_table_info()` ツール

MCPの `get_table_info()` ツールが以下の情報を返すように拡張：

- **テーブル説明**: テーブルの目的と用途
- **TARGET相当機能**: での対応画面
- **主キー情報**: テーブルの主キー
- **カラム詳細**: 各カラムの名前、型、**説明**
- **クエリヒント**: よく使うJOINパターンや条件の例

## 使用例

### Before（説明なし）

```json
{
  "table_name": "NL_RA_RACE",
  "columns": [
    {"name": "idYear", "type": "VARCHAR"},
    {"name": "idJyoCD", "type": "VARCHAR"},
    {"name": "GradeCD", "type": "VARCHAR"}
  ]
}
```

LLMは「idJyoCD」が何を意味するか推測するしかない → **誤ったクエリ生成**

### After（説明付き）

```json
{
  "table_name": "NL_RA_RACE",
  "table_description": "レース情報テーブル - 各レースの基本情報、条件、グレード等",
    "primary_keys": ["idYear", "idMonthDay", "idJyoCD", "idKaiji", "idNichiji", "idRaceNum"],
  "total_columns": 110,
  "columns": [
    {
      "name": "idYear",
      "type": "VARCHAR",
      "description": "開催年（YYYY形式）"
    },
    {
      "name": "idJyoCD",
      "type": "VARCHAR",
      "description": "競馬場コード（01=札幌, 02=函館, 03=福島, 04=新潟, 05=東京, 06=中山, 07=中京, 08=京都, 09=阪神, 10=小倉）"
    },
    {
      "name": "GradeCD",
      "type": "VARCHAR",
      "description": "グレードコード（A=G1, B=G2, C=G3, D=リステッド, etc.）"
    }
  ],
  "query_hints": "..."
}
```

LLMは各カラムの意味を正確に理解 → **正確なクエリ生成**

## 説明が追加されているテーブル

| テーブル名 | 説明 | 主要カラム説明数 |
|-----------|------|--------------|
| **NL_RA_RACE** | レース情報 | 20カラム |
| **NL_SE_RACE_UMA** | 出馬表 | 25カラム |
| **NL_UM_UMA** | 馬マスタ | 18カラム |
| **NL_KS_KISYU** | 騎手マスタ | 7カラム |
| **NL_CH_CHOKYOSI** | 調教師マスタ | 5カラム |

### 説明されている内容の例

#### 競馬特有の用語

- `Ninki`: "人気順位（確定後、1=1番人気）"
- `LastTime`: "上がり3Fタイム（SSf形式、例：345=34秒5）"
- `SibaBabaCD`: "芝馬場状態コード（1=良, 2=稍重, 3=重, 4=不良）"

#### コード値の説明

- `GradeCD`: "A=G1, B=G2, C=G3, D=リステッド, E=オープン特別..."
- `idJyoCD`: "01=札幌, 02=函館, ..., 10=小倉"
- `JyokenInfoSyubetuCD`: "11=芝, 21=ダート, 23=障害芝, 24=障害ダート"

#### データ形式の説明

- `Time`: "走破タイム（MMSSf形式、例：010435=1分04秒35）"
- `Futan`: "斤量（kg、55.0のように小数点1桁）"
- `KettoNum`: "血統登録番号（10桁、馬の一意識別子）"

## クエリ生成ヒント

主要テーブル（NL_RA_RACE, NL_SE_RACE_UMA）には、よく使うクエリパターンも含まれています：

### 結合パターン

```sql
-- レース情報 + 出馬表
FROM NL_RA_RACE r
JOIN NL_SE_RACE_UMA s
  ON r.idYear = s.idYear
  AND r.idMonthDay = s.idMonthDay
  AND r.idJyoCD = s.idJyoCD
  AND r.idKaiji = s.idKaiji
  AND r.idNichiji = s.idNichiji
  AND r.idRaceNum = s.idRaceNum
```

### よくある条件

- **東京競馬場の芝1600m**: `idJyoCD = '05' AND TrackInfoKyori = 1600 AND JyokenInfoSyubetuCD = '11'`
- **G1レース**: `GradeCD = 'A'`
- **1番人気**: `Ninki = 1`
- **過去3年**: `idYear >= strftime('%Y', date('now', '-3 years'))`

## LLMでの効果

### Before: 曖昧なクエリ

```
ユーザー: 「東京競馬場のG1レースを検索して」
LLM: どのカラムが競馬場を表すか不明...
     -> 誤ったクエリ or 質問を返す
```

### After: 正確なクエリ

```
ユーザー: 「東京競馬場のG1レースを検索して」
LLM: schema_descriptions を参照
     - idJyoCD = '05'  (説明: 05=東京)
     - GradeCD = 'A'   (説明: A=G1)
     -> 正確なクエリ生成！

SELECT *
FROM NL_RA_RACE
WHERE idJyoCD = '05' AND GradeCD = 'A'
```

## 今後の拡張

### 追加予定の説明

- [ ] NL_HC_HANRO (斤量)
- [ ] NL_WC_WOOD (調教)
- [ ] NL_JG_JOGAIBA (馬場情報)
- [ ] NL_HR_PAY (払戻金)
- [ ] NL_BN_BANUSI (馬主)

### 拡張機能

- [ ] setting.xml からスキーマ説明を自動取得
- [ ] データサンプルの表示
- [ ] カラム値の分布情報
- [ ] 外部キー関係の可視化

## 貢献方法

新しいカラムの説明を追加する場合：

1. `schema_descriptions.py` の `COLUMN_DESCRIPTIONS` を編集
2. テーブル名とカラム名をキーに説明を追加
3. できるだけ具体的な例を含める

```python
"NL_RA_RACE": {
    "new_column": "説明（例を含めると良い、例：1600=1600m）",
}
```

## 参考資料

- JRA-VAN Data Lab: https://jra-van.jp/
- マニュアル
- JVLink 仕様書
