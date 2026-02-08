"""JVLinkデータベースのクエリテンプレート

よく使うクエリパターンをテンプレート化し、パラメータを埋めるだけで正しいSQLが生成できます。
すべてのユーザー入力値はパラメータ化クエリ（プレースホルダ）で安全に渡されます。
"""

from typing import Any, Dict, List, Optional, Tuple

# 競馬場名→コードマッピング（JRA）
VENUE_NAME_TO_CODE = {
    "札幌": "01",
    "函館": "02",
    "福島": "03",
    "新潟": "04",
    "東京": "05",
    "中山": "06",
    "中京": "07",
    "京都": "08",
    "阪神": "09",
    "小倉": "10",
}

# NAR地方競馬場名→コードマッピング
NAR_VENUE_NAME_TO_CODE = {
    "門別": "30", "北見": "31", "岩見沢": "32", "帯広": "33", "旭川": "34",
    "盛岡": "35", "水沢": "36", "上山": "37", "三条": "38", "足利": "39",
    "宇都宮": "40", "高崎": "41", "浦和": "42", "船橋": "43", "大井": "44",
    "川崎": "45", "金沢": "46", "笠松": "47", "名古屋": "48", "園田": "49",
    "姫路": "50", "益田": "51", "福山": "52", "高知": "53", "佐賀": "54",
    "荒尾": "55", "中津": "56", "札幌(地)": "57",
}

# 全競馬場コード（JRA + NAR）
ALL_VENUE_NAME_TO_CODE = {**VENUE_NAME_TO_CODE, **NAR_VENUE_NAME_TO_CODE}

# グレード名→コードマッピング
GRADE_NAME_TO_CODE = {
    "G1": "A",
    "GI": "A",
    "G2": "B",
    "GII": "B",
    "G3": "C",
    "GIII": "C",
    "リステッド": "D",
    "オープン特別": "E",
    "3勝クラス": "F",
    "2勝クラス": "G",
    "1勝クラス": "H",
    "未勝利": "I",
    "新馬": "J",
}

# クエリテンプレート定義
QUERY_TEMPLATES = {
    "favorite_win_rate": {
        "description": "人気別勝率を計算",
        "parameters": {
            "ninki": {
                "type": "int",
                "description": "人気順位（1-18）",
                "required": True,
            },
            "venue": {
                "type": "str",
                "description": "競馬場名（札幌、函館、福島、新潟、東京、中山、中京、京都、阪神、小倉）",
                "required": False,
            },
            "year_from": {
                "type": "str",
                "description": "集計開始年（YYYY形式）",
                "required": False,
            },
        },
        "sql": """
SELECT
    COUNT(*) as total_races,
    SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) as top3,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as top3_rate
FROM NL_SE
WHERE Ninki = {ninki}
  {venue_condition}
  {year_condition}
  AND KakuteiJyuni IS NOT NULL
  AND KakuteiJyuni > 0
""",
    },
    "jockey_stats": {
        "description": "騎手成績を集計",
        "parameters": {
            "jockey_name": {
                "type": "str",
                "description": "騎手名（部分一致可）",
                "required": False,
            },
            "year": {
                "type": "str",
                "description": "対象年（YYYY形式）",
                "required": False,
            },
            "limit": {
                "type": "int",
                "description": "表示件数",
                "required": False,
                "default": 20,
            },
        },
        "sql": """
SELECT
    KisyuRyakusyo as jockey_name,
    COUNT(*) as total_rides,
    SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN KakuteiJyuni <= 2 THEN 1 ELSE 0 END) as top2,
    SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) as top3,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as top3_rate
FROM NL_SE
WHERE KakuteiJyuni IS NOT NULL
  AND KakuteiJyuni > 0
  {jockey_condition}
  {year_condition}
GROUP BY KisyuRyakusyo
ORDER BY wins DESC, win_rate DESC
LIMIT {limit}
""",
    },
    "frame_stats": {
        "description": "枠番別成績を集計",
        "parameters": {
            "venue": {
                "type": "str",
                "description": "競馬場名",
                "required": False,
            },
            "kyori": {
                "type": "str",
                "description": "距離（メートル単位、例：1600）",
                "required": False,
            },
        },
        "sql": """
SELECT
    Wakuban as frame_number,
    COUNT(*) as total_runs,
    SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) as top3,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as top3_rate
FROM NL_SE
WHERE KakuteiJyuni IS NOT NULL
  AND KakuteiJyuni > 0
  {venue_condition}
  {kyori_condition}
GROUP BY Wakuban
ORDER BY Wakuban
""",
    },
    "race_result": {
        "description": "レース結果を取得（レース情報とJOIN）",
        "parameters": {
            "year": {
                "type": "str",
                "description": "開催年（YYYY形式）",
                "required": True,
            },
            "month_day": {
                "type": "str",
                "description": "開催月日（MMDD形式）",
                "required": True,
            },
            "jyo_cd": {
                "type": "str",
                "description": "競馬場コード（01-10）",
                "required": True,
            },
            "kaiji": {
                "type": "str",
                "description": "開催回次",
                "required": True,
            },
            "nichiji": {
                "type": "str",
                "description": "開催日次",
                "required": True,
            },
            "race_num": {
                "type": "str",
                "description": "レース番号（1-12）",
                "required": True,
            },
        },
        "sql": """
SELECT
    r.Hondai as race_name,
    r.GradeCD as grade,
    r.Kyori as distance,
    r.TrackCD as track_code,
    s.KakuteiJyuni as finish_position,
    s.Wakuban as frame_number,
    s.Umaban as horse_number,
    s.Bamei as horse_name,
    s.KisyuRyakusyo as jockey_name,
    s.Ninki as popularity,
    s.Odds as odds,
    s.Time as time,
    s.HaronTimeL3 as last_3f,
    s.BaTaijyu as weight
FROM NL_RA r
JOIN NL_SE s
  ON r.Year = s.Year
  AND r.MonthDay = s.MonthDay
  AND r.JyoCD = s.JyoCD
  AND r.Kaiji = s.Kaiji
  AND r.Nichiji = s.Nichiji
  AND r.RaceNum = s.RaceNum
WHERE r.Year = {year}
  AND r.MonthDay = '{month_day}'
  AND r.JyoCD = '{jyo_cd}'
  AND r.Kaiji = {kaiji}
  AND r.Nichiji = {nichiji}
  AND r.RaceNum = {race_num}
ORDER BY CAST(s.KakuteiJyuni AS INTEGER)
""",
    },
    "grade_race_list": {
        "description": "重賞レース一覧を取得",
        "parameters": {
            "grade": {
                "type": "str",
                "description": "グレード（G1、G2、G3、リステッド）",
                "required": False,
            },
            "year": {
                "type": "str",
                "description": "対象年（YYYY形式）",
                "required": False,
            },
            "venue": {
                "type": "str",
                "description": "競馬場名",
                "required": False,
            },
            "limit": {
                "type": "int",
                "description": "表示件数",
                "required": False,
                "default": 50,
            },
        },
        "sql": """
SELECT
    r.Year as year,
    r.MonthDay as month_day,
    r.JyoCD as venue_code,
    r.Hondai as race_name,
    r.GradeCD as grade,
    r.Kyori as distance,
    r.TrackCD as track_code,
    r.SyussoTosu as horse_count
FROM NL_RA r
WHERE r.GradeCD IN ('A', 'B', 'C', 'D')
  {grade_condition}
  {year_condition}
  {venue_condition}
ORDER BY r.Year DESC, r.MonthDay DESC
LIMIT {limit}
""",
    },
    "horse_pedigree": {
        "description": "馬の血統情報を取得",
        "parameters": {
            "horse_name": {
                "type": "str",
                "description": "馬名（部分一致可）",
                "required": True,
            },
        },
        "sql": """
SELECT
    u.Bamei as horse_name,
    u.KettoNum as ketto_num,
    u.SexCD as sex_code,
    u.BirthDate as birth_date,
    u.Ketto3InfoBamei1 as sire,
    u.Ketto3InfoBamei2 as dam,
    u.Ketto3InfoBamei5 as broodmare_sire,
    u.SanchiName as birthplace,
    u.BreederName as breeder,
    u.BanusiName as owner
FROM NL_UM u
WHERE u.Bamei LIKE {horse_name}
ORDER BY u.Bamei
LIMIT 20
""",
    },
    "sire_stats": {
        "description": "種牡馬別成績を集計",
        "parameters": {
            "sire_name": {
                "type": "str",
                "description": "種牡馬名（部分一致可）",
                "required": False,
            },
            "year": {
                "type": "str",
                "description": "対象年（YYYY形式）",
                "required": False,
            },
            "limit": {
                "type": "int",
                "description": "表示件数",
                "required": False,
                "default": 20,
            },
        },
        "sql": """
SELECT
    s.Bamei1 as sire_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN s.KakuteiJyuni <= 3 THEN 1 ELSE 0 END) as top3,
    ROUND(100.0 * SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate,
    ROUND(100.0 * SUM(CASE WHEN s.KakuteiJyuni <= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as top3_rate
FROM NL_SE s
WHERE s.KakuteiJyuni IS NOT NULL
  AND s.KakuteiJyuni > 0
  AND s.Bamei1 IS NOT NULL
  AND LENGTH(s.Bamei1) > 0
  {sire_condition}
  {year_condition}
GROUP BY s.Bamei1
HAVING COUNT(*) >= 10
ORDER BY wins DESC, win_rate DESC
LIMIT {limit}
""",
    },
    # === NAR（地方競馬）テンプレート ===
    "nar_favorite_win_rate": {
        "description": "NAR地方競馬の人気別勝率を計算",
        "parameters": {
            "ninki": {"type": "int", "description": "人気順位（1-18）", "required": True},
            "venue": {"type": "str", "description": "地方競馬場名（大井、船橋、川崎、浦和、名古屋、園田等）", "required": False},
            "year_from": {"type": "str", "description": "集計開始年（YYYY形式）", "required": False},
        },
        "sql": """
SELECT
    COUNT(*) as total_races,
    SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) as top3,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as top3_rate
FROM NL_SE_NAR
WHERE Ninki = {ninki}
  {venue_condition}
  {year_condition}
  AND KakuteiJyuni IS NOT NULL
  AND KakuteiJyuni > 0
""",
    },
    "nar_jockey_stats": {
        "description": "NAR地方競馬の騎手成績を集計",
        "parameters": {
            "jockey_name": {"type": "str", "description": "騎手名（部分一致可）", "required": False},
            "year": {"type": "str", "description": "対象年（YYYY形式）", "required": False},
            "limit": {"type": "int", "description": "表示件数", "required": False, "default": 20},
        },
        "sql": """
SELECT
    KisyuRyakusyo as jockey_name,
    COUNT(*) as total_rides,
    SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) as top3,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni <= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) as top3_rate
FROM NL_SE_NAR
WHERE KakuteiJyuni IS NOT NULL AND KakuteiJyuni > 0
  {jockey_condition}
  {year_condition}
GROUP BY KisyuRyakusyo
ORDER BY wins DESC, win_rate DESC
LIMIT {limit}
""",
    },
    "nar_venue_stats": {
        "description": "NAR地方競馬場別の1番人気成績を集計",
        "parameters": {
            "year_from": {"type": "str", "description": "集計開始年", "required": False},
        },
        "sql": """
SELECT
    JyoCD as venue_code,
    COUNT(*) as total_races,
    SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    ROUND(100.0 * SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate
FROM NL_SE_NAR
WHERE Ninki = 1 AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni > 0
  {year_condition}
GROUP BY JyoCD
ORDER BY win_rate DESC
""",
    },
    "track_condition_stats": {
        "description": "馬場状態別成績を分析（特定の馬）",
        "parameters": {
            "horse_name": {
                "type": "str",
                "description": "馬名（部分一致可）",
                "required": True,
            },
        },
        "sql": """
SELECT
    s.Bamei as horse_name,
    r.TrackCD as track_code,
    COUNT(*) as total_runs,
    SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN s.KakuteiJyuni <= 3 THEN 1 ELSE 0 END) as top3,
    ROUND(100.0 * SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as win_rate
FROM NL_SE s
JOIN NL_RA r
  ON s.Year = r.Year
  AND s.MonthDay = r.MonthDay
  AND s.JyoCD = r.JyoCD
  AND s.Kaiji = r.Kaiji
  AND s.Nichiji = r.Nichiji
  AND s.RaceNum = r.RaceNum
WHERE s.Bamei LIKE {horse_name}
  AND s.KakuteiJyuni IS NOT NULL
  AND s.KakuteiJyuni > 0
GROUP BY s.Bamei, r.TrackCD
ORDER BY total_runs DESC
""",
    },
}


def _to_int(value) -> int:
    """値を整数に変換（INTEGER型カラム用）

    SQLインジェクション防止のため、数値以外の値は拒否する
    """
    str_value = str(value).strip()
    if not str_value.lstrip('-').isdigit():
        raise ValueError(f"数値パラメータに不正な値が指定されました: {value!r}")
    return int(str_value)


def _venue_to_code(venue_name: str) -> str:
    """競馬場名をコードに変換（JRA + NAR対応）"""
    return ALL_VENUE_NAME_TO_CODE.get(venue_name, venue_name)


def _grade_to_code(grade_name: str) -> str:
    """グレード名をコードに変換"""
    return GRADE_NAME_TO_CODE.get(grade_name.upper(), grade_name)


def _zero_pad_code(code: str, length: int = 2) -> str:
    """コードをゼロパディング"""
    return code.zfill(length)


def render_template(template_name: str, **params) -> Tuple[str, tuple]:
    """テンプレートにパラメータを適用してSQLとパラメータタプルを生成

    Args:
        template_name: テンプレート名
        **params: パラメータ（テンプレートで定義されたもの）

    Returns:
        (SQL文字列, パラメータタプル) のタプル

    Raises:
        ValueError: テンプレートが存在しない、または必須パラメータが不足している場合

    Examples:
        >>> sql, query_params = render_template('favorite_win_rate', ninki=1, venue='東京')
        >>> sql, query_params = render_template('jockey_stats', jockey_name='武豊', limit=10)
    """
    if template_name not in QUERY_TEMPLATES:
        raise ValueError(
            f"テンプレート '{template_name}' が見つかりません。"
            f"利用可能なテンプレート: {list(QUERY_TEMPLATES.keys())}"
        )

    template = QUERY_TEMPLATES[template_name]
    template_params = template["parameters"]
    sql_template = template["sql"]

    # 必須パラメータのチェック
    for param_name, param_info in template_params.items():
        if param_info.get("required", False) and param_name not in params:
            raise ValueError(
                f"必須パラメータ '{param_name}' が指定されていません。"
                f"説明: {param_info.get('description', 'なし')}"
            )

    # パラメータを整形して格納
    formatted_params = {}
    query_params = []  # プレースホルダに対応するパラメータリスト

    for key, value in params.items():
        if value is None:
            continue

        # 人気順位の変換（INTEGER型）
        if key == "ninki":
            formatted_params[key] = "?"
            query_params.append(_to_int(value))

        # 競馬場名の変換
        elif key == "venue":
            formatted_params["venue_condition"] = "AND JyoCD = ?"
            query_params.append(_zero_pad_code(_venue_to_code(value)))

        # グレードの変換
        elif key == "grade":
            formatted_params["grade_condition"] = "AND r.GradeCD = ?"
            query_params.append(_grade_to_code(value))

        # 年の条件（INTEGER型）
        elif key == "year":
            formatted_params["year_condition"] = "AND Year = ?"
            query_params.append(_to_int(value))

        elif key == "year_from":
            formatted_params["year_condition"] = "AND Year >= ?"
            query_params.append(_to_int(value))

        # 騎手名の条件 - パラメータ化クエリ
        elif key == "jockey_name":
            formatted_params["jockey_condition"] = "AND KisyuRyakusyo LIKE ?"
            query_params.append('%' + str(value) + '%')

        # 種牡馬名の条件 - パラメータ化クエリ
        elif key == "sire_name":
            formatted_params["sire_condition"] = "AND s.Bamei1 LIKE ?"
            query_params.append('%' + str(value) + '%')

        # 距離の条件（INTEGER型）
        elif key == "kyori":
            formatted_params["kyori_condition"] = "AND Kyori = ?"
            query_params.append(_to_int(value))

        # 馬名 - パラメータ化クエリ（テンプレートSQL内の LIKE '%{horse_name}%' を置換）
        elif key == "horse_name":
            formatted_params[key] = "?"
            # horse_nameはテンプレート内で '%{horse_name}%' として使われるので
            # プレースホルダ置換後に処理する（下記の後処理で対応）
            query_params.append('%' + str(value) + '%')

        # 競馬場コード
        elif key == "jyo_cd":
            formatted_params[key] = "?"
            query_params.append(_zero_pad_code(value))

        # 数値として使われるパラメータ
        elif key in ("kaiji", "nichiji", "race_num"):
            formatted_params[key] = "?"
            query_params.append(_to_int(value))

        # 月日パラメータ（MMDD形式、数字のみ許可）
        elif key == "month_day":
            if not str(value).strip().isdigit():
                raise ValueError(f"month_day に不正な値が指定されました: {value!r}")
            formatted_params[key] = "?"
            query_params.append(str(value).strip())

        # limit等の数値パラメータ
        elif key == "limit":
            formatted_params[key] = "?"
            query_params.append(_to_int(value))

        # その他はそのまま
        else:
            formatted_params[key] = value

    # デフォルト値の設定
    for param_name, param_info in template_params.items():
        if param_name not in formatted_params and "default" in param_info:
            formatted_params[param_name] = "?"
            query_params.append(param_info["default"])

    # 条件が指定されていない場合は空文字に
    condition_keys = [
        "venue_condition", "year_condition", "jockey_condition",
        "sire_condition", "kyori_condition", "grade_condition"
    ]
    for cond_key in condition_keys:
        if cond_key not in formatted_params:
            formatted_params[cond_key] = ""

    # テンプレートに適用
    try:
        sql = sql_template.format(**formatted_params)
    except KeyError as e:
        raise ValueError(f"テンプレートに必要なパラメータが不足しています: {e}")

    # race_result等で '{field}' が '?' になった場合、クォートを除去
    sql = sql.replace("'?'", "?")

    # 余分な空白行を削除
    sql_lines = [line for line in sql.split("\n") if line.strip()]
    sql = "\n".join(sql_lines)

    return sql, tuple(query_params)


def list_templates() -> List[Dict[str, Any]]:
    """利用可能なテンプレート一覧を返す

    Returns:
        テンプレート情報のリスト
            - name: テンプレート名
            - description: 説明
            - parameters: パラメータ定義

    Examples:
        >>> templates = list_templates()
        >>> for t in templates:
        ...     print(f"{t['name']}: {t['description']}")
    """
    result = []
    for name, template in QUERY_TEMPLATES.items():
        result.append({
            "name": name,
            "description": template["description"],
            "parameters": template["parameters"],
        })
    return result


def get_template_info(template_name: str) -> Optional[Dict[str, Any]]:
    """特定のテンプレート情報を取得

    Args:
        template_name: テンプレート名

    Returns:
        テンプレート情報（存在しない場合はNone）
            - description: 説明
            - parameters: パラメータ定義
            - sql: SQLテンプレート

    Examples:
        >>> info = get_template_info('favorite_win_rate')
        >>> print(info['description'])
        人気別勝率を計算
    """
    if template_name not in QUERY_TEMPLATES:
        return None

    template = QUERY_TEMPLATES[template_name]
    return {
        "name": template_name,
        "description": template["description"],
        "parameters": template["parameters"],
        "sql": template["sql"],
    }


# 便利な定数をエクスポート
__all__ = [
    "QUERY_TEMPLATES",
    "VENUE_NAME_TO_CODE",
    "NAR_VENUE_NAME_TO_CODE",
    "ALL_VENUE_NAME_TO_CODE",
    "GRADE_NAME_TO_CODE",
    "render_template",
    "list_templates",
    "get_template_info",
]
