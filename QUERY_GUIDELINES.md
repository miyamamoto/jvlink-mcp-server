# クエリ作成ガイドライン (jrvltsql版)

Claude Code経由でMCPサーバーを使用する際の重要な注意点とベストプラクティス

## テーブル名の変更

jrvltsql版では旧JVLinkToSQLiteとテーブル名が異なります：

| 旧テーブル名 | 新テーブル名 | 説明 |
|-------------|-------------|------|
| NL_RA_RACE | NL_RA | レース情報 |
| NL_SE_RACE_UMA | NL_SE | 出馬表・結果 |
| NL_UM_UMA | NL_UM | 馬マスタ |
| NL_KS_KISYU | NL_KS | 騎手マスタ |
| NL_CH_CHOKYOSI | NL_CH | 調教師マスタ |

## カラム名の変更

| 旧カラム名 | 新カラム名 | 説明 |
|-----------|-----------|------|
| idYear | Year | 開催年 |
| idMonthDay | MonthDay | 開催月日 |
| idJyoCD | JyoCD | 競馬場コード |
| idKaiji | Kaiji | 開催回 |
| idNichiji | Nichiji | 開催日 |
| idRaceNum | RaceNum | レース番号 |
| RaceInfoHondai | Hondai | レース名本題 |
| Ketto3Info1Bamei | Ketto3InfoBamei1 | 父馬名 |

## 発見されたデータ形式の注意点

### 1. 人気（Ninki）カラムの形式

**誤**: `WHERE Ninki = '1'`
**正**: `WHERE Ninki = '01'`

人気は2桁のゼロ埋め文字列で格納されています。

```sql
-- 正しい例
SELECT * FROM NL_SE
WHERE Ninki = '01'  -- 1番人気

SELECT * FROM NL_SE
WHERE Ninki = '02'  -- 2番人気
```

### 2. グレードコード（GradeCD）のフィルタリング

**誤**: `WHERE GradeCD IS NOT NULL`
**正**: `WHERE GradeCD IN ('A', 'B', 'C')`

GradeCDの値：
- `A` = G1
- `B` = G2
- `C` = G3
- `D`, `E`, `F`, `G`, `H`, `I`, `J` = その他のクラス

重賞のみを対象にする場合は明示的に指定します：

```sql
-- 重賞（G1, G2, G3）のみ
SELECT * FROM NL_RA
WHERE GradeCD IN ('A', 'B', 'C')

-- G1のみ
SELECT * FROM NL_RA
WHERE GradeCD = 'A'
```

### 3. 種牡馬名の表記

種牡馬名は実際のデータベース内の表記と完全に一致させる必要があります。

**データに存在する種牡馬名の確認方法**：

```sql
-- 産駒数が多い種牡馬トップ20
SELECT
    Ketto3InfoBamei1 as sire,
    COUNT(*) as progeny_count
FROM NL_UM
WHERE Ketto3InfoBamei1 IS NOT NULL
    AND Ketto3InfoBamei1 != ''
GROUP BY Ketto3InfoBamei1
ORDER BY progeny_count DESC
LIMIT 20
```

### 4. 確定着順（KakuteiJyuni）のフィルタリング

レース結果のみを対象にする場合：

```sql
WHERE KakuteiJyuni IS NOT NULL
    AND LENGTH(KakuteiJyuni) > 0
```

1着のみ：

```sql
WHERE KakuteiJyuni = '01'
```

### 5. JOIN時の注意点

NL_SEとNL_RAをJOINする際の正しい方法：

```sql
SELECT ...
FROM NL_SE se
JOIN NL_RA ra ON
    se.Year = ra.Year
    AND se.MonthDay = ra.MonthDay
    AND se.JyoCD = ra.JyoCD
    AND se.Kaiji = ra.Kaiji
    AND se.Nichiji = ra.Nichiji
    AND se.RaceNum = ra.RaceNum
```

全6カラムでJOINする必要があります。

## テスト済みクエリパターン

### パターン1: 馬の戦績検索

```sql
SELECT
    se.Year || '-' || SUBSTR(se.MonthDay, 1, 2) || '-' || SUBSTR(se.MonthDay, 3, 2) as date,
    se.KakuteiJyuni as finish,
    se.Ninki as popularity,
    ra.GradeCD as grade
FROM NL_SE se
LEFT JOIN NL_RA ra ON
    se.Year = ra.Year AND se.MonthDay = ra.MonthDay AND
    se.JyoCD = ra.JyoCD AND se.Kaiji = ra.Kaiji AND
    se.Nichiji = ra.Nichiji AND se.RaceNum = ra.RaceNum
WHERE se.Bamei LIKE '%馬名%'
    AND se.KakuteiJyuni IS NOT NULL
    AND LENGTH(se.KakuteiJyuni) > 0
ORDER BY se.Year DESC, se.MonthDay DESC
LIMIT 10
```

### パターン2: 騎手の成績（競馬場別）

```sql
SELECT
    se.JyoCD as track_code,
    COUNT(*) as rides,
    SUM(CASE WHEN se.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
    ROUND(CAST(SUM(CASE WHEN se.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
FROM NL_SE se
WHERE se.KisyuRyakusyo LIKE '%騎手名%'
    AND se.KakuteiJyuni IS NOT NULL
    AND LENGTH(se.KakuteiJyuni) > 0
    AND se.Year >= '2023'
GROUP BY se.JyoCD
ORDER BY wins DESC
```

### パターン3: 人気別成績（クラス別）

```sql
SELECT
    ra.GradeCD as grade,
    COUNT(*) as total_races,
    SUM(CASE WHEN se.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
    ROUND(CAST(SUM(CASE WHEN se.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
FROM NL_SE se
JOIN NL_RA ra ON
    se.Year = ra.Year AND se.MonthDay = ra.MonthDay AND
    se.JyoCD = ra.JyoCD AND se.Kaiji = ra.Kaiji AND
    se.Nichiji = ra.Nichiji AND se.RaceNum = ra.RaceNum
WHERE se.Ninki = '01'  -- 1番人気
    AND se.KakuteiJyuni IS NOT NULL
    AND LENGTH(se.KakuteiJyuni) > 0
    AND ra.GradeCD IN ('A', 'B', 'C')  -- 重賞のみ
    AND se.Year >= '2023'
GROUP BY ra.GradeCD
ORDER BY grade
```

### パターン4: コース・距離別成績（枠順別）

```sql
SELECT
    se.Wakuban as frame,
    COUNT(*) as runs,
    SUM(CASE WHEN se.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
    ROUND(CAST(SUM(CASE WHEN se.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
FROM NL_SE se
JOIN NL_RA ra ON
    se.Year = ra.Year AND se.MonthDay = ra.MonthDay AND
    se.JyoCD = ra.JyoCD AND se.Kaiji = ra.Kaiji AND
    se.Nichiji = ra.Nichiji AND se.RaceNum = ra.RaceNum
WHERE ra.JyoCD = '05'  -- 東京
    AND ra.TrackCD LIKE '1%'  -- 芝
    AND ra.Kyori = '1600'  -- 1600m
    AND se.KakuteiJyuni IS NOT NULL
    AND LENGTH(se.KakuteiJyuni) > 0
    AND se.Wakuban IS NOT NULL
    AND se.Year >= '2022'
GROUP BY se.Wakuban
ORDER BY se.Wakuban
```

## よくある間違いと修正方法

| 間違い | 正しい方法 | 理由 |
|--------|-----------|------|
| `NL_RA_RACE` | `NL_RA` | テーブル名変更 |
| `NL_SE_RACE_UMA` | `NL_SE` | テーブル名変更 |
| `idYear` | `Year` | カラム名変更 |
| `Ninki = '1'` | `Ninki = '01'` | 2桁ゼロ埋め |
| `KakuteiJyuni = '1'` | `KakuteiJyuni = '01'` | 2桁ゼロ埋め |
| `Ketto3Info1Bamei` | `Ketto3InfoBamei1` | カラム名変更 |

## 血統情報の取得方法

### NL_SEとNL_UMのJOIN

血統情報（父馬名、母馬名等）を取得するには、NL_UMテーブルとKettoNumでJOINします：

```sql
SELECT 
    s.Bamei as 馬名,
    u.Ketto3InfoBamei1 as 父馬名,
    u.Ketto3InfoBamei2 as 母馬名,
    u.Ketto3InfoBamei5 as 母父馬名
FROM NL_SE s
LEFT JOIN NL_UM u ON s.KettoNum = u.KettoNum
WHERE s.KakuteiJyuni IS NOT NULL
```

**マッチング率**: 約85.5%（67,245 / 78,605件）

### 種牡馬成績分析

```sql
SELECT 
    u.Ketto3InfoBamei1 as 種牡馬,
    COUNT(*) as 出走数,
    SUM(CASE WHEN s.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as 勝利数,
    ROUND(SUM(CASE WHEN s.KakuteiJyuni = '01' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1) as 勝率
FROM NL_SE s
JOIN NL_UM u ON s.KettoNum = u.KettoNum
WHERE s.KakuteiJyuni IS NOT NULL AND s.KakuteiJyuni != ''
GROUP BY u.Ketto3InfoBamei1
HAVING COUNT(*) >= 100
ORDER BY 勝利数 DESC
LIMIT 20
```

### ⚠️ NL_SE.Bamei1カラムについて

**注意**: NL_SE.Bamei1カラムは**父馬名ではありません**。
- Bamei1にはKettoNum1が参照する馬の名前が入っています（父馬ではない）
- **Bamei2, Bamei3カラムは存在しません**
- 血統情報は必ずNL_UMテーブルを使用してください

## データ型について

jrvltsqlでは**すべてのカラムがTEXT型**です。数値比較を行う場合は注意：

```sql
-- 距離での比較
WHERE CAST(Kyori AS INTEGER) >= 1600

-- または文字列比較（ゼロ埋めされている場合）
WHERE Kyori >= '1600'
```

## データ範囲の確認方法

現在のデータ範囲を確認：

```sql
SELECT
    MIN(Year) as min_year,
    MAX(Year) as max_year,
    COUNT(DISTINCT Year) as year_count,
    COUNT(*) as total_races
FROM NL_RA
```

---

**作成日**: 2025-11-27
**対象DB**: jrvltsql (keiba.db)
