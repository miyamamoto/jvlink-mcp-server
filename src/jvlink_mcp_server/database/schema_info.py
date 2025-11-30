"""JVLinkデータベースのスキーマ情報（jrvltsql版）

重要: jrvltsql v2.0以降では適切な型が使用されています。
- INTEGER: 着順、人気、馬番、枠番、年、距離など
- REAL: オッズ、タイム、馬体重など
- TEXT: コード、名前など
"""

JVLINK_TABLES = {
    "NL_RA": {
        "description": "レース情報テーブル",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
        "key_columns": {
            "Year": "開催年 (INTEGER)",
            "MonthDay": "開催月日 (INTEGER, 例: 1225)",
            "JyoCD": "競馬場コード (TEXT, 01-10)",
            "Hondai": "レース名本題",
            "GradeCD": "グレードコード (A=G1, B=G2, C=G3)",
            "Kyori": "距離（INTEGER, メートル）",
            "TrackCD": "トラックコード（2桁: 1桁目=種別[1=芝,2=ダート], 2桁目=回り）",
            "SibaBabaCD": "芝馬場状態コード (1=良, 2=稍重, 3=重, 4=不良)",
            "DirtBabaCD": "ダート馬場状態コード",
        },
    },
    "NL_SE": {
        "description": "出馬表・レース結果テーブル。血統情報はNL_UMとKettoNumでJOINして取得",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
        "key_columns": {
            "KettoNum": "血統登録番号（NL_UMとJOINするためのキー）",
            "Umaban": "馬番 (INTEGER, 1-18)",
            "Wakuban": "枠番 (INTEGER, 1-8)",
            "Bamei": "馬名",
            "KisyuRyakusyo": "騎手名略称",
            "KakuteiJyuni": "確定着順 (INTEGER, 1=1着, 2=2着...)",
            "Ninki": "人気 (INTEGER, 1=1番人気, 2=2番人気...)",
            "Odds": "単勝オッズ (REAL)",
            "Time": "走破タイム (REAL, 秒)",
            "HaronTimeL3": "上がり3F (REAL, 秒)",
            "BaTaijyu": "馬体重 (REAL, kg)",
            "Futan": "斤量 (REAL, kg)",
            "Barei": "馬齢 (INTEGER)",
            "SexCD": "性別コード (1=牡, 2=牝, 3=セン)",
        },
    },
    "NL_UM": {
        "description": "馬マスタ（JRA中央競馬のみ。地方競馬はJOIN不可）",
        "primary_keys": ["KettoNum"],
        "key_columns": {
            "Bamei": "馬名",
            "Ketto3InfoBamei1": "父馬名",
            "Ketto3InfoBamei2": "母馬名",
            "Ketto3InfoBamei5": "母父馬名",
        },
    },
    "NL_KS": {"description": "騎手マスタ", "primary_keys": ["KisyuCode"], "key_columns": {"KisyuName": "騎手名", "KisyuRyakusyo": "騎手名略称"}},
    "NL_CH": {"description": "調教師マスタ", "primary_keys": ["ChokyosiCode"], "key_columns": {"ChokyosiName": "調教師名", "ChokyosiRyakusyo": "調教師名略称"}},
    "NL_HR": {"description": "払戻テーブル", "primary_keys": [], "key_columns": {}},
    "NL_O1": {"description": "単勝複勝オッズ", "primary_keys": [], "key_columns": {}},
}

TRACK_CODES = {"01": "札幌", "02": "函館", "03": "福島", "04": "新潟", "05": "東京", "06": "中山", "07": "中京", "08": "京都", "09": "阪神", "10": "小倉"}
GRADE_CODES = {"A": "GI", "B": "GII", "C": "GIII", "D": "リステッド", "E": "オープン特別", "F": "3勝クラス", "G": "2勝クラス", "H": "1勝クラス", "I": "未勝利", "J": "新馬"}
TRACK_CONDITION_CODES = {"1": "良", "2": "稍重", "3": "重", "4": "不良"}
TRACK_TYPE_CODES = {"1": "芝", "2": "ダート", "5": "障害"}
SEX_CODES = {"1": "牡", "2": "牝", "3": "セン"}


def get_schema_description():
    return {
        "tables": JVLINK_TABLES,
        "track_codes": TRACK_CODES,
        "grade_codes": GRADE_CODES,
        "important_notes": [
            "KakuteiJyuni(着順)とNinki(人気)はINTEGER型（1, 2, 3...）",
            "Umaban(馬番)とWakuban(枠番)もINTEGER型",
            "JyoCD(競馬場)はTEXT型でゼロパディング（'05'=東京）",
            "Odds, Time, HaronTimeL3, BaTaijyuはREAL型",
            "地方競馬はNL_UMとJOIN不可",
        ],
    }


def get_query_examples():
    return {
        "1番人気勝率": "SELECT COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE Ninki = 1 AND KakuteiJyuni IS NOT NULL",
        "騎手成績": "SELECT KisyuRyakusyo, COUNT(*) as rides, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE KakuteiJyuni IS NOT NULL GROUP BY KisyuRyakusyo ORDER BY wins DESC LIMIT 20",
        "東京1番人気": "SELECT COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE JyoCD = '05' AND Ninki = 1 AND KakuteiJyuni IS NOT NULL",
        "枠番別成績": "SELECT Wakuban, COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE KakuteiJyuni IS NOT NULL GROUP BY Wakuban ORDER BY Wakuban",
        "種牡馬成績": "SELECT u.Ketto3InfoBamei1 as sire, COUNT(*) as runs, SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE s JOIN NL_UM u ON s.KettoNum = u.KettoNum WHERE s.KakuteiJyuni IS NOT NULL GROUP BY u.Ketto3InfoBamei1 HAVING COUNT(*) >= 100 ORDER BY wins DESC LIMIT 20",
    }


def get_target_equivalent_query_examples():
    return get_query_examples()
