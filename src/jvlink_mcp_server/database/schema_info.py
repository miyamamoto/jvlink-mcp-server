"""JVLinkデータベースのスキーマ情報（jrvltsql版）

重要: すべてのカラムはTEXT型です。
数値カラム（着順、人気等）はゼロパディングされた文字列です。
"""

JVLINK_TABLES = {
    "NL_RA": {
        "description": "レース情報テーブル",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
        "key_columns": {
            "Year": "開催年",
            "MonthDay": "開催月日",
            "JyoCD": "競馬場コード (01-10、ゼロパディング)",
            "Hondai": "レース名本題",
            "GradeCD": "グレードコード (A=G1, B=G2, C=G3)",
            "Kyori": "距離（メートル）",
            "TrackCD": "トラックコード（2桁: 1桁目=種別[1=芝,2=ダート], 2桁目=馬場状態）",
        },
    },
    "NL_SE": {
        "description": "出馬表・レース結果テーブル。血統情報はNL_UMとKettoNumでJOINして取得",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
        "key_columns": {
            "KettoNum": "血統登録番号（NL_UMとJOINするためのキー）",
            "Umaban": "馬番（01-18、ゼロパディング）",
            "Wakuban": "枠番（1-8）",
            "Bamei": "馬名",
            "KisyuRyakusyo": "騎手名略称",
            "KakuteiJyuni": "確定着順（01=1着, 02=2着...ゼロパディング2桁）",
            "Ninki": "人気（01=1番人気, 02=2番人気...ゼロパディング2桁）",
            "Odds": "単勝オッズ",
            "HaronTimeL3": "上がり3F（0.1秒単位、例: 334=33.4秒）",
            "BaTaijyu": "馬体重",
            # 注意: Bamei1は対戦相手の馬名（1着馬→2着馬、2着以下→1着馬）。KettoNum1も同様。血統情報はNL_UMを使用
        },
    },
    "NL_UM": {"description": "馬マスタ（JRA中央競馬のみ。地方競馬はJOIN不可）", "primary_keys": ["KettoNum"], "key_columns": {"Bamei": "馬名", "Ketto3InfoBamei1": "父馬名", "Ketto3InfoBamei2": "母馬名", "Ketto3InfoBamei5": "母父馬名"}},
    "NL_KS": {"description": "騎手マスタ", "primary_keys": ["KisyuCode"], "key_columns": {}},
    "NL_CH": {"description": "調教師マスタ", "primary_keys": ["ChokyosiCode"], "key_columns": {}},
    "NL_HR": {"description": "払戻テーブル", "primary_keys": [], "key_columns": {}},
    "NL_O1": {"description": "単勝複勝オッズ", "primary_keys": [], "key_columns": {}},
    "NL_WE": {"description": "馬場状態テーブル（現在データ空、0B11/0B14/0B16 SPEC必要）", "primary_keys": [], "key_columns": {}},
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
            "KakuteiJyuni(着順)とNinki(人気)はゼロパディング2桁（01,02...）",
            "JyoCD(競馬場)もゼロパディング（05=東京）",
            "すべてのカラムはTEXT型",
            "Bamei1/KettoNum1は対戦相手の情報（父馬ではない）",
            "NL_WEテーブルは現在データ空（馬場状態分析不可）",
            "地方競馬はNL_UMとJOIN不可",
        ]
    }

def get_query_examples():
    return {
        "1番人気勝率": "SELECT COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE Ninki = '01' AND KakuteiJyuni IS NOT NULL",
        "騎手成績": "SELECT KisyuRyakusyo, COUNT(*) as rides, SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE KakuteiJyuni IS NOT NULL GROUP BY KisyuRyakusyo ORDER BY wins DESC LIMIT 20",
        "東京1番人気": "SELECT COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE JyoCD = '05' AND Ninki = '01' AND KakuteiJyuni IS NOT NULL",
        "枠番別成績": "SELECT Wakuban, COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE KakuteiJyuni IS NOT NULL GROUP BY Wakuban ORDER BY Wakuban",
        "種牡馬成績": "SELECT u.Ketto3InfoBamei1 as sire, COUNT(*) as runs, SUM(CASE WHEN s.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins FROM NL_SE s JOIN NL_UM u ON s.KettoNum = u.KettoNum WHERE s.KakuteiJyuni IS NOT NULL GROUP BY u.Ketto3InfoBamei1 HAVING COUNT(*) >= 100 ORDER BY wins DESC LIMIT 20",
    }

def get_target_equivalent_query_examples():
    return get_query_examples()