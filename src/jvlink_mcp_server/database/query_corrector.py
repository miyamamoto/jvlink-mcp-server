"""SQLクエリの自動修正モジュール

よくある間違いを自動的に検出・修正する。
jrvltsql v2.0以降では数値カラムがINTEGER型になったため、
ゼロパディングが必要なのはJyoCD（競馬場コード）のみ。
"""

import re
from typing import List, Tuple


class QueryCorrector:
    """SQLクエリを検証し、よくある間違いを自動修正するクラス"""

    # JyoCDのみゼロパディングが必要（TEXT型のまま）
    ZERO_PADDING_COLUMNS = {
        'JyoCD': 2,
    }

    # INTEGER型になったカラム（文字列比較を数値比較に修正）
    INTEGER_COLUMNS = ['Ninki', 'KakuteiJyuni', 'Umaban', 'Wakuban', 'Barei', 'Year', 'Kyori']

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

        # JyoCDのゼロパディング
        for column_name, padding_length in self.ZERO_PADDING_COLUMNS.items():
            corrected_sql = self._apply_zero_padding(
                corrected_sql,
                column_name,
                padding_length
            )

        # INTEGER型カラムの文字列比較を数値比較に修正
        for column_name in self.INTEGER_COLUMNS:
            corrected_sql = self._convert_string_to_int(corrected_sql, column_name)

        return corrected_sql, self.corrections

    def _convert_string_to_int(self, sql: str, column_name: str) -> str:
        """文字列比較を数値比較に変換

        例: Ninki = '1' → Ninki = 1
        """
        # パターン: column = 'value' 形式
        pattern = rf"({column_name}\s*=\s*)'(\d+)'"

        def replacer(match):
            prefix = match.group(1)
            value = match.group(2)
            correction_msg = f"{column_name}: '{value}' → {value} (INTEGER型)"
            if correction_msg not in self.corrections:
                self.corrections.append(correction_msg)
            return f"{prefix}{value}"

        return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)

    def _apply_zero_padding(
        self,
        sql: str,
        column_name: str,
        padding_length: int
    ) -> str:
        """指定カラムの値にゼロパディングを適用"""
        # パターン: column = 'value' 形式
        pattern_equal = rf"({column_name}\s*=\s*')(\d+)(')"
        sql = self._replace_with_padding(
            sql,
            pattern_equal,
            column_name,
            padding_length
        )

        # パターン: column IN ('value1', 'value2', ...) 形式
        pattern_in = rf"{column_name}\s+IN\s*\((.*?)\)"

        def replace_in_clause(match):
            in_values = match.group(1)
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
        padding_length: int
    ) -> str:
        """パターンマッチして値をゼロパディング"""
        def replacer(match):
            prefix = match.group(1)
            value = match.group(2)
            suffix = match.group(3)

            if value.isdigit() and len(value) < padding_length:
                padded_value = value.zfill(padding_length)
                correction_msg = f"{column_name}: '{value}' → '{padded_value}'"
                if correction_msg not in self.corrections:
                    self.corrections.append(correction_msg)
                return f"{prefix}{padded_value}{suffix}"

            return match.group(0)

        return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)


def correct_query(sql: str) -> Tuple[str, List[str]]:
    """クエリ修正のヘルパー関数"""
    corrector = QueryCorrector()
    return corrector.correct_query(sql)
