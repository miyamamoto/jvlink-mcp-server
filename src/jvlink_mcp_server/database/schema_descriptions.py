"""JVLink Database Schema Descriptions

カラムごとの詳細な説明を提供します。
LLMがより正確にクエリを生成できるようにするための情報です。
"""

from .schema_auto_descriptions import generate_column_description as auto_generate

# テーブルの説明
TABLE_DESCRIPTIONS = {
    "NL_RA_RACE": {
        "description": "レース情報テーブル - 各レースの基本情報、条件、グレード等",
                "primary_keys": ["idYear", "idMonthDay", "idJyoCD", "idKaiji", "idNichiji", "idRaceNum"],
    },
    "NL_SE_RACE_UMA": {
        "description": "出馬表テーブル - レース出走前の馬情報、オッズ、枠番等",
                "primary_keys": ["idYear", "idMonthDay", "idJyoCD", "idKaiji", "idNichiji", "idRaceNum", "idUmaban"],
    },
    "NL_UM_UMA": {
        "description": "馬マスタテーブル - 馬の基本情報、血統、生産者等",
                "primary_keys": ["KettoNum"],
    },
    "NL_KS_KISYU": {
        "description": "騎手マスタテーブル - 騎手の基本情報",
                "primary_keys": ["KisyuCode"],
    },
    "NL_CH_CHOKYOSI": {
        "description": "調教師マスタテーブル - 調教師の基本情報",
                "primary_keys": ["ChokyosiCode"],
    },
}

# カラムの説明（主要カラムのみ）
COLUMN_DESCRIPTIONS = {
    # === NL_RA_RACE (レース情報) ===
    "NL_RA_RACE": {
        "idYear": "開催年（YYYY形式）",
        "idMonthDay": "開催月日（MMDD形式）",
        "idJyoCD": "競馬場コード（01=札幌, 02=函館, 03=福島, 04=新潟, 05=東京, 06=中山, 07=中京, 08=京都, 09=阪神, 10=小倉）",
        "idKaiji": "開催回次（第何回開催か）",
        "idNichiji": "開催日次（何日目か）",
        "idRaceNum": "レース番号（1-12）",
        "RaceInfoHondai": "レース正式名称（例：日本ダービー）",
        "RaceInfoFukudai": "レース副題",
        "RaceInfoKakko": "レースカッコ内表記",
        "GradeCD": "グレードコード（A=G1, B=G2, C=G3, D=リステッド, etc.）",
        "JyokenInfoSyubetuCD": "競走種別コード（11=芝, 21=ダート, 23=障害芝, 24=障害ダート）",
        "JyokenInfoKigoCD": "競走記号コード（000=平地, 051=障害など）",
        "JyokenInfoJyuryoCD": "重量種別コード（1=ハンデ, 2=別定, 3=馬齢, 4=定量）",
        "Kyori": "距離（メートル単位、例：1600）",
        "TrackCD": "トラックコード（10=芝・右, 11=芝・左, 18=芝・直, 20=ダート・右, etc.）",
        "TrackInfoKaisaiKubunCD": "開催区分コード（通常/冬季）",
        "TenkoBabaTenkoCD": "天候コード（1=晴, 2=曇, 3=雨, 4=小雨, etc.）",
        "TenkoBabaSibaBabaCD": "芝馬場状態コード（1=良, 2=稍重, 3=重, 4=不良）",
        "TenkoBabaDirtBabaCD": "ダート馬場状態コード（1=良, 2=稍重, 3=重, 4=不良）",
        "HassoTime": "発走時刻（HHmm形式）",
        "TorokiTosu": "登録頭数",
        "SyussoTosu": "出走頭数",
        "NyusenTosu": "入線頭数",
        "TorokuJyotaiFlag1": "登録状態フラグ（レース確定状態など）",
    },

    # === NL_SE_RACE_UMA (出馬表) ===
    "NL_SE_RACE_UMA": {
        "idUmaban": "馬番",
        "KettoNum": "血統登録番号（馬の一意識別子）",
        "Bamei": "馬名",
        "WakuBan": "枠番",
        "KisyuCode": "騎手コード",
        "KisyuName": "騎手名",
        "ChokyosiCode": "調教師コード",
        "ChokyosiName": "調教師名",
        "Futan": "斤量（kg、55.0のように小数点1桁）",
        "Ninki": "人気順位（確定後、1=1番人気）",
        "OddsWin": "単勝オッズ",
        "OddsPlace": "複勝オッズ",
        "ZogenFugo": "増減記号（+, -, ±）",
        "ZogenSa": "増減差（馬体重の増減、kg）",
        "IJyoCD": "異常区分コード（取消、除外、中止など）",
        "KakuteiJyuni": "確定着順（1=1着、0=着外）",
        "Time": "走破タイム（MMSSf形式、例：010435=1分04秒35）",
        "ChakusaCD": "着差コード（1=ハナ, 2=クビ, 3=1/2馬身, etc.）",
        "ChakusaCDP": "前走との着差コード",
        "LastTime": "上がり3Fタイム（SSf形式、例：345=34秒5）",
        "TsukaKyori1": "通過順位1コーナー",
        "TsukaKyori2": "通過順位2コーナー",
        "TsukaKyori3": "通過順位3コーナー",
        "TsukaKyori4": "通過順位4コーナー",
        "BaTaijyu": "馬体重（kg）",
    },

    # === NL_UM_UMA (馬マスタ) ===
    "NL_UM_UMA": {
        "KettoNum": "血統登録番号（10桁、馬の一意識別子）",
        "Bamei": "馬名（カタカナ）",
        "BameiKana": "馬名カナ",
        "BameiEng": "馬名英字",
        "Seibetsu": "性別コード（1=牡, 2=牝, 3=セン）",
        "Keiro": "毛色コード（1=栗毛, 2=栃栗毛, etc.）",
        "SanchiName": "産地名",
        "BreederName": "生産者名",
        "BanusiName": "馬主名",
        "ChokyosiCode": "所属調教師コード",
        "ChokyosiRyakusyo": "調教師略称",
        "Fukuso": "父血統登録番号",
        "FBamei": "父馬名",
        "BokuroBamei": "母馬名",
        "HahaSideSeibetsu": "母父血統登録番号",
        "BBamei": "母父馬名",
        "Tanjyobi": "誕生日（YYYYMMDDまたはYYYY形式）",
        "SyotokuSyokinTotal": "総賞金（千円単位）",
        "HonSyokin": "本賞金（千円単位）",
        "FukaSyokin": "付加賞金（千円単位）",
    },

    # === NL_KS_KISYU (騎手マスタ) ===
    "NL_KS_KISYU": {
        "KisyuCode": "騎手コード（5桁）",
        "KisyuName": "騎手名",
        "KisyuNameKana": "騎手名カナ",
        "Seibetsu": "性別コード（1=男性, 2=女性）",
        "SyozokuCD": "所属コード（1=JRA, 2=地方, 3=海外）",
        "SyozokuName": "所属名称",
        "IkkatuKey": "一括キー（見習い区分など）",
    },

    # === NL_CH_CHOKYOSI (調教師マスタ) ===
    "NL_CH_CHOKYOSI": {
        "ChokyosiCode": "調教師コード（5桁）",
        "ChokyosiName": "調教師名",
        "ChokyosiNameKana": "調教師名カナ",
        "SyozokuCD": "所属コード（1=美浦, 2=栗東）",
        "SyozokuName": "所属トレセン名",
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
        "A": "G1（最高グレード）",
        "B": "G2",
        "C": "G3",
        "D": "リステッド競走",
        "E": "オープン特別",
        "F": "1600万円以下",
        "G": "1000万円以下",
        "H": "500万円以下",
        "I": "未勝利",
        "J": "新馬",
    },
    "競走種別コード": {
        "11": "芝（平地）",
        "21": "ダート（平地）",
        "23": "障害・芝",
        "24": "障害・ダート",
    },
    "馬場状態コード": {
        "1": "良（ベストコンディション）",
        "2": "稍重（やや重い、乾燥不足）",
        "3": "重（重い、水分多い）",
        "4": "不良（最悪、大量の水分）",
    },
    "性別コード": {
        "1": "牡馬（オスの馬）",
        "2": "牝馬（メスの馬）",
        "3": "セン馬（去勢された牡馬）",
    },
}

# LLM向けのクエリ生成ヒント
QUERY_GENERATION_HINTS = """
## JVLinkデータベースでのクエリ生成ヒント

### 主要な結合パターン

1. **レース情報 + 出馬表**
```sql
SELECT *
FROM NL_RA_RACE r
JOIN NL_SE_RACE_UMA s
  ON r.idYear = s.idYear
  AND r.idMonthDay = s.idMonthDay
  AND r.idJyoCD = s.idJyoCD
  AND r.idKaiji = s.idKaiji
  AND r.idNichiji = s.idNichiji
  AND r.idRaceNum = s.idRaceNum
```

2. **出馬表 + 馬マスタ**
```sql
SELECT *
FROM NL_SE_RACE_UMA s
JOIN NL_UM_UMA u ON s.KettoNum = u.KettoNum
```

3. **出馬表 + 騎手マスタ**
```sql
SELECT *
FROM NL_SE_RACE_UMA s
JOIN NL_KS_KISYU k ON s.KisyuCode = k.KisyuCode
```

### よくある条件

- **東京競馬場の芝1600m**: `idJyoCD = '05' AND Kyori = 1600 AND JyokenInfoSyubetuCD = '11'`
- **G1レース**: `GradeCD = 'A'`
- **1番人気**: `Ninki = 1`
- **良馬場（芝）**: `TenkoBabaSibaBabaCD = '1'`
- **過去3年**: `idYear >= strftime('%Y', date('now', '-3 years'))`

### 注意事項

- 日付は文字列型（idYear, idMonthDay）なので文字列比較になります
- 距離はメートル単位（1600, 2000など）
- オッズは小数点を含む文字列の場合があります
- 着順0は「着外」「取消」「除外」を意味します
"""


def get_column_description(table_name: str, column_name: str) -> str:
    """カラムの説明を取得

    Args:
        table_name: テーブル名
        column_name: カラム名

    Returns:
        カラムの説明（手動説明 > 自動生成の順に優先）
    """
    # 手動で定義された説明を優先
    if table_name in COLUMN_DESCRIPTIONS:
        manual_desc = COLUMN_DESCRIPTIONS[table_name].get(column_name, "")
        if manual_desc:
            return manual_desc

    # 自動生成をフォールバック
    return auto_generate(table_name, column_name)


def get_table_description(table_name: str) -> dict:
    """テーブルの説明を取得

    Args:
        table_name: テーブル名

    Returns:
        テーブルの説明辞書
    """
    return TABLE_DESCRIPTIONS.get(table_name, {
        "description": "（説明未登録）",
                "primary_keys": [],
    })
