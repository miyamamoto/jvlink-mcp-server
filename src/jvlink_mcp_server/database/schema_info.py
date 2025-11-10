"""JVLinkデータベースのスキーマ情報"""

# JVLinkToSQLiteで作成される主要テーブルの情報
# TARGET frontier JVとの対応も含む

JVLINK_TABLES = {
    "NL_RA_RACE": {
        "description": "レース情報テーブル",
        "target_equivalent": "レース検索画面のデータソース",
        "key_columns": [
            "race_id",  # レースID (主キー)
            "race_date",  # 開催日
            "track_code",  # 競馬場コード
            "race_number",  # レース番号
            "race_name",  # レース名
            "grade",  # グレード (G1, G2, G3, OP等)
            "distance",  # 距離
            "track_type",  # 芝/ダート
            "direction",  # 右/左回り
            "track_condition",  # 馬場状態
            "weather",  # 天候
        ],
        "sample_query": "SELECT * FROM NL_RA_RACE WHERE track_code = '05' AND distance = 1600"
    },
    "NL_UM_UMA": {
        "description": "馬情報テーブル",
        "target_equivalent": "馬データ画面",
        "key_columns": [
            "horse_id",  # 馬ID (主キー)
            "horse_name",  # 馬名
            "sex",  # 性別
            "birth_date",  # 生年月日
            "sire_name",  # 父馬名
            "dam_name",  # 母馬名
            "broodmare_sire_name",  # 母父馬名
            "breeder",  # 生産者
            "owner",  # 馬主
        ]
    },
    "NL_SE_RACE_UMA": {
        "description": "レース出走馬情報",
        "target_equivalent": "出馬表画面",
        "key_columns": [
            "race_id",  # レースID
            "horse_id",  # 馬ID
            "horse_number",  # 馬番
            "bracket_number",  # 枠番
            "jockey_name",  # 騎手名
            "trainer_name",  # 調教師名
            "horse_weight",  # 馬体重
            "horse_weight_diff",  # 馬体重増減
            "odds_win",  # 単勝オッズ
            "popularity",  # 人気
        ]
    },
    "NL_RA_RACE_UMA": {
        "description": "レース結果テーブル",
        "target_equivalent": "レース結果画面",
        "key_columns": [
            "race_id",  # レースID
            "horse_id",  # 馬ID
            "finish_position",  # 着順
            "popularity",  # 人気
            "odds_win",  # 単勝オッズ
            "time",  # タイム
            "margin",  # 着差
            "passing_order",  # 通過順
            "last_3f_time",  # 上がり3Fタイム
            "jockey_name",  # 騎手名
            "trainer_name",  # 調教師名
            "horse_weight",  # 馬体重
        ]
    },
    "NL_KS_KISYU": {
        "description": "騎手情報テーブル",
        "target_equivalent": "騎手データ画面",
        "key_columns": [
            "jockey_code",  # 騎手コード
            "jockey_name",  # 騎手名
            "jockey_kana",  # 騎手名カナ
            "affiliation",  # 所属 (関東/関西)
        ]
    },
    "NL_CH_CHOKYOSI": {
        "description": "調教師情報テーブル",
        "target_equivalent": "調教師データ画面",
        "key_columns": [
            "trainer_code",  # 調教師コード
            "trainer_name",  # 調教師名
            "trainer_kana",  # 調教師名カナ
            "affiliation",  # 所属 (関東/関西)
        ]
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

# グレードマッピング
GRADE_CODES = {
    "G1": "GⅠ",
    "G2": "GⅡ",
    "G3": "GⅢ",
    "OP": "オープン",
    "1600": "1600万下",
    "1000": "1000万下",
    "500": "500万下",
    "未勝利": "未勝利",
    "新馬": "新馬",
}

# 馬場状態マッピング
TRACK_CONDITION_CODES = {
    "良": "良",
    "稍重": "稍重",
    "重": "重",
    "不良": "不良",
}


def get_schema_description() -> dict:
    """スキーマ全体の説明を取得"""
    return {
        "tables": JVLINK_TABLES,
        "track_codes": TRACK_CODES,
        "grade_codes": GRADE_CODES,
        "track_condition_codes": TRACK_CONDITION_CODES,
        "usage_notes": [
            "レース検索は NL_RA_RACE テーブルを使用",
            "出馬表は NL_SE_RACE_UMA テーブルを使用",
            "レース結果は NL_RA_RACE_UMA テーブルを使用",
            "馬情報は NL_UM_UMA テーブルを使用",
            "JOINする際は race_id, horse_id をキーに使用",
        ]
    }


def get_target_equivalent_query_examples() -> dict:
    """TARGET frontier JV風のクエリ例"""
    return {
        "1番人気の成績": """
            SELECT
                COUNT(*) as total_races,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN finish_position <= 2 THEN 1 ELSE 0 END) as places,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) as shows
            FROM NL_RA_RACE_UMA
            WHERE popularity = 1
            AND race_date >= DATE('now', '-3 years')
        """,
        "東京1600m芝の成績": """
            SELECT
                r.race_name,
                ru.horse_id,
                ru.finish_position,
                ru.time
            FROM NL_RA_RACE r
            JOIN NL_RA_RACE_UMA ru ON r.race_id = ru.race_id
            WHERE r.track_code = '05'
            AND r.distance = 1600
            AND r.track_type = '芝'
        """,
        "種牡馬別成績": """
            SELECT
                u.sire_name,
                COUNT(*) as races,
                SUM(CASE WHEN ru.finish_position = 1 THEN 1 ELSE 0 END) as wins,
                CAST(SUM(CASE WHEN ru.finish_position = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as win_rate
            FROM NL_UM_UMA u
            JOIN NL_RA_RACE_UMA ru ON u.horse_id = ru.horse_id
            GROUP BY u.sire_name
            HAVING COUNT(*) >= 10
            ORDER BY win_rate DESC
        """,
        "騎手成績（コース別）": """
            SELECT
                ru.jockey_name,
                r.track_code,
                COUNT(*) as races,
                SUM(CASE WHEN ru.finish_position = 1 THEN 1 ELSE 0 END) as wins
            FROM NL_RA_RACE_UMA ru
            JOIN NL_RA_RACE r ON ru.race_id = r.race_id
            WHERE r.race_date >= DATE('now', '-3 years')
            GROUP BY ru.jockey_name, r.track_code
            ORDER BY wins DESC
        """,
    }
