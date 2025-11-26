"""SQLクエリの自動修正モジュール

よくある間違い(ゼロパディング不足など)を自動的に検出・修正する。
"""

import re
from typing import List, Tuple


class QueryCorrector:
    """SQLクエリを検証し、よくある間違いを自動修正するクラス"""

    ZERO_PADDING_COLUMNS = {
        'Ninki': 2,
        'KakuteiJyuni': 2,
        'JyoCD': 2,
        'Umaban': 2,
    }

    def __init__(self):
        """QueryCorrectorを初期化"""
        self.corrections: List[str] = []

    def correct_query(self, sql: str) -> Tuple[str, List[str]]:
        """SQLクエリを修正する

        Args:
            sql: 修正対象のSQLクエリ

        Returns:
            (修正後SQL, 修正内容リスト)のタプル
        """
        self.corrections = []
        corrected_sql = sql

        # 各カラムに対してゼロパディングを適用
        for column_name, padding_length in self.ZERO_PADDING_COLUMNS.items():
            corrected_sql = self._apply_zero_padding(
                corrected_sql,
                column_name,
                padding_length
            )

        return corrected_sql, self.corrections

    def _apply_zero_padding(
        self,
        sql: str,
        column_name: str,
        padding_length: int
    ) -> str:
        """指定カラムの値にゼロパディングを適用

        Args:
            sql: SQL文字列
            column_name: 対象カラム名
            padding_length: パディング桁数

        Returns:
            修正後のSQL文字列
        """
        # パターン1: column = 'value' 形式
        pattern_equal = rf"({column_name}\s*=\s*')(\d+)(')"
        sql = self._replace_with_padding(
            sql,
            pattern_equal,
            column_name,
            padding_length,
            is_in_clause=False
        )

        # パターン2: column IN ('value1', 'value2', ...) 形式
        # IN句内の各値を個別に処理
        pattern_in = rf"{column_name}\s+IN\s*\((.*?)\)"

        def replace_in_clause(match):
            in_values = match.group(1)
            original_values = in_values

            # IN句内の各値を抽出して修正
            value_pattern = r"'(\d+)'"

            def replace_value(value_match):
                original_value = value_match.group(1)
                if len(original_value) < padding_length and original_value.isdigit():
                    padded_value = original_value.zfill(padding_length)
                    if original_value != padded_value:
                        correction_msg = (
                            f"{column_name} IN句内: '{original_value}' → '{padded_value}'"
                        )
                        if correction_msg not in self.corrections:
                            self.corrections.append(correction_msg)
                    return f"'{padded_value}'"
                return value_match.group(0)

            corrected_values = re.sub(value_pattern, replace_value, in_values)
            return f"{column_name} IN ({corrected_values})"

        sql = re.sub(pattern_in, replace_in_clause, sql, flags=re.IGNORECASE)

        return sql

    def _replace_with_padding(
        self,
        sql: str,
        pattern: str,
        column_name: str,
        padding_length: int,
        is_in_clause: bool = False
    ) -> str:
        """パターンマッチして値をゼロパディング

        Args:
            sql: SQL文字列
            pattern: 正規表現パターン
            column_name: カラム名
            padding_length: パディング桁数
            is_in_clause: IN句内の値かどうか

        Returns:
            修正後のSQL文字列
        """
        def replacer(match):
            prefix = match.group(1)  # "ColumnName = '"
            value = match.group(2)    # "1"
            suffix = match.group(3)   # "'"

            # 数値で、かつ必要な桁数より短い場合のみパディング
            if value.isdigit() and len(value) < padding_length:
                padded_value = value.zfill(padding_length)
                correction_msg = f"{column_name}: '{value}' → '{padded_value}'"
                if correction_msg not in self.corrections:
                    self.corrections.append(correction_msg)
                return f"{prefix}{padded_value}{suffix}"

            return match.group(0)

        return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)

    def validate_query(self, sql: str) -> Tuple[bool, List[str]]:
        """クエリの検証（修正が必要かチェック）

        Args:
            sql: 検証対象のSQLクエリ

        Returns:
            (検証OK, 警告メッセージリスト)のタプル
        """
        warnings = []

        # 各カラムについてゼロパディング不足をチェック
        for column_name, padding_length in self.ZERO_PADDING_COLUMNS.items():
            # = 形式のチェック
            pattern_equal = rf"{column_name}\s*=\s*'(\d{{1,{padding_length-1}}})'"
            matches = re.findall(pattern_equal, sql, re.IGNORECASE)
            for match in matches:
                warnings.append(
                    f"{column_name}の値 '{match}' は{padding_length}桁でゼロパディングが推奨されます"
                )

            # IN句のチェック
            pattern_in = rf"{column_name}\s+IN\s*\((.*?)\)"
            in_matches = re.findall(pattern_in, sql, re.IGNORECASE)
            for in_clause in in_matches:
                value_pattern = r"'(\d+)'"
                values = re.findall(value_pattern, in_clause)
                for value in values:
                    if len(value) < padding_length:
                        warnings.append(
                            f"{column_name} IN句内の値 '{value}' は{padding_length}桁でゼロパディングが推奨されます"
                        )

        is_valid = len(warnings) == 0
        return is_valid, warnings


def correct_query(sql: str) -> Tuple[str, List[str]]:
    """クエリ修正のヘルパー関数

    Args:
        sql: 修正対象のSQLクエリ

    Returns:
        (修正後SQL, 修正内容リスト)のタプル
    """
    corrector = QueryCorrector()
    return corrector.correct_query(sql)


def validate_query(sql: str) -> Tuple[bool, List[str]]:
    """クエリ検証のヘルパー関数

    Args:
        sql: 検証対象のSQLクエリ

    Returns:
        (検証OK, 警告メッセージリスト)のタプル
    """
    corrector = QueryCorrector()
    return corrector.validate_query(sql)
