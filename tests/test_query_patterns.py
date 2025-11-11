# -*- coding: utf-8 -*-
"""
JVLink Database Query Pattern Tests

典型的な検索パターンを網羅的にテストします。
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.jvlink_mcp_server.database.connection import DatabaseConnection
from src.jvlink_mcp_server.database.schema_info import TRACK_CODES, GRADE_CODES


class QueryPatternTester:
    """クエリパターンのテスター"""

    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()
        self.test_results = []

    def run_test(self, test_name, query, description):
        """テストを実行して結果を記録"""
        print(f"\n{'='*80}")
        print(f"テスト: {test_name}")
        print(f"説明: {description}")
        print(f"{'='*80}")

        try:
            result = self.db.execute_safe_query(query)
            rows = len(result)
            success = True
            error = None

            print(f"✓ 成功: {rows}件のレコードを取得")

            # 結果の一部を表示（最大5件）
            if rows > 0:
                print(f"\n結果サンプル（最大5件）:")
                print(result.head(5).to_string())

            self.test_results.append({
                'test_name': test_name,
                'success': True,
                'rows': rows,
                'error': None
            })

        except Exception as e:
            print(f"✗ エラー: {str(e)}")
            self.test_results.append({
                'test_name': test_name,
                'success': False,
                'rows': 0,
                'error': str(e)
            })

    def test_race_search_patterns(self):
        """レース検索パターンのテスト"""
        print("\n" + "="*80)
        print("【カテゴリ1】レース検索パターン")
        print("="*80)

        # 1-1. 特定競馬場のレース検索
        self.run_test(
            "1-1. 特定競馬場のレース検索（東京競馬場）",
            """
            SELECT
                idYear, idMonthDay, idRaceNum,
                RaceInfoHondai as race_name,
                Kyori as distance
            FROM NL_RA_RACE
            WHERE idJyoCD = '05'
              AND idYear = '2024'
            ORDER BY idMonthDay DESC, idRaceNum
            LIMIT 10
            """,
            "東京競馬場（コード05）の2024年レースを検索"
        )

        # 1-2. 特定距離のレース検索
        self.run_test(
            "1-2. 特定距離のレース検索（1600m）",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                RaceInfoHondai as race_name,
                Kyori as distance
            FROM NL_RA_RACE
            WHERE Kyori = '1600'
              AND idYear = '2024'
            ORDER BY idMonthDay DESC
            LIMIT 10
            """,
            "1600mのレースを検索"
        )

        # 1-3. G1レース検索
        self.run_test(
            "1-3. G1レース検索",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                RaceInfoHondai as race_name,
                GradeCD as grade,
                Kyori as distance
            FROM NL_RA_RACE
            WHERE GradeCD = 'A'
              AND idYear = '2024'
            ORDER BY idMonthDay DESC
            LIMIT 10
            """,
            "G1レース（グレードコードA）を検索"
        )

        # 1-4. 芝レース検索
        self.run_test(
            "1-4. 芝レース検索",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                RaceInfoHondai as race_name,
                TrackCD as track_type,
                Kyori as distance
            FROM NL_RA_RACE
            WHERE TrackCD LIKE '1%'
              AND idYear = '2024'
            ORDER BY idMonthDay DESC
            LIMIT 10
            """,
            "芝コース（TrackCD 1で始まる）のレースを検索"
        )

        # 1-5. 良馬場のレース検索
        self.run_test(
            "1-5. 良馬場のレース検索",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                RaceInfoHondai as race_name,
                TenkoBabaSibaBabaCD as turf_condition
            FROM NL_RA_RACE
            WHERE TenkoBabaSibaBabaCD = '1'
              AND idYear = '2024'
            ORDER BY idMonthDay DESC
            LIMIT 10
            """,
            "芝・良馬場（コード1）のレースを検索"
        )

        # 1-6. 複合条件：東京・芝・1600m
        self.run_test(
            "1-6. 複合条件：東京・芝・1600m",
            """
            SELECT
                idYear, idMonthDay, idRaceNum,
                RaceInfoHondai as race_name,
                GradeCD as grade
            FROM NL_RA_RACE
            WHERE idJyoCD = '05'
              AND TrackCD LIKE '1%'
              AND Kyori = '1600'
              AND idYear = '2024'
            ORDER BY idMonthDay DESC
            LIMIT 10
            """,
            "東京競馬場の芝1600mレースを検索"
        )

    def test_jockey_performance_patterns(self):
        """騎手成績パターンのテスト"""
        print("\n" + "="*80)
        print("【カテゴリ2】騎手成績パターン")
        print("="*80)

        # 2-1. 特定騎手の全成績
        self.run_test(
            "2-1. 特定騎手の全成績（ルメール騎手）",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                Bamei as horse_name,
                KakuteiJyuni as finish,
                Ninki as popularity
            FROM NL_SE_RACE_UMA
            WHERE KisyuRyakusyo LIKE '%ルメール%'
              AND idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
            ORDER BY idMonthDay DESC
            LIMIT 20
            """,
            "ルメール騎手の2024年全成績"
        )

        # 2-2. 騎手の勝利数集計
        self.run_test(
            "2-2. 騎手別勝利数ランキング（2024年）",
            """
            SELECT
                KisyuRyakusyo as jockey_name,
                COUNT(*) as total_rides,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND KisyuRyakusyo IS NOT NULL
              AND LENGTH(KisyuRyakusyo) > 0
            GROUP BY KisyuRyakusyo
            HAVING COUNT(*) >= 50
            ORDER BY wins DESC
            LIMIT 20
            """,
            "2024年騎手別勝利数（50騎乗以上）"
        )

        # 2-3. 騎手の人気別成績
        self.run_test(
            "2-3. 特定騎手の人気別成績",
            """
            SELECT
                Ninki as popularity,
                COUNT(*) as rides,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN KakuteiJyuni IN ('01','02','03') THEN 1 ELSE 0 END) as top3
            FROM NL_SE_RACE_UMA
            WHERE KisyuRyakusyo LIKE '%ルメール%'
              AND idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND Ninki IN ('01','02','03','04','05')
            GROUP BY Ninki
            ORDER BY Ninki
            """,
            "ルメール騎手の人気別成績"
        )

        # 2-4. 騎手の競馬場別成績
        self.run_test(
            "2-4. 特定騎手の競馬場別成績",
            """
            SELECT
                idJyoCD as track_code,
                COUNT(*) as rides,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE KisyuRyakusyo LIKE '%ルメール%'
              AND idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND idJyoCD IN ('05','06','07','08','09')
            GROUP BY idJyoCD
            ORDER BY rides DESC
            """,
            "ルメール騎手の主要競馬場別成績"
        )

    def test_horse_search_patterns(self):
        """馬検索パターンのテスト"""
        print("\n" + "="*80)
        print("【カテゴリ3】馬検索パターン")
        print("="*80)

        # 3-1. 馬名検索
        self.run_test(
            "3-1. 馬名で検索",
            """
            SELECT
                KettoNum,
                Bamei as horse_name,
                Seibetsu as sex,
                Keiro as color
            FROM NL_UM_UMA
            WHERE Bamei LIKE '%ソダシ%'
            LIMIT 10
            """,
            "馬名「ソダシ」で検索"
        )

        # 3-2. 父馬で検索
        self.run_test(
            "3-2. 父馬で産駒検索",
            """
            SELECT
                Bamei as horse_name,
                FBamei as sire_name,
                BokuroBamei as dam_name,
                Tanjyobi as birthday
            FROM NL_UM_UMA
            WHERE FBamei LIKE '%ディープインパクト%'
            LIMIT 20
            """,
            "父ディープインパクトの産駒を検索"
        )

        # 3-3. 馬主名で検索
        self.run_test(
            "3-3. 馬主名で検索",
            """
            SELECT
                Bamei as horse_name,
                BanusiName as owner_name,
                ChokyosiRyakusyo as trainer_name
            FROM NL_UM_UMA
            WHERE BanusiName LIKE '%サンデーレーシング%'
            LIMIT 20
            """,
            "馬主「サンデーレーシング」の所有馬を検索"
        )

        # 3-4. 特定馬の戦績
        self.run_test(
            "3-4. 特定馬の戦績取得",
            """
            SELECT
                ru.idYear, ru.idMonthDay, ru.idJyoCD, ru.idRaceNum,
                r.RaceInfoHondai as race_name,
                ru.KakuteiJyuni as finish,
                ru.Ninki as popularity,
                ru.KisyuRyakusyo as jockey_name
            FROM NL_SE_RACE_UMA ru
            LEFT JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE ru.Bamei LIKE '%ソダシ%'
              AND ru.KakuteiJyuni IS NOT NULL
              AND LENGTH(ru.KakuteiJyuni) > 0
            ORDER BY ru.idYear DESC, ru.idMonthDay DESC
            LIMIT 20
            """,
            "ソダシの全戦績を取得"
        )

    def test_race_result_analysis_patterns(self):
        """レース結果分析パターンのテスト"""
        print("\n" + "="*80)
        print("【カテゴリ4】レース結果分析パターン")
        print("="*80)

        # 4-1. 1番人気の成績
        self.run_test(
            "4-1. 1番人気の成績分析",
            """
            SELECT
                COUNT(*) as total_races,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN KakuteiJyuni IN ('01','02') THEN 1 ELSE 0 END) as top2,
                SUM(CASE WHEN KakuteiJyuni IN ('01','02','03') THEN 1 ELSE 0 END) as top3,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE Ninki = '01'
              AND idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
            """,
            "2024年1番人気の成績（勝率・連対率・複勝率）"
        )

        # 4-2. 人気別成績比較
        self.run_test(
            "4-2. 人気別成績比較",
            """
            SELECT
                Ninki as popularity,
                COUNT(*) as total_races,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND Ninki IN ('01','02','03','04','05','06','07','08','09','10')
            GROUP BY Ninki
            ORDER BY Ninki
            """,
            "人気別（1-10番人気）の勝率比較"
        )

        # 4-3. 枠番別成績
        self.run_test(
            "4-3. 枠番別成績分析",
            """
            SELECT
                Wakuban as bracket,
                COUNT(*) as total_races,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND Wakuban IN ('1','2','3','4','5','6','7','8')
            GROUP BY Wakuban
            ORDER BY Wakuban
            """,
            "2024年枠番別成績"
        )

        # 4-4. 馬体重変化と成績
        self.run_test(
            "4-4. 馬体重増減別成績",
            """
            SELECT
                CASE
                    WHEN CAST(ZogenSa AS INTEGER) >= 10 THEN '+10kg以上'
                    WHEN CAST(ZogenSa AS INTEGER) >= 5 THEN '+5~9kg'
                    WHEN CAST(ZogenSa AS INTEGER) >= 0 THEN '±0~4kg'
                    WHEN CAST(ZogenSa AS INTEGER) >= -5 THEN '-1~5kg'
                    WHEN CAST(ZogenSa AS INTEGER) >= -10 THEN '-6~10kg'
                    ELSE '-11kg以上'
                END as weight_change,
                COUNT(*) as total_races,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND ZogenSa IS NOT NULL
              AND LENGTH(ZogenSa) > 0
              AND ZogenSa != '0'
            GROUP BY weight_change
            ORDER BY weight_change
            """,
            "馬体重増減別の成績"
        )

    def test_trainer_performance_patterns(self):
        """調教師成績パターンのテスト"""
        print("\n" + "="*80)
        print("【カテゴリ5】調教師成績パターン")
        print("="*80)

        # 5-1. 調教師別勝利数
        self.run_test(
            "5-1. 調教師別勝利数ランキング",
            """
            SELECT
                ChokyosiRyakusyo as trainer_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND ChokyosiRyakusyo IS NOT NULL
              AND LENGTH(ChokyosiRyakusyo) > 0
            GROUP BY ChokyosiRyakusyo
            HAVING COUNT(*) >= 50
            ORDER BY wins DESC
            LIMIT 20
            """,
            "2024年調教師別勝利数（50出走以上）"
        )

        # 5-2. 特定調教師の競馬場別成績
        self.run_test(
            "5-2. 特定調教師の競馬場別成績",
            """
            SELECT
                idJyoCD as track_code,
                COUNT(*) as runs,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE ChokyosiRyakusyo LIKE '%藤沢和%'
              AND idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND idJyoCD IN ('05','06','07','08','09')
            GROUP BY idJyoCD
            ORDER BY runs DESC
            """,
            "藤沢和雄調教師の競馬場別成績"
        )

    def test_combined_advanced_patterns(self):
        """複合条件・高度な分析パターンのテスト"""
        print("\n" + "="*80)
        print("【カテゴリ6】複合条件・高度な分析パターン")
        print("="*80)

        # 6-1. 騎手×調教師コンビの成績
        self.run_test(
            "6-1. 騎手×調教師コンビ成績",
            """
            SELECT
                KisyuRyakusyo as jockey_name,
                ChokyosiRyakusyo as trainer_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND LENGTH(KakuteiJyuni) > 0
              AND KisyuRyakusyo IS NOT NULL
              AND ChokyosiRyakusyo IS NOT NULL
            GROUP BY KisyuRyakusyo, ChokyosiRyakusyo
            HAVING COUNT(*) >= 10
            ORDER BY wins DESC
            LIMIT 20
            """,
            "騎手×調教師コンビ成績（10回以上）"
        )

        # 6-2. 特定条件でのレース結果統計
        self.run_test(
            "6-2. 東京芝1600m・良馬場の人気別成績",
            """
            SELECT
                ru.Ninki as popularity,
                COUNT(*) as total_races,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA ru
            JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE r.idJyoCD = '05'
              AND r.Kyori = '1600'
              AND r.TrackCD LIKE '1%'
              AND r.TenkoBabaSibaBabaCD = '1'
              AND ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND LENGTH(ru.KakuteiJyuni) > 0
              AND ru.Ninki IN ('01','02','03','04','05')
            GROUP BY ru.Ninki
            ORDER BY ru.Ninki
            """,
            "東京芝1600m良馬場での人気別成績"
        )

        # 6-3. 血統別成績（父馬）
        self.run_test(
            "6-3. 血統（父馬）別成績",
            """
            SELECT
                u.FBamei as sire_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA ru
            JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
            WHERE ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND LENGTH(ru.KakuteiJyuni) > 0
              AND u.FBamei IS NOT NULL
              AND LENGTH(u.FBamei) > 0
            GROUP BY u.FBamei
            HAVING COUNT(*) >= 30
            ORDER BY wins DESC
            LIMIT 20
            """,
            "2024年父馬別成績（30頭以上出走）"
        )

    def test_datetime_patterns(self):
        """日付・期間検索パターンのテスト"""
        print("\n" + "="*80)
        print("【カテゴリ7】日付・期間検索パターン")
        print("="*80)

        # 7-1. 特定月のレース
        self.run_test(
            "7-1. 特定月のレース検索",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                RaceInfoHondai as race_name
            FROM NL_RA_RACE
            WHERE idYear = '2024'
              AND idMonthDay LIKE '10%'
            ORDER BY idMonthDay, idJyoCD, idRaceNum
            LIMIT 20
            """,
            "2024年10月のレースを検索"
        )

        # 7-2. 期間指定検索
        self.run_test(
            "7-2. 期間指定のレース検索",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                RaceInfoHondai as race_name
            FROM NL_RA_RACE
            WHERE idYear = '2024'
              AND idMonthDay BETWEEN '1001' AND '1031'
            ORDER BY idMonthDay, idJyoCD, idRaceNum
            LIMIT 20
            """,
            "2024年10月1日～31日のレースを検索"
        )

        # 7-3. 最新N件のレース
        self.run_test(
            "7-3. 最新レースの取得",
            """
            SELECT
                idYear, idMonthDay, idJyoCD, idRaceNum,
                RaceInfoHondai as race_name
            FROM NL_RA_RACE
            WHERE idYear = '2024'
            ORDER BY idYear DESC, idMonthDay DESC, idJyoCD DESC, idRaceNum DESC
            LIMIT 20
            """,
            "2024年の最新20レースを取得"
        )

    def run_all_tests(self):
        """全テストを実行"""
        print("\n" + "="*80)
        print("JVLink Database Query Pattern Tests")
        print("網羅的クエリパターンテスト")
        print("="*80)

        self.test_race_search_patterns()
        self.test_jockey_performance_patterns()
        self.test_horse_search_patterns()
        self.test_race_result_analysis_patterns()
        self.test_trainer_performance_patterns()
        self.test_combined_advanced_patterns()
        self.test_datetime_patterns()

        # サマリー表示
        self.print_summary()

    def print_summary(self):
        """テスト結果のサマリーを表示"""
        print("\n" + "="*80)
        print("テスト結果サマリー")
        print("="*80)

        total = len(self.test_results)
        success = sum(1 for r in self.test_results if r['success'])
        failed = total - success

        print(f"\n総テスト数: {total}")
        print(f"成功: {success} ({success*100//total}%)")
        print(f"失敗: {failed} ({failed*100//total if total > 0 else 0}%)")

        if failed > 0:
            print("\n失敗したテスト:")
            for r in self.test_results:
                if not r['success']:
                    print(f"  ✗ {r['test_name']}")
                    print(f"    エラー: {r['error']}")

        print("\n" + "="*80)
        print("全テスト完了")
        print("="*80)

    def close(self):
        """データベース接続を閉じる"""
        self.db.close()


def main():
    """メイン処理"""
    tester = QueryPatternTester()
    try:
        tester.run_all_tests()
    finally:
        tester.close()


if __name__ == '__main__':
    main()
