"""High-level API for common horse racing analysis patterns

このモジュールは、よくある分析パターンを簡単に実行できる関数を提供します。
内部で正しいSQLを自動生成し、データベースから結果を取得します。
"""

from typing import Optional, Dict, Any
import pandas as pd


def _escape_like_param(value: str) -> str:
    """LIKE句のパラメータをエスケープしてSQLインジェクションを防止

    Args:
        value: ユーザー入力値

    Returns:
        エスケープ済みの文字列
    """
    # シングルクォートをエスケープ
    escaped = value.replace("'", "''")
    # LIKE句の特殊文字をエスケープ
    escaped = escaped.replace("%", "\\%")
    escaped = escaped.replace("_", "\\_")
    return escaped


# 競馬場名→コード変換テーブル（JRA）
VENUE_CODES = {
    '札幌': '01', '函館': '02', '福島': '03', '新潟': '04',
    '東京': '05', '中山': '06', '中京': '07', '京都': '08',
    '阪神': '09', '小倉': '10'
}

# NAR地方競馬場名→コード変換テーブル
NAR_VENUE_CODES = {
    '門別': '30', '北見': '31', '岩見沢': '32', '帯広': '33', '旭川': '34',
    '盛岡': '35', '水沢': '36', '上山': '37', '三条': '38', '足利': '39',
    '宇都宮': '40', '高崎': '41', '浦和': '42', '船橋': '43', '大井': '44',
    '川崎': '45', '金沢': '46', '笠松': '47', '名古屋': '48', '園田': '49',
    '姫路': '50', '益田': '51', '福山': '52', '高知': '53', '佐賀': '54',
    '荒尾': '55', '中津': '56', '札幌(地)': '57',
}

# 全競馬場コード（JRA + NAR）
ALL_VENUE_CODES = {**VENUE_CODES, **NAR_VENUE_CODES}

# コード→競馬場名の逆引き
VENUE_NAMES = {v: k for k, v in VENUE_CODES.items()}
NAR_VENUE_NAMES = {v: k for k, v in NAR_VENUE_CODES.items()}
ALL_VENUE_NAMES = {**VENUE_NAMES, **NAR_VENUE_NAMES}

# グレードコード変換（入力形式→DBコード）
GRADE_CODES = {
    'G1': 'A', 'GI': 'A', 'G1': 'A',
    'G2': 'B', 'GII': 'B', 'G2': 'B',
    'G3': 'C', 'GIII': 'C', 'G3': 'C',
    'A': 'A', 'B': 'B', 'C': 'C',
    'リステッド': 'D', 'オープン特別': 'E',
    '3勝': 'F', '2勝': 'G', '1勝': 'H',
    '未勝利': 'I', '新馬': 'J'
}

# ソース別テーブル名
_SOURCE_TABLES = {
    'jra': {'se': 'NL_SE', 'ra': 'NL_RA'},
    'nar': {'se': 'NL_SE_NAR', 'ra': 'NL_RA_NAR'},
}


def _resolve_venue(venue: str, source: str = 'jra') -> str:
    """競馬場名をコードに変換（source対応）"""
    if source == 'nar':
        code = NAR_VENUE_CODES.get(venue) or VENUE_CODES.get(venue)
        if not code:
            raise ValueError(f"不明な競馬場名: {venue}. NAR: {list(NAR_VENUE_CODES.keys())}, JRA: {list(VENUE_CODES.keys())}")
        return code
    else:
        code = VENUE_CODES.get(venue)
        if not code:
            raise ValueError(f"不明な競馬場名: {venue}. 有効な値: {list(VENUE_CODES.keys())}")
        return code


def _compute_rates(total, wins, places_2, places_3):
    """勝率・連対率・複勝率を計算"""
    return {
        'total': total, 'wins': wins, 'places_2': places_2, 'places_3': places_3,
        'win_rate': (wins / total * 100) if total > 0 else 0.0,
        'place_rate_2': (places_2 / total * 100) if total > 0 else 0.0,
        'place_rate_3': (places_3 / total * 100) if total > 0 else 0.0,
    }


def _favorite_performance_impl(
    db_connection,
    venue: Optional[str] = None,
    ninki: int = 1,
    grade: Optional[str] = None,
    year_from: Optional[str] = None,
    distance: Optional[int] = None,
    source: str = 'jra'
) -> Dict[str, Any]:
    """人気別成績の共通実装（JRA/NAR兼用）"""
    tables = _SOURCE_TABLES[source]
    conditions = []
    condition_desc = []

    conditions.append(f"Ninki = {ninki}")
    condition_desc.append(f"{ninki}番人気")
    if source == 'nar':
        condition_desc.append("NAR地方競馬")

    conditions.append("KakuteiJyuni IS NOT NULL")
    conditions.append("KakuteiJyuni > 0")

    if venue:
        venue_code = _resolve_venue(venue, source)
        conditions.append(f"s.JyoCD = '{venue_code}'")
        condition_desc.append(f"{venue}競馬場")

    if grade:
        grade_code = GRADE_CODES.get(grade.upper())
        if not grade_code:
            raise ValueError(f"不明なグレード: {grade}. 有効な値: {list(GRADE_CODES.keys())}")
        conditions.append(f"r.GradeCD = '{grade_code}'")
        condition_desc.append(f"グレード{grade}")

    if year_from:
        conditions.append(f"s.Year >= {year_from}")
        condition_desc.append(f"{year_from}年以降")

    if distance:
        conditions.append(f"r.Kyori = {distance}")
        condition_desc.append(f"{distance}m")

    where_clause = " AND ".join(conditions)
    need_join = grade or distance

    if need_join:
        query = f"""
        SELECT COUNT(*) as total,
            SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM {tables['se']} s
        JOIN {tables['ra']} r
            ON s.Year = r.Year AND s.MonthDay = r.MonthDay AND s.JyoCD = r.JyoCD
            AND s.Kaiji = r.Kaiji AND s.Nichiji = r.Nichiji AND s.RaceNum = r.RaceNum
        WHERE {where_clause}
        """
    else:
        query = f"""
        SELECT COUNT(*) as total,
            SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM {tables['se']} s
        WHERE {where_clause}
        """

    df = db_connection.execute_safe_query(query)

    if df.empty or df.iloc[0]['total'] == 0:
        return {**_compute_rates(0, 0, 0, 0),
                'conditions': ', '.join(condition_desc), 'query': query}

    row = df.iloc[0]
    result = _compute_rates(int(row['total']), int(row['wins']),
                           int(row['places_2']), int(row['places_3']))
    result['conditions'] = ', '.join(condition_desc)
    result['query'] = query
    return result


def get_favorite_performance(
    db_connection,
    venue: Optional[str] = None,
    ninki: int = 1,
    grade: Optional[str] = None,
    year_from: Optional[str] = None,
    distance: Optional[int] = None
) -> Dict[str, Any]:
    """人気別成績を取得

    Args:
        db_connection: DatabaseConnectionインスタンス
        venue: 競馬場名（日本語、例: '東京', '中山'）
        ninki: 人気順位（1-18）
        grade: グレードコード（'G1', 'G2', 'G3' または 'A', 'B', 'C'）
        year_from: 集計開始年（例: '2023'）
        distance: 距離（メートル、例: 1600）

    Returns:
        dict: 勝率・連対率・複勝率等

    Example:
        >>> result = get_favorite_performance(
        ...     db_conn, venue='東京', ninki=1, grade='G1', year_from='2020'
        ... )
        >>> print(f"勝率: {result['win_rate']:.1f}%")
    """
    return _favorite_performance_impl(
        db_connection, venue=venue, ninki=ninki, grade=grade,
        year_from=year_from, distance=distance, source='jra'
    )


def _jockey_stats_impl(
    db_connection,
    jockey_name: str,
    venue: Optional[str] = None,
    year_from: Optional[str] = None,
    distance: Optional[int] = None,
    source: str = 'jra'
) -> Dict[str, Any]:
    """騎手成績の共通実装（JRA/NAR兼用）"""
    tables = _SOURCE_TABLES[source]
    conditions = []
    condition_desc = [f"騎手名: {jockey_name}（部分一致）"]
    if source == 'nar':
        condition_desc.append("NAR地方競馬")

    safe_name = _escape_like_param(jockey_name)
    conditions.append(f"s.KisyuRyakusyo LIKE '%{safe_name}%' ESCAPE '\\'")
    conditions.append("s.KakuteiJyuni IS NOT NULL")
    conditions.append("s.KakuteiJyuni > 0")

    if venue:
        venue_code = _resolve_venue(venue, source)
        conditions.append(f"s.JyoCD = '{venue_code}'")
        condition_desc.append(f"{venue}競馬場")

    if year_from:
        conditions.append(f"s.Year >= {year_from}")
        condition_desc.append(f"{year_from}年以降")

    if distance:
        conditions.append(f"r.Kyori = {distance}")
        condition_desc.append(f"{distance}m")

    where_clause = " AND ".join(conditions)

    if distance:
        query = f"""
        SELECT s.KisyuRyakusyo as jockey_name, COUNT(*) as total_rides,
            SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM {tables['se']} s
        JOIN {tables['ra']} r
            ON s.Year = r.Year AND s.MonthDay = r.MonthDay AND s.JyoCD = r.JyoCD
            AND s.Kaiji = r.Kaiji AND s.Nichiji = r.Nichiji AND s.RaceNum = r.RaceNum
        WHERE {where_clause}
        GROUP BY s.KisyuRyakusyo
        """
    else:
        query = f"""
        SELECT s.KisyuRyakusyo as jockey_name, COUNT(*) as total_rides,
            SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM {tables['se']} s
        WHERE {where_clause}
        GROUP BY s.KisyuRyakusyo
        """

    df = db_connection.execute_safe_query(query)

    if df.empty:
        return {
            'jockey_name': jockey_name, 'total_rides': 0, 'wins': 0,
            'places_2': 0, 'places_3': 0, 'win_rate': 0.0,
            'place_rate_2': 0.0, 'place_rate_3': 0.0,
            'conditions': ', '.join(condition_desc), 'query': query
        }

    total_rides = int(df['total_rides'].sum())
    wins = int(df['wins'].sum())
    places_2 = int(df['places_2'].sum())
    places_3 = int(df['places_3'].sum())
    matched_jockey = df.loc[df['total_rides'].idxmax(), 'jockey_name']

    return {
        'jockey_name': matched_jockey, 'total_rides': total_rides,
        'wins': wins, 'places_2': places_2, 'places_3': places_3,
        'win_rate': (wins / total_rides * 100) if total_rides > 0 else 0.0,
        'place_rate_2': (places_2 / total_rides * 100) if total_rides > 0 else 0.0,
        'place_rate_3': (places_3 / total_rides * 100) if total_rides > 0 else 0.0,
        'conditions': ', '.join(condition_desc),
        'matched_jockeys': df['jockey_name'].tolist(), 'query': query
    }


def get_jockey_stats(
    db_connection,
    jockey_name: str,
    venue: Optional[str] = None,
    year_from: Optional[str] = None,
    distance: Optional[int] = None
) -> Dict[str, Any]:
    """騎手成績を取得

    Args:
        db_connection: DatabaseConnectionインスタンス
        jockey_name: 騎手名（部分一致検索、例: 'ルメール', '武豊'）
        venue: 競馬場名（日本語、例: '東京', '中山'）
        year_from: 集計開始年（例: '2023'）
        distance: 距離（メートル、例: 1600）

    Returns:
        dict: 騎手成績（勝率・連対率・複勝率等）

    Example:
        >>> result = get_jockey_stats(db_conn, 'ルメール', venue='東京', year_from='2023')
        >>> print(f"{result['jockey_name']}: 勝率 {result['win_rate']:.1f}%")
    """
    return _jockey_stats_impl(
        db_connection, jockey_name=jockey_name, venue=venue,
        year_from=year_from, distance=distance, source='jra'
    )


def get_frame_stats(
    db_connection,
    venue: Optional[str] = None,
    distance: Optional[int] = None,
    year_from: Optional[str] = None
) -> pd.DataFrame:
    """枠番別成績を取得

    Args:
        db_connection: DatabaseConnectionインスタンス
        venue: 競馬場名（日本語、例: '東京', '中山'）
        distance: 距離（メートル、例: 1600）
        year_from: 集計開始年（例: '2023'）

    Returns:
        DataFrame: 枠番別の成績
            - wakuban: 枠番（1-8）
            - total: 総出走数
            - wins: 1着回数
            - places_2: 2着以内回数
            - places_3: 3着以内回数
            - win_rate: 勝率（%）
            - place_rate_2: 連対率（%）
            - place_rate_3: 複勝率（%）

    Example:
        >>> df = get_frame_stats(db_conn, venue='東京', distance=1600)
        >>> print(df.to_string())
    """
    # WHERE条件を構築
    conditions = []
    condition_desc = []

    # 確定着順がNULLでない（INTEGER型）
    conditions.append("s.KakuteiJyuni IS NOT NULL")
    conditions.append("s.KakuteiJyuni > 0")
    conditions.append("s.Wakuban IS NOT NULL")
    conditions.append("s.Wakuban > 0")

    # 競馬場
    if venue:
        venue_code = VENUE_CODES.get(venue)
        if not venue_code:
            raise ValueError(f"不明な競馬場名: {venue}. 有効な値: {list(VENUE_CODES.keys())}")
        conditions.append(f"s.JyoCD = '{venue_code}'")
        condition_desc.append(f"{venue}競馬場")

    # 年（INTEGER型）
    if year_from:
        conditions.append(f"s.Year >= {year_from}")
        condition_desc.append(f"{year_from}年以降")

    # 距離（INTEGER型、NL_RAと結合が必要）
    if distance:
        conditions.append(f"r.Kyori = {distance}")
        condition_desc.append(f"{distance}m")

    where_clause = " AND ".join(conditions)

    # 距離指定がある場合はNL_RAと結合
    if distance:
        query = f"""
        SELECT
            s.Wakuban as wakuban,
            COUNT(*) as total,
            SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM NL_SE s
        JOIN NL_RA r
            ON s.Year = r.Year
            AND s.MonthDay = r.MonthDay
            AND s.JyoCD = r.JyoCD
            AND s.Kaiji = r.Kaiji
            AND s.Nichiji = r.Nichiji
            AND s.RaceNum = r.RaceNum
        WHERE {where_clause}
        GROUP BY s.Wakuban
        ORDER BY s.Wakuban
        """
    else:
        query = f"""
        SELECT
            Wakuban as wakuban,
            COUNT(*) as total,
            SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM NL_SE s
        WHERE {where_clause}
        GROUP BY Wakuban
        ORDER BY Wakuban
        """

    # クエリ実行
    df = db_connection.execute_safe_query(query)

    if df.empty:
        return pd.DataFrame(columns=['wakuban', 'total', 'wins', 'places_2', 'places_3',
                                    'win_rate', 'place_rate_2', 'place_rate_3'])

    # 勝率・連対率・複勝率を計算
    df['win_rate'] = (df['wins'] / df['total'] * 100).round(2)
    df['place_rate_2'] = (df['places_2'] / df['total'] * 100).round(2)
    df['place_rate_3'] = (df['places_3'] / df['total'] * 100).round(2)

    # メタデータを属性として追加
    df.attrs['conditions'] = ', '.join(condition_desc) if condition_desc else '全条件'
    df.attrs['query'] = query

    return df


def _horse_history_impl(
    db_connection,
    horse_name: str,
    year_from: Optional[str] = None,
    source: str = 'jra'
) -> pd.DataFrame:
    """馬の戦績の共通実装（JRA/NAR兼用）"""
    tables = _SOURCE_TABLES[source]
    venue_map = ALL_VENUE_NAMES if source == 'nar' else VENUE_NAMES

    safe_name = _escape_like_param(horse_name)
    conditions = [
        f"s.Bamei LIKE '%{safe_name}%' ESCAPE '\\'",
        "s.KakuteiJyuni IS NOT NULL",
        "s.KakuteiJyuni > 0"
    ]
    if year_from:
        conditions.append(f"s.Year >= {year_from}")

    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT s.Year || '-' || s.MonthDay as race_date, s.JyoCD as venue_code,
        r.Hondai as race_name, r.Kyori as distance,
        s.KakuteiJyuni as finish, s.Ninki as popularity,
        s.KisyuRyakusyo as jockey, s.Time as time, s.Bamei as horse_name
    FROM {tables['se']} s
    JOIN {tables['ra']} r
        ON s.Year = r.Year AND s.MonthDay = r.MonthDay AND s.JyoCD = r.JyoCD
        AND s.Kaiji = r.Kaiji AND s.Nichiji = r.Nichiji AND s.RaceNum = r.RaceNum
    WHERE {where_clause}
    ORDER BY s.Year DESC, s.MonthDay DESC
    """

    df = db_connection.execute_safe_query(query)

    if df.empty:
        return pd.DataFrame(columns=['race_date', 'venue', 'race_name', 'distance',
                                    'finish', 'popularity', 'jockey', 'time'])

    df['venue'] = df['venue_code'].map(venue_map)
    df = df.drop(columns=['venue_code'])
    df['finish'] = df['finish'].astype(str).str.lstrip('0').replace('', '0').astype(int)
    df['popularity'] = df['popularity'].astype(str).str.lstrip('0').replace('', '0').astype(int)
    df.attrs['query'] = query
    return df


def get_horse_history(
    db_connection,
    horse_name: str,
    year_from: Optional[str] = None
) -> pd.DataFrame:
    """馬の戦績を取得

    Args:
        db_connection: DatabaseConnectionインスタンス
        horse_name: 馬名（部分一致検索）
        year_from: 集計開始年（例: '2023'）

    Returns:
        DataFrame: 馬の戦績詳細

    Example:
        >>> df = get_horse_history(db_conn, 'ディープインパクト')
        >>> print(df.to_string())
    """
    return _horse_history_impl(db_connection, horse_name=horse_name,
                               year_from=year_from, source='jra')


def get_sire_stats(
    db_connection,
    sire_name: str,
    venue: Optional[str] = None,
    distance: Optional[int] = None,
    year_from: Optional[str] = None
) -> Dict[str, Any]:
    """種牡馬（父馬）成績を取得

    Args:
        db_connection: DatabaseConnectionインスタンス
        sire_name: 種牡馬名（部分一致検索）
        venue: 競馬場名（日本語、例: '東京', '中山'）
        distance: 距離（メートル、例: 1600）
        year_from: 集計開始年（例: '2023'）

    Returns:
        dict: {
            'sire_name': 種牡馬名,
            'total_runs': 総出走数,
            'wins': 1着回数,
            'places_2': 2着以内回数,
            'places_3': 3着以内回数,
            'win_rate': 勝率（%）,
            'place_rate_2': 連対率（%）,
            'place_rate_3': 複勝率（%）,
            'conditions': 適用した条件の説明
        }

    Example:
        >>> result = get_sire_stats(db_conn, 'ディープインパクト', venue='東京', distance=1600)
        >>> print(f"{result['sire_name']}: 勝率 {result['win_rate']:.1f}%")
    """
    conditions = []
    condition_desc = [f"種牡馬: {sire_name}（部分一致）"]

    # 種牡馬名（部分一致）- SQLインジェクション対策済み
    safe_sire_name = _escape_like_param(sire_name)
    conditions.append(f"s.Bamei1 LIKE '%{safe_sire_name}%' ESCAPE '\\'")

    # 確定着順がNULLでない（INTEGER型）
    conditions.append("s.KakuteiJyuni IS NOT NULL")
    conditions.append("s.KakuteiJyuni > 0")

    # 競馬場
    if venue:
        venue_code = VENUE_CODES.get(venue)
        if not venue_code:
            raise ValueError(f"不明な競馬場名: {venue}. 有効な値: {list(VENUE_CODES.keys())}")
        conditions.append(f"s.JyoCD = '{venue_code}'")
        condition_desc.append(f"{venue}競馬場")

    # 年（INTEGER型）
    if year_from:
        conditions.append(f"s.Year >= {year_from}")
        condition_desc.append(f"{year_from}年以降")

    # 距離（INTEGER型、NL_RAと結合が必要）
    if distance:
        conditions.append(f"r.Kyori = {distance}")
        condition_desc.append(f"{distance}m")

    where_clause = " AND ".join(conditions)

    # 距離指定がある場合はNL_RAと結合
    if distance:
        query = f"""
        SELECT
            s.Bamei1 as sire_name,
            COUNT(*) as total_runs,
            SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN s.KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM NL_SE s
        JOIN NL_RA r
            ON s.Year = r.Year
            AND s.MonthDay = r.MonthDay
            AND s.JyoCD = r.JyoCD
            AND s.Kaiji = r.Kaiji
            AND s.Nichiji = r.Nichiji
            AND s.RaceNum = r.RaceNum
        WHERE {where_clause}
        GROUP BY s.Bamei1
        """
    else:
        query = f"""
        SELECT
            Bamei1 as sire_name,
            COUNT(*) as total_runs,
            SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN KakuteiJyuni IN (1, 2) THEN 1 ELSE 0 END) as places_2,
            SUM(CASE WHEN KakuteiJyuni IN (1, 2, 3) THEN 1 ELSE 0 END) as places_3
        FROM NL_SE s
        WHERE {where_clause}
        GROUP BY Bamei1
        """

    # クエリ実行
    df = db_connection.execute_safe_query(query)

    if df.empty:
        return {
            'sire_name': sire_name,
            'total_runs': 0,
            'wins': 0,
            'places_2': 0,
            'places_3': 0,
            'win_rate': 0.0,
            'place_rate_2': 0.0,
            'place_rate_3': 0.0,
            'conditions': ', '.join(condition_desc),
            'query': query
        }

    # 複数の種牡馬がマッチする可能性があるため、合計を計算
    total_runs = int(df['total_runs'].sum())
    wins = int(df['wins'].sum())
    places_2 = int(df['places_2'].sum())
    places_3 = int(df['places_3'].sum())

    # マッチした種牡馬名を取得（最も出走数が多い種牡馬）
    matched_sire = df.loc[df['total_runs'].idxmax(), 'sire_name'] if not df.empty else sire_name

    return {
        'sire_name': matched_sire,
        'total_runs': total_runs,
        'wins': wins,
        'places_2': places_2,
        'places_3': places_3,
        'win_rate': (wins / total_runs * 100) if total_runs > 0 else 0.0,
        'place_rate_2': (places_2 / total_runs * 100) if total_runs > 0 else 0.0,
        'place_rate_3': (places_3 / total_runs * 100) if total_runs > 0 else 0.0,
        'conditions': ', '.join(condition_desc),
        'matched_sires': df['sire_name'].tolist(),
        'query': query
    }


# ============================================================================
# NAR（地方競馬）専用API — JRA版関数に委譲するラッパー
# ============================================================================

def _resolve_nar_venue(venue: str) -> str:
    """NAR競馬場名をコードに変換。JRA/NAR両方を試す（後方互換）"""
    return _resolve_venue(venue, source='nar')


def get_nar_favorite_performance(
    db_connection,
    venue: Optional[str] = None,
    ninki: int = 1,
    year_from: Optional[str] = None,
    distance: Optional[int] = None
) -> Dict[str, Any]:
    """NAR地方競馬の人気別成績を取得（JRA版に委譲）"""
    return _favorite_performance_impl(
        db_connection, venue=venue, ninki=ninki, year_from=year_from,
        distance=distance, source='nar'
    )


def get_nar_jockey_stats(
    db_connection,
    jockey_name: str,
    venue: Optional[str] = None,
    year_from: Optional[str] = None
) -> Dict[str, Any]:
    """NAR地方競馬の騎手成績を取得（JRA版に委譲）"""
    return _jockey_stats_impl(
        db_connection, jockey_name=jockey_name, venue=venue,
        year_from=year_from, source='nar'
    )


def get_nar_horse_history(
    db_connection,
    horse_name: str,
    year_from: Optional[str] = None
) -> pd.DataFrame:
    """NAR地方競馬の馬の戦績を取得（JRA版に委譲）"""
    return _horse_history_impl(
        db_connection, horse_name=horse_name, year_from=year_from, source='nar'
    )
