"""JVLink MCP Server - TARGET frontier JV風の競馬分析MCPサーバー"""

import os
import json
from pathlib import Path
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
    """TARGET frontier JV風のクエリ例集

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
        テーブル一覧、カラム情報、TARGET frontier JVとの対応表
    """
    return get_schema_description()


@mcp.tool()
def get_query_examples() -> dict:
    """TARGET frontier JV風のクエリ例集を取得

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
        重要特徴量のリスト、説明、TARGET frontier JVでの活用方法
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


@mcp.tool()
def execute_safe_query(sql_query: str) -> dict:
    """安全なSQLクエリを実行（読み取り専用）

    Args:
        sql_query: 実行するSQLクエリ（SELECTのみ）

    Returns:
        クエリ実行結果
    """
    try:
        with DatabaseConnection() as db:
            result_df = db.execute_safe_query(sql_query)

            return {
                "success": True,
                "rows": len(result_df),
                "columns": result_df.columns.tolist(),
                "data": result_df.head(100).to_dict(orient="records"),
                "note": "最大100行まで表示" if len(result_df) > 100 else None
            }
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
# TARGET風レース検索
# ============================================================================

# 注意: search_racesとanalyze_popularity_stats関数は実際のカラム名と合わないため削除
# 代わりにexecute_safe_queryとResourcesのクエリ例を使用してください

# サーバーのエントリーポイント
if __name__ == "__main__":
    mcp.run()
