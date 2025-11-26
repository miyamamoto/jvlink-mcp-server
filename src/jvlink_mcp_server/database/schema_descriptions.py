"""JVLink Database Schema Descriptions (jrvltsql版)

カラムごとの詳細な説明を提供します。
LLMがより正確にクエリを生成できるようにするための情報です。
"""

from .schema_auto_descriptions import generate_column_description as auto_generate

# テーブルの説明
TABLE_DESCRIPTIONS = {
    "NL_RA": {
        "description": "レース情報テーブル - 各レースの基本情報、条件、グレード等",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_SE": {
        "description": "出馬表テーブル - レース出走馬情報、結果、オッズ、枠番等",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_UM": {
        "description": "馬マスタテーブル - 馬の基本情報、血統、生産者等（注意: データパース不整合の可能性あり）",
        "primary_keys": [],  # 注意: KettoNumカラムは実際には存在しない
    },
    "NL_KS": {
        "description": "騎手マスタテーブル - 騎手の基本情報",
        "primary_keys": ["KisyuCode"],
    },
    "NL_CH": {
        "description": "調教師マスタテーブル - 調教師の基本情報",
        "primary_keys": ["ChokyosiCode"],
    },
    "NL_HR": {
        "description": "払戻テーブル - レースの払戻情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_O1": {
        "description": "単勝・複勝オッズテーブル",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
}

# カラムの説明（主要カラムのみ）
COLUMN_DESCRIPTIONS = {
    # === NL_RA (レース情報) ===
    "NL_RA": {
        "Year": "開催年（YYYY形式）",
        "MonthDay": "開催月日（MMDD形式）",
        "JyoCD": "競馬場コード（01=札幌, 02=函館, 03=福島, 04=新潟, 05=東京, 06=中山, 07=中京, 08=京都, 09=阪神, 10=小倉）",
        "Kaiji": "開催回次（第何回開催か）",
        "Nichiji": "開催日次（何日目か）",
        "RaceNum": "レース番号（1-12）",
        "Hondai": "レース正式名称（例：日本ダービー）",
        "Fukudai": "レース副題",
        "Kakko": "レースカッコ内表記",
        "GradeCD": "グレードコード（A=G1, B=G2, C=G3, D=リステッド, etc.）",
        "SyubetuCD": "競走種別コード（11=芝, 21=ダート, 23=障害芝, 24=障害ダート）",
        "KigoCD": "競走記号コード",
        "JyuryoCD": "重量種別コード（1=ハンデ, 2=別定, 3=馬齢, 4=定量）",
        "Kyori": "距離（メートル単位、例：1600）",
        "TrackCD": "トラックコード（10=芝・右, 11=芝・左, 18=芝・直, 20=ダート・右, etc.）",
        "HassoTime": "発走時刻（HHmm形式）",
        "TorokuTosu": "登録頭数",
        "SyussoTosu": "出走頭数",
    },

    # === NL_SE (出馬表) ===
    "NL_SE": {
        "Umaban": "馬番",
        "Wakuban": "枠番",
        "KettoNum": "血統登録番号（馬の一意識別子）",
        "Bamei": "馬名",
        "SexCD": "性別コード（1=牡, 2=牝, 3=セン）",
        "Barei": "馬齢",
        "KisyuCode": "騎手コード",
        "KisyuRyakusyo": "騎手名略称",
        "ChokyosiCode": "調教師コード",
        "ChokyosiRyakusyo": "調教師名略称",
        "Futan": "斤量（kg）",
        "Ninki": "★人気順位（ゼロパディング2桁: '01'=1番人気。'1'ではなく'01'を使用）",
        "Odds": "単勝オッズ",
        "ZogenFugo": "増減記号（+, -, ±）",
        "ZogenSa": "増減差（馬体重の増減、kg）",
        "IJyoCD": "異常区分コード（取消、除外、中止など）",
        "KakuteiJyuni": "★確定着順（ゼロパディング2桁: '01'=1着,'02'=2着。'1'ではなく'01'を使用）",
        "Time": "走破タイム（MMSSf形式、例：010435=1分04秒35）",
        "ChakusaCD": "着差コード（1=ハナ, 2=クビ, 3=1/2馬身, etc.）",
        "HaronTimeL3": "上がり3Fタイム",
        "Jyuni1c": "1コーナー通過順位",
        "Jyuni2c": "2コーナー通過順位",
        "Jyuni3c": "3コーナー通過順位",
        "Jyuni4c": "4コーナー通過順位",
        "BaTaijyu": "馬体重（kg）",
        "Bamei1": "父馬ID（血統登録番号形式、例:'2021103912'）- 馬名ではなくIDが格納されている",
        "Bamei2": "母馬ID（血統登録番号形式）- 現状'0000'等のダミー値が多い",
        "Bamei3": "母父馬ID（血統登録番号形式）- 現状'0'等のダミー値が多い",
    },

    # === NL_UM (馬マスタ) ===
    "NL_UM": {
        "KettoNum": "血統登録番号（10桁、馬の一意識別子）",
        "Bamei": "馬名（カタカナ）",
        "BameiKana": "馬名カナ",
        "BameiEng": "馬名英字",
        "SexCD": "性別コード（1=牡, 2=牝, 3=セン）",
        "KeiroCD": "毛色コード",
        "BirthDate": "誕生日",
        "SanchiName": "産地名",
        "BreederName": "生産者名",
        "BanusiName": "馬主名",
        "ChokyosiCode": "所属調教師コード",
        "ChokyosiRyakusyo": "調教師略称",
        "Ketto3InfoBamei1": "父馬名",
        "Ketto3InfoBamei2": "母馬名",
        "Ketto3InfoBamei3": "父父馬名",
        "Ketto3InfoBamei4": "父母馬名",
        "Ketto3InfoBamei5": "母父馬名",
        "Ketto3InfoBamei6": "母母馬名",
    },

    # === NL_KS (騎手マスタ) ===
    "NL_KS": {
        "KisyuCode": "騎手コード",
        "KisyuName": "騎手名",
        "KisyuNameKana": "騎手名カナ",
        "KisyuRyakusyo": "騎手名略称",
        "TozaiCD": "東西コード（1=美浦, 2=栗東）",
    },

    # === NL_CH (調教師マスタ) ===
    "NL_CH": {
        "ChokyosiCode": "調教師コード",
        "ChokyosiName": "調教師名",
        "ChokyosiNameKana": "調教師名カナ",
        "ChokyosiRyakusyo": "調教師名略称",
        "TozaiCD": "東西コード（1=美浦, 2=栗東）",
    },
}

# コード値の説明
CODE_MAPPINGS = {
    "競馬場コード": {
        "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
        "05": "東京", "06": "中山", "07": "中京", "08": "京都",
        "09": "阪神", "10": "小倉",
    },
    "グレードコード": {
        "A": "G1（最高グレード）", "B": "G2", "C": "G3",
        "D": "リステッド競走", "E": "オープン特別",
        "F": "3勝クラス", "G": "2勝クラス", "H": "1勝クラス",
        "I": "未勝利", "J": "新馬",
    },
    "競走種別コード": {
        "11": "芝（平地）", "21": "ダート（平地）",
        "23": "障害・芝", "24": "障害・ダート",
    },
    "馬場状態コード": {
        "1": "良（ベストコンディション）", "2": "稍重（やや重い、乾燥不足）",
        "3": "重（重い、水分多い）", "4": "不良（最悪、大量の水分）",
    },
    "性別コード": {
        "1": "牡馬（オスの馬）", "2": "牝馬（メスの馬）", "3": "セン馬（去勢された牡馬）",
    },
}

# LLM向けのクエリ生成ヒント
QUERY_GENERATION_HINTS = """
## JVLinkデータベースでのクエリ生成ヒント

### 主要な結合パターン

1. **レース情報 + 出馬表**
```sql
SELECT *
FROM NL_RA r
JOIN NL_SE s
  ON r.Year = s.Year
  AND r.MonthDay = s.MonthDay
  AND r.JyoCD = s.JyoCD
  AND r.Kaiji = s.Kaiji
  AND r.Nichiji = s.Nichiji
  AND r.RaceNum = s.RaceNum
```

2. **出馬表 + 馬マスタ**
```sql
SELECT *
FROM NL_SE s
JOIN NL_UM u ON s.KettoNum = u.KettoNum
```

3. **出馬表 + 騎手マスタ**
```sql
SELECT *
FROM NL_SE s
JOIN NL_KS k ON s.KisyuCode = k.KisyuCode
```

### よくある条件

- **東京競馬場の芝1600m**: `JyoCD = '05' AND Kyori = '1600' AND SyubetuCD = '11'`
- **G1レース**: `GradeCD = 'A'`
- **1番人気**: `Ninki = '01'`
- **過去3年**: `Year >= strftime('%Y', date('now', '-3 years'))`

### 注意事項

- すべてのカラムがTEXT型です（数値比較時は注意）
- 日付は文字列型（Year, MonthDay）なので文字列比較になります
- 距離もTEXT型（'1600', '2000'など）
- 着順0は「着外」「取消」「除外」を意味します

### データ品質に関する注意

- **NL_SE.Bamei1/2/3**: 馬名ではなくID（血統登録番号）が格納されています
- **NL_UM**: KettoNumカラムが存在せず、データのパースに問題がある可能性があります
- **血統分析**: NL_SEのBamei1/2/3とNL_UMの結合は現状困難です
- **種牡馬成績**: NL_SEのBamei1（父馬ID）でGROUP BYして分析可能ですが、馬名は取得できません
"""


def get_column_description(table_name: str, column_name: str) -> str:
    """カラムの説明を取得"""
    if table_name in COLUMN_DESCRIPTIONS:
        manual_desc = COLUMN_DESCRIPTIONS[table_name].get(column_name, "")
        if manual_desc:
            return manual_desc
    return auto_generate(table_name, column_name)


def get_table_description(table_name: str) -> dict:
    """テーブルの説明を取得"""
    return TABLE_DESCRIPTIONS.get(table_name, {
        "description": "（説明未登録）",
        "primary_keys": [],
    })
