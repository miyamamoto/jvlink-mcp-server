"""Tests for query_templates module"""

import pytest
from jvlink_mcp_server.database.query_templates import (
    render_template, list_templates, get_template_info
)


class TestListTemplates:
    def test_returns_list(self):
        templates = list_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0

    def test_template_structure(self):
        templates = list_templates()
        for t in templates:
            assert "name" in t
            assert "description" in t
            assert "parameters" in t


class TestGetTemplateInfo:
    def test_existing_template(self):
        info = get_template_info("favorite_win_rate")
        assert info is not None
        assert info["name"] == "favorite_win_rate"

    def test_nonexistent_template(self):
        info = get_template_info("nonexistent")
        assert info is None


class TestRenderTemplate:
    def test_favorite_win_rate_basic(self):
        sql, params = render_template("favorite_win_rate", ninki=1)
        assert "Ninki = ?" in sql
        assert 1 in params
        assert "SELECT" in sql

    def test_favorite_win_rate_with_venue(self):
        sql, params = render_template("favorite_win_rate", ninki=1, venue="東京")
        assert "JyoCD = ?" in sql
        assert "05" in params

    def test_jockey_stats(self):
        sql, params = render_template("jockey_stats", jockey_name="ルメール")
        assert "LIKE ?" in sql
        assert "%ルメール%" in params

    def test_nonexistent_template_raises(self):
        with pytest.raises(ValueError, match="見つかりません"):
            render_template("nonexistent")

    def test_missing_required_param(self):
        with pytest.raises(ValueError, match="必須パラメータ"):
            render_template("race_result")  # requires year, month_day, etc.

    def test_horse_pedigree_escaping(self):
        """SQLインジェクション対策テスト - パラメータ化クエリにより安全"""
        sql, params = render_template("horse_pedigree", horse_name="test'; DROP TABLE--")
        # SQL本文には値が埋め込まれない
        assert "test'" not in sql
        # 値はパラメータとして渡される
        assert "%test'; DROP TABLE--%" in params

    def test_sire_stats(self):
        sql, params = render_template("sire_stats", sire_name="ディープインパクト")
        assert "LIKE ?" in sql
        assert "%ディープインパクト%" in params

    def test_grade_race_list(self):
        sql, params = render_template("grade_race_list", grade="G1", year="2024")
        assert "GradeCD = ?" in sql
        assert "A" in params
        assert "Year = ?" in sql
        assert 2024 in params

    def test_frame_stats_with_distance(self):
        sql, params = render_template("frame_stats", kyori="1600")
        assert "Kyori = ?" in sql
        assert 1600 in params

    def test_returns_tuple(self):
        """render_templateが(sql, params)タプルを返すことを確認"""
        result = render_template("favorite_win_rate", ninki=1)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], tuple)
