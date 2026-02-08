"""Tests for NAR (地方競馬) support"""

import pytest
import pandas as pd
from unittest.mock import Mock

from jvlink_mcp_server.database.high_level_api import (
    get_nar_favorite_performance,
    get_nar_jockey_stats,
    get_nar_horse_history,
    NAR_VENUE_CODES,
    ALL_VENUE_CODES,
    ALL_VENUE_NAMES,
)
from jvlink_mcp_server.database.schema_descriptions import (
    TABLE_DESCRIPTIONS,
    COLUMN_DESCRIPTIONS,
    CODE_MAPPINGS,
    get_column_description,
    get_table_description,
)
from jvlink_mcp_server.database.schema_info import (
    ALL_TABLES,
    NAR_TABLES,
    NAR_TRACK_CODES,
    get_schema_description,
    get_query_examples,
)
from jvlink_mcp_server.database.query_templates import (
    QUERY_TEMPLATES,
    NAR_VENUE_NAME_TO_CODE,
    ALL_VENUE_NAME_TO_CODE,
    render_template,
    list_templates,
)
from jvlink_mcp_server.database.schema_auto_descriptions import (
    generate_column_description,
)


@pytest.fixture
def mock_db():
    return Mock()


class TestNARConstants:
    """NAR定数のテスト"""

    def test_nar_venue_codes(self):
        assert NAR_VENUE_CODES['大井'] == '44'
        assert NAR_VENUE_CODES['船橋'] == '43'
        assert NAR_VENUE_CODES['川崎'] == '45'
        assert NAR_VENUE_CODES['浦和'] == '42'
        assert NAR_VENUE_CODES['名古屋'] == '48'
        assert len(NAR_VENUE_CODES) == 28

    def test_all_venue_codes_includes_both(self):
        assert '東京' in ALL_VENUE_CODES  # JRA
        assert '大井' in ALL_VENUE_CODES  # NAR
        assert ALL_VENUE_CODES['東京'] == '05'
        assert ALL_VENUE_CODES['大井'] == '44'

    def test_nar_track_codes(self):
        assert NAR_TRACK_CODES['44'] == '大井'
        assert NAR_TRACK_CODES['43'] == '船橋'
        assert len(NAR_TRACK_CODES) == 28


class TestNARSchemaDescriptions:
    """NARスキーマ説明のテスト"""

    def test_nar_tables_in_table_descriptions(self):
        assert 'NL_RA_NAR' in TABLE_DESCRIPTIONS
        assert 'NL_SE_NAR' in TABLE_DESCRIPTIONS
        assert 'NL_UM_NAR' in TABLE_DESCRIPTIONS
        assert 'RT_RA_NAR' in TABLE_DESCRIPTIONS

    def test_nar_table_description_content(self):
        desc = TABLE_DESCRIPTIONS['NL_RA_NAR']
        assert 'NAR' in desc['description'] or '地方' in desc['description']

    def test_nar_column_descriptions(self):
        assert 'NL_RA_NAR' in COLUMN_DESCRIPTIONS
        assert '地方' in COLUMN_DESCRIPTIONS['NL_RA_NAR']['JyoCD']

    def test_get_column_description_nar_fallback(self):
        """NARテーブルのカラム説明がJRAにフォールバックするか"""
        desc = get_column_description('NL_SE_NAR', 'Bamei')
        assert '馬名' in desc

    def test_get_table_description_nar(self):
        desc = get_table_description('NL_RA_NAR')
        assert 'NAR' in desc['description'] or '地方' in desc['description']

    def test_nar_venue_code_mappings(self):
        assert '地方競馬場コード' in CODE_MAPPINGS
        assert CODE_MAPPINGS['地方競馬場コード']['44'] == '大井'


class TestNARSchemaInfo:
    """NARスキーマ情報のテスト"""

    def test_nar_tables_in_all_tables(self):
        assert 'NL_RA_NAR' in ALL_TABLES
        assert 'NL_SE_NAR' in ALL_TABLES
        assert 'NL_UM_NAR' in ALL_TABLES
        assert 'RT_RA_NAR' in ALL_TABLES
        assert 'RT_SE_NAR' in ALL_TABLES
        assert 'TS_O1_NAR' in ALL_TABLES

    def test_nar_tables_count(self):
        nar_count = sum(1 for t in ALL_TABLES if t.endswith('_NAR'))
        # Should have NAR equivalents for all JRA tables
        jra_count = sum(1 for t in ALL_TABLES if not t.endswith('_NAR'))
        assert nar_count == jra_count

    def test_schema_description_includes_nar(self):
        desc = get_schema_description()
        assert 'nar_track_codes' in desc
        assert any('NAR' in note for note in desc['important_notes'])

    def test_query_examples_include_nar(self):
        examples = get_query_examples()
        assert any('NAR' in key for key in examples.keys())


class TestNARAutoDescriptions:
    """NAR自動カラム説明のテスト"""

    def test_jyocd_nar_table(self):
        desc = generate_column_description('NL_RA_NAR', 'JyoCD')
        assert '地方' in desc
        assert '大井' in desc

    def test_jyocd_jra_table(self):
        desc = generate_column_description('NL_RA', 'JyoCD')
        assert '札幌' in desc
        assert '大井' not in desc


class TestNARQueryTemplates:
    """NARクエリテンプレートのテスト"""

    def test_nar_templates_exist(self):
        assert 'nar_favorite_win_rate' in QUERY_TEMPLATES
        assert 'nar_jockey_stats' in QUERY_TEMPLATES
        assert 'nar_venue_stats' in QUERY_TEMPLATES

    def test_nar_venue_name_to_code(self):
        assert NAR_VENUE_NAME_TO_CODE['大井'] == '44'
        assert NAR_VENUE_NAME_TO_CODE['船橋'] == '43'

    def test_all_venue_includes_nar(self):
        assert ALL_VENUE_NAME_TO_CODE['大井'] == '44'
        assert ALL_VENUE_NAME_TO_CODE['東京'] == '05'

    def test_render_nar_favorite_template(self):
        sql = render_template('nar_favorite_win_rate', ninki=1)
        assert 'NL_SE_NAR' in sql
        assert 'Ninki = 1' in sql

    def test_render_nar_favorite_with_venue(self):
        sql = render_template('nar_favorite_win_rate', ninki=1, venue='大井')
        assert 'NL_SE_NAR' in sql
        assert "JyoCD = '44'" in sql

    def test_render_nar_jockey_template(self):
        sql = render_template('nar_jockey_stats')
        assert 'NL_SE_NAR' in sql

    def test_list_templates_includes_nar(self):
        templates = list_templates()
        names = [t['name'] for t in templates]
        assert 'nar_favorite_win_rate' in names
        assert 'nar_jockey_stats' in names


class TestNARHighLevelAPI:
    """NAR高レベルAPIのテスト"""

    def test_nar_favorite_performance_basic(self, mock_db):
        mock_result = pd.DataFrame({
            'total': [100], 'wins': [30], 'places_2': [50], 'places_3': [70]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_nar_favorite_performance(mock_db, ninki=1)

        assert result['total'] == 100
        assert result['wins'] == 30
        assert result['win_rate'] == 30.0
        assert 'NAR' in result['conditions']

        call_args = mock_db.execute_safe_query.call_args[0][0]
        assert 'NL_SE_NAR' in call_args

    def test_nar_favorite_performance_with_venue(self, mock_db):
        mock_result = pd.DataFrame({
            'total': [50], 'wins': [15], 'places_2': [25], 'places_3': [35]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_nar_favorite_performance(mock_db, venue='大井', ninki=1)

        call_args = mock_db.execute_safe_query.call_args[0][0]
        assert "JyoCD = '44'" in call_args
        assert '大井' in result['conditions']

    def test_nar_favorite_performance_zero_results(self, mock_db):
        mock_result = pd.DataFrame({'total': [0], 'wins': [0], 'places_2': [0], 'places_3': [0]})
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_nar_favorite_performance(mock_db, ninki=1)
        assert result['total'] == 0
        assert result['win_rate'] == 0.0

    def test_nar_favorite_performance_invalid_venue(self, mock_db):
        with pytest.raises(ValueError, match="不明な競馬場名"):
            get_nar_favorite_performance(mock_db, venue='無効')

    def test_nar_jockey_stats_basic(self, mock_db):
        mock_result = pd.DataFrame({
            'jockey_name': ['テスト騎手'],
            'total_rides': [200], 'wins': [40],
            'places_2': [80], 'places_3': [120]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_nar_jockey_stats(mock_db, jockey_name='テスト')

        assert result['jockey_name'] == 'テスト騎手'
        assert result['win_rate'] == 20.0
        call_args = mock_db.execute_safe_query.call_args[0][0]
        assert 'NL_SE_NAR' in call_args

    def test_nar_jockey_stats_no_results(self, mock_db):
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame())
        result = get_nar_jockey_stats(mock_db, jockey_name='存在しない')
        assert result['total_rides'] == 0

    def test_nar_horse_history_basic(self, mock_db):
        mock_result = pd.DataFrame({
            'race_date': ['2024-0515'],
            'venue_code': ['44'],
            'race_name': ['東京ダービー'],
            'distance': ['2000'],
            'finish': ['01'],
            'popularity': ['02'],
            'jockey': ['テスト騎手'],
            'time': ['020512'],
            'horse_name': ['テスト馬']
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        df = get_nar_horse_history(mock_db, horse_name='テスト馬')

        assert len(df) == 1
        assert df['venue'].iloc[0] == '大井'
        call_args = mock_db.execute_safe_query.call_args[0][0]
        assert 'NL_SE_NAR' in call_args
        assert 'NL_RA_NAR' in call_args

    def test_nar_horse_history_empty(self, mock_db):
        mock_db.execute_safe_query = Mock(return_value=pd.DataFrame())
        df = get_nar_horse_history(mock_db, horse_name='存在しない')
        assert df.empty
