"""JVLink MCP Server - 競馬分析MCPサーバー"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# .envファイルを読み込む
load_dotenv()
from .database.connection import DatabaseConnection
from .database.schema_info import (
    get_schema_description,
    get_target_equivalent_query_examples,
    TRACK_CODES,
    GRADE_CODES,
)
from .database.schema_descriptions import (
    get_column_description,
    get_table_description,
    QUERY_GENERATION_HINTS,
)
# Improvement modules
from .database.query_corrector import correct_query as auto_correct_query
from .database.query_templates import (
    list_templates as get_templates_list,
    render_template,
    get_template_info,
)
from .database.high_level_api import (
    get_favorite_performance as _get_favorite_performance,
    get_jockey_stats as _get_jockey_stats,
    get_frame_stats as _get_frame_stats,
    get_horse_history as _get_horse_history,
    get_sire_stats as _get_sire_stats,
)
from .database.sample_data_provider import (
    get_sample_data as _get_sample_data,
    get_column_value_examples as _get_column_value_examples,
    get_data_snapshot as _get_data_snapshot,
)

# FastMCPサーバーの初期化
mcp = FastMCP("JVLink MCP Server")

# データディレクトリのパス
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# 特徴量知見データの読み込み
with open(DATA_DIR / "feature_importance.json", "r", encoding="utf-8") as f:
    FEATURE_IMPORTANCE_DATA = json.load(f)



# ============================================================================
# Resources: Claude Desktopが接続時に自動的に読み込む情報
# ============================================================================

@mcp.resource("schema://database")
def database_schema_resource() -> str:
    """データベース全体のスキーマ情報

    接続時に自動的に読み込まれ、Claudeが最初からテーブル構造を理解できます
    """
    schema_info = get_schema_description()
    return json.dumps(schema_info, ensure_ascii=False, indent=2)


@mcp.resource("schema://tables")
def tables_list_resource() -> str:
    """テーブル一覧と説明

    全テーブルの概要を提供し、どのテーブルを使うべきか判断しやすくします
    """
    with DatabaseConnection() as db:
        tables = db.get_tables()

    tables_info = []
    for table in tables:
        desc = get_table_description(table)
        tables_info.append({
            "table_name": table,
            "description": desc.get("description", ""),
            "target_equivalent": desc.get("target_equivalent", ""),
            "primary_keys": desc.get("primary_keys", [])
        })

    return json.dumps({"tables": tables_info, "total": len(tables_info)}, ensure_ascii=False, indent=2)


@mcp.resource("schema://table/{table_name}")
def table_detail_resource(table_name: str) -> str:
    """個別テーブルの詳細情報（動的リソース）

    Args:
        table_name: テーブル名

    Returns:
        テーブルのカラム情報、説明、クエリヒント
    """
    with DatabaseConnection() as db:
        schema_df = db.get_table_schema(table_name)

        columns_with_desc = []
        for _, row in schema_df.iterrows():
            col_name = row["column_name"]
            col_info = {
                "name": col_name,
                "type": row["column_type"],
                "description": get_column_description(table_name, col_name)
            }
            columns_with_desc.append(col_info)

        table_desc = get_table_description(table_name)

        info = {
            "table_name": table_name,
            "table_description": table_desc.get("description", ""),
            "target_equivalent": table_desc.get("target_equivalent", ""),
            "primary_keys": table_desc.get("primary_keys", []),
            "total_columns": len(columns_with_desc),
            "columns": columns_with_desc,
            "query_hints": QUERY_GENERATION_HINTS if table_name in ["NL_RA_RACE", "NL_SE_RACE_UMA"] else ""
        }

        return json.dumps(info, ensure_ascii=False, indent=2)


@mcp.resource("examples://queries")
def query_examples_resource() -> str:
    """クエリ例集

    よく使うクエリパターンをサンプルとして提供
    """
    examples = get_target_equivalent_query_examples()
    return json.dumps(examples, ensure_ascii=False, indent=2)


@mcp.resource("knowledge://features")
def feature_knowledge_resource() -> str:
    """競馬予測で重要な特徴量の知見

    機械学習モデルで重要とされる特徴量とその活用方法
    """
    return json.dumps(FEATURE_IMPORTANCE_DATA, ensure_ascii=False, indent=2)


@mcp.resource("codes://tracks")
def track_codes_resource() -> str:
    """競馬場コード一覧

    JVLinkで使用される競馬場コードのマスタデータ
    """
    return json.dumps(TRACK_CODES, ensure_ascii=False, indent=2)


@mcp.resource("codes://grades")
def grade_codes_resource() -> str:
    """グレードコード一覧

    レースグレード（G1, G2, G3等）のコード表
    """
    return json.dumps(GRADE_CODES, ensure_ascii=False, indent=2)


# ============================================================================
# データベーススキーマ情報（ツール版 - 後方互換性のため残す）
# ============================================================================

@mcp.tool()
def get_database_schema() -> dict:
    """データベーススキーマ情報を取得

    Returns:
        テーブル一覧、カラム情報、との対応表
    """
    return get_schema_description()


@mcp.tool()
def get_query_examples() -> dict:
    """クエリ例集を取得

    Returns:
        よく使うクエリのサンプル集
    """
    return get_target_equivalent_query_examples()


@mcp.tool()
def list_tables() -> list[str]:
    """データベース内のテーブル一覧を取得

    Returns:
        テーブル名のリスト
    """
    with DatabaseConnection() as db:
        return db.get_tables()


@mcp.tool()
def get_table_info(table_name: str) -> dict:
    """指定テーブルのスキーマ情報を取得（詳細説明付き）

    Args:
        table_name: テーブル名

    Returns:
        カラム情報、テーブル説明、クエリヒントを含む辞書
    """
    with DatabaseConnection() as db:
        schema_df = db.get_table_schema(table_name)
        
        # カラム情報に説明を追加
        columns_with_desc = []
        for _, row in schema_df.iterrows():
            col_name = row["column_name"]
            col_info = {
                "name": col_name,
                "type": row["column_type"],
                "description": get_column_description(table_name, col_name)
            }
            columns_with_desc.append(col_info)
        
        # テーブル説明を取得
        table_desc = get_table_description(table_name)
        
        return {
            "table_name": table_name,
            "table_description": table_desc.get("description", ""),
            "target_equivalent": table_desc.get("target_equivalent", ""),
            "primary_keys": table_desc.get("primary_keys", []),
            "total_columns": len(columns_with_desc),
            "columns": columns_with_desc,
            "query_hints": QUERY_GENERATION_HINTS if table_name in ["NL_RA_RACE", "NL_SE_RACE_UMA"] else ""
        }


# ============================================================================
# 特徴量知見提供
# ============================================================================

@mcp.tool()
def get_important_features() -> dict:
    """競馬予測で重要な特徴量の知見を提供

    Returns:
        重要特徴量のリスト、説明、での活用方法
    """
    return {
        "features": FEATURE_IMPORTANCE_DATA["important_features"],
        "feature_combinations": FEATURE_IMPORTANCE_DATA["feature_combinations"],
        "total_features": len(FEATURE_IMPORTANCE_DATA["important_features"]),
        "references": FEATURE_IMPORTANCE_DATA["references"]
    }


@mcp.tool()
def get_feature_by_category(category: str) -> dict:
    """カテゴリ別に特徴量を取得

    Args:
        category: カテゴリ名（過去成績、適性、人的要因、血統など）

    Returns:
        該当カテゴリの特徴量リスト
    """
    features = [
        f for f in FEATURE_IMPORTANCE_DATA["important_features"]
        if f["category"] == category
    ]
    return {
        "category": category,
        "features": features,
        "count": len(features)
    }


@mcp.tool()
def search_features(keyword: str) -> dict:
    """キーワードで特徴量を検索

    Args:
        keyword: 検索キーワード（例: "人気", "距離", "騎手"）

    Returns:
        該当する特徴量のリスト
    """
    matching_features = [
        f for f in FEATURE_IMPORTANCE_DATA["important_features"]
        if keyword.lower() in f["name"].lower() or
           keyword.lower() in f["description"].lower()
    ]
    return {
        "keyword": keyword,
        "features": matching_features,
        "count": len(matching_features)
    }


# ============================================================================
# 自然言語SQL生成
# ============================================================================

@mcp.tool()
def generate_sql_from_natural_language(query_text: str) -> dict:
    """自然言語からSQLクエリを動的生成

    Args:
        query_text: 自然言語のクエリ
            例: "過去3年で東京競馬場の芝1600mで1番人気だった馬の成績を教えて"
            例: "ディープインパクト産駒の距離別成績を集計して"

    Returns:
        生成されたSQLクエリと説明
    """
    # スキーマ情報を取得
    schema_info = get_schema_description()

    # プロンプトを構築
    prompt = f"""
あなたはJVLink競馬データベースのSQLエキスパートです。
以下のユーザーの自然言語クエリをSQLに変換してください。

### データベース構造:
{json.dumps(schema_info, ensure_ascii=False, indent=2)}

### 競馬場コード:
{json.dumps(TRACK_CODES, ensure_ascii=False)}

### グレードコード:
{json.dumps(GRADE_CODES, ensure_ascii=False)}

### ユーザークエリ:
{query_text}

### 要件:
1. 読み取り専用のSELECT文のみ生成
2. JOINが必要な場合は適切に使用
3. WHERE句で適切にフィルタリング
4. 日付フィルタは DATE() 関数を使用
5. 集計が必要な場合はGROUP BYを使用

### 出力形式:
{{
    "sql": "生成されたSQLクエリ",
    "explanation": "クエリの日本語説明",
    "tables_used": ["使用したテーブルのリスト"],
    "notes": "注意事項やヒント"
}}
"""

    return {
        "prompt_for_llm": prompt,
        "hint": "このプロンプトをLLMに渡してSQLを生成してください",
        "schema_info": schema_info
    }


@mcp.tool(name="競馬データ検索")
def execute_safe_query(sql_query: str) -> dict:
    """SQLで競馬データを自由に検索・分析できる万能ツール

    人気別成績、騎手成績などの専用ツールでカバーできない分析はこのツールで実行できます。
    レース結果、オッズ、血統、調教など、あらゆる競馬データにアクセス可能です。

    Args:
        sql_query: 実行するSQLクエリ（SELECTのみ）

    Returns:
        クエリ実行結果
    """
    try:
        # Auto-correct query (zero-padding etc.)
        corrected_sql, corrections = auto_correct_query(sql_query)
        
        with DatabaseConnection() as db:
            result_df = db.execute_safe_query(corrected_sql)

            result = {
                "success": True,
                "rows": len(result_df),
                "columns": result_df.columns.tolist(),
                "data": result_df.head(100).to_dict(orient="records"),
                "note": "最大100行まで表示" if len(result_df) > 100 else None
            }
            
            # Notify if auto-corrections were made
            if corrections:
                result["auto_corrections"] = corrections
                result["original_query"] = sql_query
                result["corrected_query"] = corrected_sql
            
            return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "hint": "SELECT文のみ実行可能です。危険なキーワード（DROP, DELETE等）は使用できません。"
        }


@mcp.tool()
def validate_sql_query(sql_query: str) -> dict:
    """SQLクエリの安全性を検証

    Args:
        sql_query: 検証するSQLクエリ

    Returns:
        検証結果と安全性チェック
    """
    dangerous_keywords = [
        "DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER",
        "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE"
    ]

    query_upper = sql_query.upper()
    found_dangerous = [kw for kw in dangerous_keywords if kw in query_upper]

    is_safe = len(found_dangerous) == 0 and "SELECT" in query_upper

    return {
        "is_safe": is_safe,
        "query": sql_query,
        "dangerous_keywords_found": found_dangerous,
        "recommendation": "安全に実行可能" if is_safe else "危険なキーワードが含まれています",
        "can_execute": is_safe
    }




# ============================================================================
# High-level API (convenient analysis functions)
# ============================================================================

@mcp.tool(name="人気別成績")
def analyze_favorite_performance(
    ninki: int = 1,
    venue: Optional[str] = None,
    grade: Optional[str] = None,
    year_from: Optional[str] = None,
    distance: Optional[int] = None
) -> dict:
    """指定した人気順位の馬の成績を分析

    1番人気、2番人気など、人気順位別の勝率・複勝率を調べられます。
    競馬場やグレード、距離でフィルタリングも可能です。
    """
    with DatabaseConnection() as db:
        return _get_favorite_performance(
            db, venue=venue, ninki=ninki, grade=grade,
            year_from=year_from, distance=distance
        )


@mcp.tool(name="騎手成績")
def analyze_jockey_stats(
    jockey_name: str,
    venue: Optional[str] = None,
    year_from: Optional[str] = None,
    distance: Optional[int] = None
) -> dict:
    """騎手の成績を分析

    騎手名を指定して、勝率・複勝率・騎乗数などを調べられます。
    競馬場や距離でのフィルタリングも可能です。
    """
    with DatabaseConnection() as db:
        return _get_jockey_stats(
            db, jockey_name=jockey_name, venue=venue,
            year_from=year_from, distance=distance
        )


@mcp.tool(name="枠番別成績")
def analyze_frame_stats(
    venue: Optional[str] = None,
    distance: Optional[int] = None,
    year_from: Optional[str] = None
) -> dict:
    """枠番（1〜8枠）別の成績を分析

    内枠・外枠の有利不利を調べられます。
    競馬場や距離でフィルタリングすると、コース特性が見えます。
    """
    with DatabaseConnection() as db:
        df = _get_frame_stats(db, venue=venue, distance=distance, year_from=year_from)
        return {
            "data": df.to_dict(orient="records"),
            "conditions": df.attrs.get("conditions", ""),
            "columns": df.columns.tolist()
        }


@mcp.tool(name="馬の戦績")
def get_horse_race_history(
    horse_name: str,
    year_from: Optional[str] = None
) -> dict:
    """特定の馬の過去レース戦績を取得

    馬名を指定して、過去の出走履歴・着順・タイムなどを一覧できます。
    """
    with DatabaseConnection() as db:
        df = _get_horse_history(db, horse_name=horse_name, year_from=year_from)
        return {
            "horse_name": horse_name,
            "total_races": len(df),
            "data": df.to_dict(orient="records"),
            "columns": df.columns.tolist()
        }


@mcp.tool(name="種牡馬成績")
def analyze_sire_stats(
    sire_name: str,
    venue: Optional[str] = None,
    distance: Optional[int] = None,
    year_from: Optional[str] = None
) -> dict:
    """種牡馬（父馬）の産駒成績を分析

    種牡馬名を指定して、産駒の勝率・複勝率を調べられます。
    距離や競馬場でフィルタリングすると、血統の適性傾向が見えます。
    """
    with DatabaseConnection() as db:
        return _get_sire_stats(
            db, sire_name=sire_name, venue=venue,
            distance=distance, year_from=year_from
        )


# ============================================================================
# Query Templates
# ============================================================================

@mcp.tool()
def list_query_templates() -> dict:
    """利用可能なクエリテンプレート一覧を取得"""
    templates = get_templates_list()
    return {
        "templates": templates,
        "total": len(templates),
        "usage": "execute_template_query(template_name, **params)"
    }


@mcp.tool()
def execute_template_query(template_name: str, **params) -> dict:
    """テンプレートからSQLを生成して実行"""
    try:
        sql = render_template(template_name, **params)
        with DatabaseConnection() as db:
            result_df = db.execute_safe_query(sql)
            return {
                "success": True,
                "template": template_name,
                "parameters": params,
                "generated_sql": sql,
                "rows": len(result_df),
                "columns": result_df.columns.tolist(),
                "data": result_df.head(100).to_dict(orient="records"),
                "note": "max 100 rows" if len(result_df) > 100 else None
            }
    except ValueError as e:
        return {"success": False, "error": str(e), "hint": "Use list_query_templates to see available templates"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# Sample Data Provider
# ============================================================================

@mcp.tool()
def get_table_sample_data(table_name: str, num_rows: int = 5) -> dict:
    """テーブルのサンプルデータを取得（データ形式理解用）"""
    with DatabaseConnection() as db:
        return _get_sample_data(db, table_name=table_name, num_rows=num_rows)


@mcp.tool()
def get_column_examples(table_name: str, column_name: str, limit: int = 10) -> dict:
    """特定カラムの値の例を取得（データ形式理解用）"""
    with DatabaseConnection() as db:
        return _get_column_value_examples(
            db, table_name=table_name,
            column_name=column_name, limit=limit
        )


@mcp.tool()
def get_database_overview() -> dict:
    """データベース全体の概要を取得"""
    with DatabaseConnection() as db:
        return _get_data_snapshot(db)


# サーバーのエントリーポイント
if __name__ == "__main__":
    mcp.run()
