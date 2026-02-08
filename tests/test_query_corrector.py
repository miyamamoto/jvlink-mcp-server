"""Tests for query_corrector module"""

import pytest
from jvlink_mcp_server.database.query_corrector import correct_query, QueryCorrector


class TestCorrectQuery:
    """correct_query関数のテスト"""

    def test_jyocd_zero_padding(self):
        """JyoCDのゼロパディング修正"""
        sql = "SELECT * FROM NL_SE WHERE JyoCD = '5'"
        corrected, corrections = correct_query(sql)
        assert "JyoCD = '05'" in corrected
        assert len(corrections) == 1

    def test_jyocd_already_padded(self):
        """既にゼロパディング済みのJyoCD"""
        sql = "SELECT * FROM NL_SE WHERE JyoCD = '05'"
        corrected, corrections = correct_query(sql)
        assert corrected == sql
        assert len(corrections) == 0

    def test_integer_column_string_to_int(self):
        """INTEGER型カラムの文字列比較→数値比較変換"""
        sql = "SELECT * FROM NL_SE WHERE Ninki = '1'"
        corrected, corrections = correct_query(sql)
        assert "Ninki = 1" in corrected
        assert len(corrections) == 1

    def test_multiple_integer_columns(self):
        """複数のINTEGER型カラム修正"""
        sql = "SELECT * FROM NL_SE WHERE Ninki = '1' AND KakuteiJyuni = '3'"
        corrected, corrections = correct_query(sql)
        assert "Ninki = 1" in corrected
        assert "KakuteiJyuni = 3" in corrected
        assert len(corrections) == 2

    def test_jyocd_in_clause(self):
        """IN句内のJyoCDゼロパディング"""
        sql = "SELECT * FROM NL_SE WHERE JyoCD IN ('5', '6')"
        corrected, corrections = correct_query(sql)
        assert "'05'" in corrected
        assert "'06'" in corrected

    def test_no_corrections_needed(self):
        """修正不要のクエリ"""
        sql = "SELECT * FROM NL_SE WHERE JyoCD = '05' AND Ninki = 1"
        corrected, corrections = correct_query(sql)
        assert corrected == sql
        assert len(corrections) == 0

    def test_year_string_to_int(self):
        """Year列の文字列→数値変換"""
        sql = "SELECT * FROM NL_SE WHERE Year = '2024'"
        corrected, corrections = correct_query(sql)
        assert "Year = 2024" in corrected
