# クエリ作成ガイドライン

Claude Code経由でMCPサーバーを使用する際の重要な注意点とベストプラクティス

## 発見されたデータ形式の注意点

### 1. 人気（Ninki）カラムの形式

**誤**: `WHERE Ninki = '1'`
**正**: `WHERE Ninki = '01'`

人気は2桁のゼロ埋め文字列で格納されています。

```sql
-- 正しい例
SELECT * FROM NL_SE_RACE_UMA
WHERE Ninki = '01'  -- 1番人気

SELECT * FROM NL_SE_RACE_UMA
WHERE Ninki = '02'  -- 2番人気
```

### 2. グレードコード（GradeCD）のフィルタリング

**誤**: `WHERE GradeCD IS NOT NULL`
**正**: `WHERE GradeCD IN ('A', 'B', 'C')`

GradeCDの値：
- `A` = G1
- `B` = G2
- `C` = G3
- `D`, `E`, `F`, `G`, `H`, `L` = その他のクラス

重賞のみを対象にする場合は明示的に指定します：

```sql
-- 重賞（G1, G2, G3）のみ
SELECT * FROM NL_RA_RACE
WHERE GradeCD IN ('A', 'B', 'C')

-- G1のみ
SELECT * FROM NL_RA_RACE
WHERE GradeCD = 'A'
```

### 3. 種牡馬名の表記

種牡馬名は実際のデータベース内の表記と完全に一致させる必要があります。

**データに存在する種牡馬名の確認方法**：

```sql
-- 産駒数が多い種牡馬トップ20
SELECT
    Ketto3Info1Bamei as sire,
    COUNT(*) as progeny_count
FROM NL_UM_UMA
WHERE Ketto3Info1Bamei IS NOT NULL
    AND Ketto3Info1Bamei != ''
GROUP BY Ketto3Info1Bamei
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

NL_SE_RACE_UMAとNL_RA_RACEをJOINする際の正しい方法：

```sql
SELECT ...
FROM NL_SE_RACE_UMA ru
JOIN NL_RA_RACE r ON
    ru.idYear = r.idYear
    AND ru.idMonthDay = r.idMonthDay
    AND ru.idJyoCD = r.idJyoCD
    AND ru.idKaiji = r.idKaiji
    AND ru.idNichiji = r.idNichiji
    AND ru.idRaceNum = r.idRaceNum
```

全6カラムでJOINする必要があります。

## テスト済みクエリパターン

### パターン1: 馬の戦績検索

```sql
SELECT
    ru.idYear || '-' || SUBSTR(ru.idMonthDay, 1, 2) || '-' || SUBSTR(ru.idMonthDay, 3, 2) as date,
    ru.KakuteiJyuni as finish,
    ru.Ninki as popularity,
    r.GradeCD as grade
FROM NL_SE_RACE_UMA ru
LEFT JOIN NL_RA_RACE r ON
    ru.idYear = r.idYear AND ru.idMonthDay = r.idMonthDay AND
    ru.idJyoCD = r.idJyoCD AND ru.idKaiji = r.idKaiji AND
    ru.idNichiji = r.idNichiji AND ru.idRaceNum = r.idRaceNum
WHERE ru.Bamei LIKE '%馬名%'
    AND ru.KakuteiJyuni IS NOT NULL
    AND LENGTH(ru.KakuteiJyuni) > 0
ORDER BY ru.idYear DESC, ru.idMonthDay DESC
LIMIT 10
```

### パターン2: 騎手の成績（競馬場別）

```sql
SELECT
    ru.idJyoCD as track_code,
    COUNT(*) as rides,
    SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
    ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
FROM NL_SE_RACE_UMA ru
WHERE ru.KisyuRyakusyo LIKE '%騎手名%'
    AND ru.KakuteiJyuni IS NOT NULL
    AND LENGTH(ru.KakuteiJyuni) > 0
    AND ru.idYear >= '2023'
GROUP BY ru.idJyoCD
ORDER BY wins DESC
```

### パターン3: 人気別成績（クラス別）

```sql
SELECT
    r.GradeCD as grade,
    COUNT(*) as total_races,
    SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
    ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
FROM NL_SE_RACE_UMA ru
JOIN NL_RA_RACE r ON
    ru.idYear = r.idYear AND ru.idMonthDay = r.idMonthDay AND
    ru.idJyoCD = r.idJyoCD AND ru.idKaiji = r.idKaiji AND
    ru.idNichiji = r.idNichiji AND ru.idRaceNum = r.idRaceNum
WHERE ru.Ninki = '01'  -- 1番人気
    AND ru.KakuteiJyuni IS NOT NULL
    AND LENGTH(ru.KakuteiJyuni) > 0
    AND r.GradeCD IN ('A', 'B', 'C')  -- 重賞のみ
    AND ru.idYear >= '2023'
GROUP BY r.GradeCD
ORDER BY grade
```

### パターン4: コース・距離別成績（枠順別）

```sql
SELECT
    ru.Wakuban as frame,
    COUNT(*) as runs,
    SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
    ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
FROM NL_SE_RACE_UMA ru
JOIN NL_RA_RACE r ON
    ru.idYear = r.idYear AND ru.idMonthDay = r.idMonthDay AND
    ru.idJyoCD = r.idJyoCD AND ru.idKaiji = r.idKaiji AND
    ru.idNichiji = r.idNichiji AND ru.idRaceNum = r.idRaceNum
WHERE r.idJyoCD = '05'  -- 東京
    AND r.TrackCD LIKE '1%'  -- 芝
    AND r.Kyori = '1600'  -- 1600m
    AND ru.KakuteiJyuni IS NOT NULL
    AND LENGTH(ru.KakuteiJyuni) > 0
    AND ru.Wakuban IS NOT NULL
    AND ru.idYear >= '2022'
GROUP BY ru.Wakuban
ORDER BY ru.Wakuban
```

## よくある間違いと修正方法

| 間違い | 正しい方法 | 理由 |
|--------|-----------|------|
| `Ninki = '1'` | `Ninki = '01'` | 2桁ゼロ埋め |
| `KakuteiJyuni = '1'` | `KakuteiJyuni = '01'` | 2桁ゼロ埋め |
| `GradeCD IS NOT NULL` | `GradeCD IN ('A', 'B', 'C')` | 具体的な値で指定 |
| `WHERE Bamei = 'ディープインパクト'` | `WHERE Ketto3Info1Bamei LIKE '%種牡馬名%'` | 馬名と種牡馬名は別カラム |
| LEFT JOIN on 3 columns | LEFT JOIN on 6 columns (all race IDs) | 完全な一意性確保 |

## データ範囲の確認方法

現在のデータ範囲を確認：

```sql
SELECT
    MIN(idYear) as min_year,
    MAX(idYear) as max_year,
    COUNT(DISTINCT idYear) as year_count,
    COUNT(*) as total_races
FROM NL_RA_RACE
```

年別のレース数：

```sql
SELECT idYear, COUNT(*) as race_count
FROM NL_RA_RACE
GROUP BY idYear
ORDER BY idYear DESC
```

## パフォーマンス最適化

### インデックスの活用

以下のカラムでフィルタする場合は効率的：
- `idYear` - 年でフィルタ
- `idJyoCD` - 競馬場でフィルタ
- `Ninki` - 人気でフィルタ
- `KakuteiJyuni` - 着順でフィルタ

### LIMIT句の使用

大量データを扱う場合は必ずLIMIT句を使用：

```sql
SELECT * FROM NL_SE_RACE_UMA
WHERE idYear >= '2020'
LIMIT 1000  -- 結果を制限
```

## トラブルシューティング

### データが0件の場合

1. カラム名のスペルチェック
2. 値の形式確認（ゼロ埋め等）
3. JOINの条件を確認
4. データの実際の値を `SELECT DISTINCT` で確認

### 文字化けする場合

クエリ結果が文字化けする場合は、Pythonスクリプト内で適切なエンコーディング処理を行ってください。

---

**作成日**: 2025-11-11
**テスト実施**: test_questions.py
**成功率**: 100% (7/7 tests passed)
