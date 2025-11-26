"""サンプルデータ提供モジュール

LLMがデータ形式を理解しやすいように、実際のデータサンプルを提供します。
"""

from typing import Dict, Any, List, Optional

# キャッシュ用
_sample_data_cache: Dict[str, Any] = {}

# 重要なカラム定義（サンプル取得時に表示）
IMPORTANT_COLUMNS = {
    "NL_SE": [
        "Year", "MonthDay", "JyoCD", "RaceNum", "Umaban", "Wakuban",
        "Bamei", "KisyuRyakusyo", "KakuteiJyuni", "Ninki", "Odds",
        "BaTaijyu", "HaronTimeL3", "Time"
        # 注意: Bamei1/2/3は馬名ではなくIDを含むため除外
    ],
    "NL_RA": [
        "Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum",
        "Hondai", "GradeCD", "Kyori", "TrackCD", "SyussoTosu"
    ],
    "NL_UM": [
        "KettoNum", "Bamei", "SexCD", "BirthDate",
        "Ketto3InfoBamei1", "Ketto3InfoBamei2", "Ketto3InfoBamei5",
        "SanchiName", "BreederName"
    ],
}


def get_sample_data(
    db_connection,
    table_name: str,
    num_rows: int = 5,
    where_clause: Optional[str] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """テーブルからサンプルデータを取得

    Args:
        db_connection: DatabaseConnectionインスタンス
        table_name: テーブル名
        num_rows: 取得行数（デフォルト5行）
        where_clause: 追加のWHERE条件（例: "JyoCD = '05'"）
        use_cache: キャッシュを使用するか

    Returns:
        dict: {
            'table_name': テーブル名,
            'columns': カラム名リスト,
            'sample_rows': サンプルデータ（リスト形式）,
            'column_info': 重要カラムの説明,
            'data_format_notes': データ形式の注意事項
        }
    """
    cache_key = f"{table_name}_{num_rows}_{where_clause}"

    if use_cache and cache_key in _sample_data_cache:
        return _sample_data_cache[cache_key]

    # 重要カラムを優先して取得
    important_cols = IMPORTANT_COLUMNS.get(table_name, [])

    if important_cols:
        columns_str = ", ".join(important_cols)
    else:
        columns_str = "*"

    # SQL構築
    sql = f"SELECT {columns_str} FROM {table_name}"

    if where_clause:
        sql += f" WHERE {where_clause}"

    # 結果データがあるレコードを優先（NL_SEの場合）
    if table_name == "NL_SE":
        sql += " AND KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''" if where_clause else " WHERE KakuteiJyuni IS NOT NULL AND KakuteiJyuni != ''"

    sql += f" LIMIT {num_rows}"

    try:
        df = db_connection.execute_safe_query(sql)

        result = {
            "table_name": table_name,
            "columns": df.columns.tolist(),
            "sample_rows": df.to_dict(orient="records"),
            "num_rows": len(df),
            "column_info": _get_column_info(table_name),
            "data_format_notes": _get_data_format_notes(table_name),
        }

        if use_cache:
            _sample_data_cache[cache_key] = result

        return result

    except Exception as e:
        return {
            "table_name": table_name,
            "error": str(e),
            "columns": [],
            "sample_rows": [],
        }


def get_column_value_examples(
    db_connection,
    table_name: str,
    column_name: str,
    limit: int = 10
) -> Dict[str, Any]:
    """特定カラムの値の例を取得

    Args:
        db_connection: DatabaseConnectionインスタンス
        table_name: テーブル名
        column_name: カラム名
        limit: 取得する値の種類数

    Returns:
        dict: {
            'column_name': カラム名,
            'unique_values': ユニークな値のリスト,
            'value_counts': 値ごとの件数（上位10件）
        }
    """
    # ユニーク値取得
    sql = f"""
    SELECT {column_name}, COUNT(*) as cnt
    FROM {table_name}
    WHERE {column_name} IS NOT NULL AND {column_name} != ''
    GROUP BY {column_name}
    ORDER BY cnt DESC
    LIMIT {limit}
    """

    try:
        df = db_connection.execute_safe_query(sql)

        return {
            "table_name": table_name,
            "column_name": column_name,
            "unique_values": df[column_name].tolist(),
            "value_counts": df.to_dict(orient="records"),
            "description": _get_column_description(table_name, column_name),
        }
    except Exception as e:
        return {
            "table_name": table_name,
            "column_name": column_name,
            "error": str(e),
        }


def get_data_snapshot(db_connection) -> Dict[str, Any]:
    """データベース全体のスナップショット情報を取得

    Args:
        db_connection: DatabaseConnectionインスタンス

    Returns:
        dict: {
            'tables': テーブルごとの概要情報,
            'total_records': 総レコード数,
            'data_period': データ期間
        }
    """
    results = {
        "tables": {},
        "total_records": 0,
    }

    # 各テーブルのレコード数を取得
    for table_name in ["NL_RA", "NL_SE", "NL_UM", "NL_KS", "NL_CH", "NL_HR", "NL_O1"]:
        try:
            count_sql = f"SELECT COUNT(*) as cnt FROM {table_name}"
            df = db_connection.execute_safe_query(count_sql)
            count = int(df.iloc[0]["cnt"]) if not df.empty else 0
            results["tables"][table_name] = {
                "record_count": count,
                "description": _get_table_description(table_name),
            }
            results["total_records"] += count
        except Exception:
            results["tables"][table_name] = {"record_count": 0, "error": "取得失敗"}

    # データ期間を取得（NL_SEから）
    try:
        period_sql = """
        SELECT
            MIN(Year || '-' || MonthDay) as earliest,
            MAX(Year || '-' || MonthDay) as latest
        FROM NL_SE
        WHERE KakuteiJyuni IS NOT NULL
        """
        df = db_connection.execute_safe_query(period_sql)
        if not df.empty:
            results["data_period"] = {
                "earliest": df.iloc[0]["earliest"],
                "latest": df.iloc[0]["latest"],
            }
    except Exception:
        results["data_period"] = {"error": "取得失敗"}

    return results


def _get_column_info(table_name: str) -> Dict[str, str]:
    """重要カラムの説明を取得"""

    column_info = {
        "NL_SE": {
            "KakuteiJyuni": "確定着順。01=1着, 02=2着...（ゼロパディング2桁）",
            "Ninki": "人気順位。01=1番人気, 02=2番人気...（ゼロパディング2桁）",
            "JyoCD": "競馬場コード。01=札幌, 05=東京, 06=中山...（ゼロパディング2桁）",
            "Umaban": "馬番。01-18（ゼロパディング2桁）",
            "Wakuban": "枠番。1-8（1桁）",
            "Odds": "単勝オッズ",
            "BaTaijyu": "馬体重（kg）",
            "HaronTimeL3": "上がり3Fタイム（0.1秒単位、例: 334=33.4秒）",
            "Bamei1": "父馬名",
            "Bamei2": "母馬名",
            "Bamei3": "母父馬名",
        },
        "NL_RA": {
            "Year": "開催年（YYYY）",
            "MonthDay": "開催月日（MMDD）",
            "JyoCD": "競馬場コード（ゼロパディング2桁）",
            "Hondai": "レース名",
            "GradeCD": "グレード。A=G1, B=G2, C=G3, D=リステッド",
            "Kyori": "距離（メートル）",
            "TrackCD": "トラックコード（2桁: 1桁目=芝/ダート, 2桁目=馬場状態）",
        },
        "NL_UM": {
            "KettoNum": "血統登録番号（馬の一意識別子）",
            "SexCD": "性別。1=牡, 2=牝, 3=セン",
            "Ketto3InfoBamei1": "父馬名",
            "Ketto3InfoBamei2": "母馬名",
            "Ketto3InfoBamei5": "母父馬名",
        },
    }

    return column_info.get(table_name, {})


def _get_data_format_notes(table_name: str) -> List[str]:
    """データ形式の注意事項を取得"""

    common_notes = [
        "すべてのカラムはTEXT型です",
        "数値比較時は文字列比較になるため注意が必要です",
    ]

    table_specific_notes = {
        "NL_SE": [
            "KakuteiJyuni='01'は1着、'02'は2着（ゼロパディング必須）",
            "Ninki='01'は1番人気（ゼロパディング必須）",
            "JyoCD='05'は東京競馬場（ゼロパディング必須）",
            "KakuteiJyuni='00'や空文字はレース未確定または除外馬",
        ],
        "NL_RA": [
            "GradeCD='A'はG1レース、'B'はG2、'C'はG3",
            "TrackCDは複合コード（例: '11'=芝・良）",
        ],
        "NL_UM": [
            "KettoNumは馬の一意識別子として他テーブルと結合可能",
        ],
    }

    return common_notes + table_specific_notes.get(table_name, [])


def _get_column_description(table_name: str, column_name: str) -> str:
    """カラムの説明を取得"""
    descriptions = _get_column_info(table_name)
    return descriptions.get(column_name, "説明なし")


def _get_table_description(table_name: str) -> str:
    """テーブルの説明を取得"""
    descriptions = {
        "NL_RA": "レース情報テーブル",
        "NL_SE": "出馬表・レース結果テーブル",
        "NL_UM": "馬マスタテーブル",
        "NL_KS": "騎手マスタテーブル",
        "NL_CH": "調教師マスタテーブル",
        "NL_HR": "払戻テーブル",
        "NL_O1": "単勝複勝オッズテーブル",
    }
    return descriptions.get(table_name, "不明")


def clear_cache():
    """キャッシュをクリア"""
    global _sample_data_cache
    _sample_data_cache = {}


__all__ = [
    "get_sample_data",
    "get_column_value_examples",
    "get_data_snapshot",
    "IMPORTANT_COLUMNS",
    "clear_cache",
]
