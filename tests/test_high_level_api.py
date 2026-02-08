"""Tests for high_level_api module"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock
from jvlink_mcp_server.database.high_level_api import (
    get_favorite_performance,
    get_jockey_stats,
    get_frame_stats,
    get_horse_history,
    get_sire_stats,
    VENUE_CODES,
    GRADE_CODES
)


@pytest.fixture
def mock_db():
    """モックデータベース接続を作成"""
    db = Mock()
    return db


def _get_query_and_params(mock_db):
    """モックのexecute_safe_queryの呼び出し引数を取得"""
    call_args = mock_db.execute_safe_query.call_args
    query = call_args[0][0]
    params = call_args[1].get('params', ()) if call_args[1] else ()
    return query, params


class TestGetFavoritePerformance:
    """get_favorite_performance関数のテスト"""

    def test_basic_query(self, mock_db):
        """基本的なクエリのテスト"""
        mock_result = pd.DataFrame({
            'total': [100],
            'wins': [30],
            'places_2': [60],
            'places_3': [80]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_favorite_performance(mock_db, ninki=1)

        assert result['total'] == 100
        assert result['wins'] == 30
        assert result['win_rate'] == 30.0
        assert result['place_rate_2'] == 60.0
        assert result['place_rate_3'] == 80.0
        assert '1番人気' in result['conditions']

    def test_with_venue(self, mock_db):
        """競馬場指定のテスト（パラメータ化クエリ）"""
        mock_result = pd.DataFrame({
            'total': [50],
            'wins': [20],
            'places_2': [30],
            'places_3': [40]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_favorite_performance(mock_db, venue='東京', ninki=1)

        query, params = _get_query_and_params(mock_db)
        assert "JyoCD = ?" in query
        assert '05' in params
        assert '東京競馬場' in result['conditions']

    def test_with_grade(self, mock_db):
        """グレード指定のテスト（パラメータ化クエリ）"""
        mock_result = pd.DataFrame({
            'total': [20],
            'wins': [10],
            'places_2': [15],
            'places_3': [18]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_favorite_performance(mock_db, ninki=1, grade='G1')

        query, params = _get_query_and_params(mock_db)
        assert "GradeCD = ?" in query
        assert 'A' in params
        assert 'NL_RA' in query  # グレード指定時はNL_RAと結合

    def test_zero_results(self, mock_db):
        """結果が0件の場合のテスト"""
        mock_result = pd.DataFrame({
            'total': [0],
            'wins': [0],
            'places_2': [0],
            'places_3': [0]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_favorite_performance(mock_db, ninki=1)

        assert result['total'] == 0
        assert result['win_rate'] == 0.0

    def test_invalid_venue(self, mock_db):
        """不正な競馬場名のテスト"""
        with pytest.raises(ValueError, match="不明な競馬場名"):
            get_favorite_performance(mock_db, venue='無効な競馬場')

    def test_ninki_parameterized(self, mock_db):
        """人気番号がパラメータ化されているテスト"""
        mock_result = pd.DataFrame({
            'total': [10],
            'wins': [1],
            'places_2': [2],
            'places_3': [3]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_favorite_performance(mock_db, ninki=5)

        query, params = _get_query_and_params(mock_db)
        assert "Ninki = ?" in query
        assert 5 in params


class TestGetJockeyStats:
    """get_jockey_stats関数のテスト"""

    def test_basic_query(self, mock_db):
        """基本的なクエリのテスト"""
        mock_result = pd.DataFrame({
            'jockey_name': ['ルメール'],
            'total_rides': [200],
            'wins': [50],
            'places_2': [100],
            'places_3': [140]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_jockey_stats(mock_db, jockey_name='ルメール')

        assert result['jockey_name'] == 'ルメール'
        assert result['total_rides'] == 200
        assert result['wins'] == 50
        assert result['win_rate'] == 25.0

    def test_multiple_matches(self, mock_db):
        """複数の騎手がマッチした場合のテスト"""
        mock_result = pd.DataFrame({
            'jockey_name': ['武豊', '武幸四郎'],
            'total_rides': [300, 100],
            'wins': [60, 20],
            'places_2': [150, 50],
            'places_3': [210, 70]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_jockey_stats(mock_db, jockey_name='武')

        assert result['total_rides'] == 400
        assert result['wins'] == 80
        assert result['jockey_name'] == '武豊'
        assert len(result['matched_jockeys']) == 2

    def test_no_results(self, mock_db):
        """結果が0件の場合のテスト"""
        mock_result = pd.DataFrame()
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_jockey_stats(mock_db, jockey_name='存在しない騎手')

        assert result['total_rides'] == 0
        assert result['win_rate'] == 0.0

    def test_jockey_name_parameterized(self, mock_db):
        """騎手名がパラメータ化されているテスト"""
        mock_result = pd.DataFrame({
            'jockey_name': ['ルメール'],
            'total_rides': [200],
            'wins': [50],
            'places_2': [100],
            'places_3': [140]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        get_jockey_stats(mock_db, jockey_name='ルメール')

        query, params = _get_query_and_params(mock_db)
        assert "LIKE ?" in query
        assert '%ルメール%' in params
        # 値がSQL文に直接埋め込まれていないことを確認
        assert 'ルメール' not in query


class TestGetFrameStats:
    """get_frame_stats関数のテスト"""

    def test_basic_query(self, mock_db):
        """基本的なクエリのテスト"""
        mock_result = pd.DataFrame({
            'wakuban': ['1', '2', '3', '4', '5', '6', '7', '8'],
            'total': [100, 100, 100, 100, 100, 100, 100, 100],
            'wins': [10, 12, 15, 13, 14, 11, 9, 16],
            'places_2': [25, 28, 30, 27, 29, 26, 24, 31],
            'places_3': [40, 42, 45, 43, 44, 41, 39, 46]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        df = get_frame_stats(mock_db)

        assert len(df) == 8
        assert 'wakuban' in df.columns
        assert 'win_rate' in df.columns
        assert df['win_rate'].iloc[0] == 10.0

    def test_with_conditions(self, mock_db):
        """条件付きクエリのテスト（パラメータ化）"""
        mock_result = pd.DataFrame({
            'wakuban': ['1'],
            'total': [50],
            'wins': [5],
            'places_2': [15],
            'places_3': [25]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        df = get_frame_stats(mock_db, venue='東京', distance=1600)

        query, params = _get_query_and_params(mock_db)
        assert "JyoCD = ?" in query
        assert "Kyori = ?" in query
        assert '05' in params
        assert 1600 in params

    def test_empty_result(self, mock_db):
        """結果が空の場合のテスト"""
        mock_result = pd.DataFrame()
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        df = get_frame_stats(mock_db)

        assert df.empty
        assert list(df.columns) == ['wakuban', 'total', 'wins', 'places_2', 'places_3',
                                    'win_rate', 'place_rate_2', 'place_rate_3']


class TestGetHorseHistory:
    """get_horse_history関数のテスト"""

    def test_basic_query(self, mock_db):
        """基本的なクエリのテスト"""
        mock_result = pd.DataFrame({
            'race_date': ['2023-0521', '2023-0430'],
            'venue_code': ['05', '06'],
            'race_name': ['日本ダービー', '皐月賞'],
            'distance': ['2400', '2000'],
            'finish': ['01', '02'],
            'popularity': ['03', '02'],
            'jockey': ['ルメール', '武豊'],
            'time': ['022434', '020112'],
            'horse_name': ['テスト馬', 'テスト馬']
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        df = get_horse_history(mock_db, horse_name='テスト馬')

        assert len(df) == 2
        assert df['venue'].iloc[0] == '東京'
        assert df['venue'].iloc[1] == '中山'
        assert df['finish'].iloc[0] == 1
        assert df['popularity'].iloc[0] == 3

    def test_no_results(self, mock_db):
        """結果が0件の場合のテスト"""
        mock_result = pd.DataFrame()
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        df = get_horse_history(mock_db, horse_name='存在しない馬')

        assert df.empty

    def test_horse_name_parameterized(self, mock_db):
        """馬名がパラメータ化されているテスト"""
        mock_result = pd.DataFrame()
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        get_horse_history(mock_db, horse_name="テスト'; DROP TABLE--")

        query, params = _get_query_and_params(mock_db)
        assert "LIKE ?" in query
        assert "テスト'" not in query  # SQLに値が埋め込まれていない
        assert "%テスト'; DROP TABLE--%" in params


class TestGetSireStats:
    """get_sire_stats関数のテスト"""

    def test_basic_query(self, mock_db):
        """基本的なクエリのテスト"""
        mock_result = pd.DataFrame({
            'sire_name': ['ディープインパクト'],
            'total_runs': [1000],
            'wins': [200],
            'places_2': [400],
            'places_3': [600]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_sire_stats(mock_db, sire_name='ディープインパクト')

        assert result['sire_name'] == 'ディープインパクト'
        assert result['total_runs'] == 1000
        assert result['wins'] == 200
        assert result['win_rate'] == 20.0

    def test_with_conditions(self, mock_db):
        """条件付きクエリのテスト（パラメータ化）"""
        mock_result = pd.DataFrame({
            'sire_name': ['ディープインパクト'],
            'total_runs': [500],
            'wins': [100],
            'places_2': [200],
            'places_3': [300]
        })
        mock_db.execute_safe_query = Mock(return_value=mock_result)

        result = get_sire_stats(
            mock_db,
            sire_name='ディープインパクト',
            venue='東京',
            distance=1600
        )

        query, params = _get_query_and_params(mock_db)
        assert "Bamei1 LIKE ?" in query
        assert "JyoCD = ?" in query
        assert "Kyori = ?" in query
        assert '%ディープインパクト%' in params
        assert '05' in params
        assert 1600 in params


class TestConstants:
    """定数のテスト"""

    def test_venue_codes(self):
        """競馬場コードのテスト"""
        assert VENUE_CODES['東京'] == '05'
        assert VENUE_CODES['中山'] == '06'
        assert len(VENUE_CODES) == 10

    def test_grade_codes(self):
        """グレードコードのテスト"""
        assert GRADE_CODES['G1'] == 'A'
        assert GRADE_CODES['G2'] == 'B'
        assert GRADE_CODES['G3'] == 'C'
        assert GRADE_CODES['A'] == 'A'
