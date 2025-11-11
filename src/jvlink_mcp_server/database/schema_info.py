"""JVLinkデータベースのスキーマ情報（実際のカラム名版）"""

# JVLinkToSQLiteで作成される主要テーブルの情報
# 注意: カラム名は実際のJVLinkデータ仕様に基づく日本語ローマ字表記

JVLINK_TABLES = {
    "NL_RA_RACE": {
        "description": "レース情報テーブル",
        "target_equivalent": "レース検索画面のデータソース",
        "primary_keys": ["idYear", "idMonthDay", "idJyoCD", "idKaiji", "idNichiji", "idRaceNum"],
        "key_columns": {
            # レースID構成要素
            "idYear": "開催年 (例: 2024)",
            "idMonthDay": "開催月日 (例: 1109 = 11月9日)",
            "idJyoCD": "競馬場コード (01-10)",
            "idKaiji": "開催回",
            "idNichiji": "開催日",
            "idRaceNum": "レース番号",

            # レース詳細
            "RaceInfoHondai": "レース名本題",
            "GradeCD": "グレードコード",
            "Kyori": "距離",
            "TrackCD": "トラック種別 (1=芝, 2=ダート)",

            # 馬場・天候
            "TenkoBabaTenkoCD": "天候コード",
            "TenkoBabaSibaBabaCD": "芝馬場状態",
            "TenkoBabaDirtBabaCD": "ダート馬場状態",
        },
    },

    "NL_SE_RACE_UMA": {
        "description": "出馬表・レース結果テーブル",
        "target_equivalent": "出馬表画面・レース結果画面",
        "primary_keys": ["idYear", "idMonthDay", "idJyoCD", "idKaiji", "idNichiji", "idRaceNum", "Umaban"],
        "key_columns": {
            # レースID構成要素
            "idYear": "開催年",
            "idMonthDay": "開催月日",
            "idJyoCD": "競馬場コード",
            "idKaiji": "開催回",
            "idNichiji": "開催日",
            "idRaceNum": "レース番号",

            # 馬情報
            "Umaban": "馬番",
            "KettoNum": "血統登録番号（馬ID）",
            "Bamei": "馬名",

            # 騎手・調教師
            "KisyuRyakusyo": "騎手名略称",
            "ChokyosiRyakusyo": "調教師名略称",

            # レース結果
            "KakuteiJyuni": "確定着順",
            "Ninki": "人気",
            "Odds": "単勝オッズ",
            "Time": "走破タイム",
            "HaronTimeL3": "後3ハロンタイム",
        },
    },
}

# 競馬場コードマッピング
TRACK_CODES = {
    "01": "札幌",
    "02": "函館",
    "03": "福島",
    "04": "新潟",
    "05": "東京",
    "06": "中山",
    "07": "中京",
    "08": "京都",
    "09": "阪神",
    "10": "小倉",
}

# グレードコードマッピング
GRADE_CODES = {
    "A1": "GⅠ",
    "A2": "GⅡ",
    "A3": "GⅢ",
    "B": "オープン",
}

# 馬場状態マッピング
TRACK_CONDITION_CODES = {
    "1": "良",
    "2": "稍重",
    "3": "重",
    "4": "不良",
}

# トラック種別マッピング
TRACK_TYPE_CODES = {
    "1": "芝",
    "2": "ダート",
}


def get_schema_description() -> dict:
    """スキーマ全体の説明を取得"""
    return {
        "tables": JVLINK_TABLES,
        "track_codes": TRACK_CODES,
        "grade_codes": GRADE_CODES,
        "track_condition_codes": TRACK_CONDITION_CODES,
        "track_type_codes": TRACK_TYPE_CODES,
        "usage_notes": [
            "レース検索は NL_RA_RACE テーブルを使用",
            "出馬表・レース結果は NL_SE_RACE_UMA テーブルを使用",
            "重要: NL_RA_RACE_UMAというテーブルは存在しません",
            "レースIDは複数カラムの組み合わせです",
            "KakuteiJyuniがNULLまたは空の場合はレース前データです",
        ],
        "important_notes": [
            "カラム名は日本語ローマ字表記（例: idYear, KakuteiJyuni）",
            "race_id, race_date のような英語カラム名は使用できません",
        ]
    }


def get_target_equivalent_query_examples() -> dict:
    """TARGET frontier JV風のクエリ例"""
    return {
        "騎手成績": """
SELECT
    ru.KisyuRyakusyo,
    ru.Bamei,
    ru.KakuteiJyuni,
    ru.Ninki
FROM NL_SE_RACE_UMA ru
WHERE ru.KisyuRyakusyo LIKE '%ルメール%'
  AND ru.KakuteiJyuni IS NOT NULL
  AND LENGTH(ru.KakuteiJyuni) > 0
ORDER BY ru.idMonthDay DESC
LIMIT 200
        """,
    }
