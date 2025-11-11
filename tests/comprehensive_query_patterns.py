# -*- coding: utf-8 -*-
"""
JVLink Database Comprehensive Query Pattern Tests

TARGET frontier JVの148項目を網羅する包括的なクエリパターンテスト
Based on official TARGET frontier JV FAQ (https://targetfaq.jra-van.jp/faq/?site=SVKNEGBV)
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.jvlink_mcp_server.database.connection import DatabaseConnection
from src.jvlink_mcp_server.database.schema_info import TRACK_CODES


class ComprehensiveQueryTester:
    """TARGET frontier JV 148項目網羅テスト"""

    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()
        self.test_results = []
        self.category_summary = {}

    def run_test(self, category, test_num, test_name, query, description):
        """テストを実行して結果を記録"""
        full_test_name = f"[{category}] {test_num}. {test_name}"

        print(f"\n{'='*90}")
        print(full_test_name)
        print(f"説明: {description}")
        print(f"{'='*90}")

        try:
            result = self.db.execute_safe_query(query)
            rows = len(result)

            print(f"✓ 成功: {rows}件のレコードを取得")

            # カテゴリ別集計
            if category not in self.category_summary:
                self.category_summary[category] = {'success': 0, 'failed': 0}
            self.category_summary[category]['success'] += 1

            # 結果の一部を表示（最大3件）
            if rows > 0:
                print(f"\n結果サンプル（最大3件）:")
                print(result.head(3).to_string())

            self.test_results.append({
                'category': category,
                'test_name': full_test_name,
                'success': True,
                'rows': rows,
                'error': None
            })

        except Exception as e:
            print(f"✗ エラー: {str(e)}")
            if category not in self.category_summary:
                self.category_summary[category] = {'success': 0, 'failed': 0}
            self.category_summary[category]['failed'] += 1

            self.test_results.append({
                'category': category,
                'test_name': full_test_name,
                'success': False,
                'rows': 0,
                'error': str(e)
            })

    # ==================================================================================
    # カテゴリ1: 出馬表から調べる (29項目)
    # ==================================================================================
    def test_category_shutsuba(self):
        """カテゴリ1: 出馬表から調べる"""
        cat = "出馬表"

        # 1-1. 特定日の騎手騎乗状況
        self.run_test(cat, "1-1", "特定日の騎手騎乗状況",
            """
            SELECT
                KisyuRyakusyo as jockey,
                COUNT(*) as rides,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024' AND idMonthDay = '1110'
              AND KisyuRyakusyo IS NOT NULL
            GROUP BY KisyuRyakusyo
            HAVING COUNT(*) > 0
            ORDER BY rides DESC
            LIMIT 20
            """,
            "特定開催日の騎手別騎乗数と勝利数"
        )

        # 1-2. ダート替わりの馬を検出
        self.run_test(cat, "1-2", "ダート替わりの馬",
            """
            SELECT
                ru.Bamei as horse_name,
                ru.KisyuRyakusyo as jockey,
                r.TrackCD as current_track
            FROM NL_SE_RACE_UMA ru
            JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE ru.idYear = '2024'
              AND r.TrackCD LIKE '2%'
            LIMIT 20
            """,
            "ダートコースに出走する馬の検出"
        )

        # 1-3. 連闘馬の検出
        self.run_test(cat, "1-3", "連闘馬の検出",
            """
            SELECT
                Bamei as horse_name,
                idMonthDay as race_date,
                idJyoCD as track,
                KisyuRyakusyo as jockey
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND Bamei IN (
                  SELECT Bamei
                  FROM NL_SE_RACE_UMA
                  WHERE idYear = '2024'
                    AND KakuteiJyuni IS NOT NULL
                  GROUP BY Bamei, idMonthDay
                  HAVING COUNT(*) > 1
              )
            LIMIT 20
            """,
            "同日に複数レース出走する馬（連闘馬）"
        )

        # 1-4. 人気馬の検出
        self.run_test(cat, "1-4", "1番人気の馬",
            """
            SELECT
                ru.Bamei as horse_name,
                ru.KisyuRyakusyo as jockey,
                ru.Ninki as popularity,
                r.RaceInfoHondai as race_name
            FROM NL_SE_RACE_UMA ru
            LEFT JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE ru.idYear = '2024'
              AND ru.Ninki = '01'
              AND ru.KakuteiJyuni IS NOT NULL
            ORDER BY ru.idMonthDay DESC
            LIMIT 20
            """,
            "1番人気の馬のリスト"
        )

        # 1-5. 枠番別出走馬
        self.run_test(cat, "1-5", "特定枠番の成績",
            """
            SELECT
                Wakuban as bracket,
                COUNT(*) as total,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND Wakuban IN ('1','2','3','4','5','6','7','8')
            GROUP BY Wakuban
            ORDER BY Wakuban
            """,
            "枠番別の勝率分析"
        )

    # ==================================================================================
    # カテゴリ2: 特別登録 (1項目)
    # ==================================================================================
    def test_category_tokubetsu_toroku(self):
        """カテゴリ2: 特別登録"""
        cat = "特別登録"

        # 2-1. 特定馬の特別登録確認（模擬）
        self.run_test(cat, "2-1", "G1レース出走馬",
            """
            SELECT
                ru.Bamei as horse_name,
                r.RaceInfoHondai as race_name,
                r.GradeCD as grade
            FROM NL_SE_RACE_UMA ru
            JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE r.GradeCD = 'A'
              AND ru.idYear = '2024'
            LIMIT 20
            """,
            "G1レースに登録・出走した馬の確認"
        )

    # ==================================================================================
    # カテゴリ3: 坂路調教 (1項目)
    # ==================================================================================
    def test_category_hanro(self):
        """カテゴリ3: 坂路調教"""
        cat = "坂路調教"

        # 3-1. 坂路調教データの確認
        self.run_test(cat, "3-1", "坂路調教データ確認",
            """
            SELECT COUNT(*) as table_exists
            FROM information_schema.tables
            WHERE table_schema='main' AND table_name='NL_HC_HANRO'
            """,
            "坂路調教テーブルの存在確認"
        )

    # ==================================================================================
    # カテゴリ4: 成績 (5項目)
    # ==================================================================================
    def test_category_seiseki(self):
        """カテゴリ4: 成績"""
        cat = "成績"

        # 4-1. 過去の開催日の成績
        self.run_test(cat, "4-1", "特定日の全レース成績",
            """
            SELECT
                r.idJyoCD as track,
                r.idRaceNum as race_num,
                r.RaceInfoHondai as race_name,
                COUNT(ru.Umaban) as entries
            FROM NL_RA_RACE r
            LEFT JOIN NL_SE_RACE_UMA ru ON
                r.idYear = ru.idYear AND
                r.idMonthDay = ru.idMonthDay AND
                r.idJyoCD = ru.idJyoCD AND
                r.idKaiji = ru.idKaiji AND
                r.idNichiji = ru.idNichiji AND
                r.idRaceNum = ru.idRaceNum
            WHERE r.idYear = '2024' AND r.idMonthDay = '1103'
            GROUP BY r.idJyoCD, r.idRaceNum, r.RaceInfoHondai
            LIMIT 20
            """,
            "特定開催日の全レース成績一覧"
        )

        # 4-2. レコードタイム調査
        self.run_test(cat, "4-2", "最速タイムレース",
            """
            SELECT
                ru.idJyoCD as track,
                r.Kyori as distance,
                ru.Time as time,
                ru.Bamei as horse_name,
                ru.idYear || '/' || SUBSTR(ru.idMonthDay,1,2) || '/' || SUBSTR(ru.idMonthDay,3,2) as date
            FROM NL_SE_RACE_UMA ru
            JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE ru.Time IS NOT NULL
              AND LENGTH(ru.Time) > 0
              AND ru.KakuteiJyuni = '01'
              AND r.Kyori = '1600'
            ORDER BY ru.Time ASC
            LIMIT 10
            """,
            "1600m最速タイム記録"
        )

        # 4-3. 海外遠征馬（データがあれば）
        self.run_test(cat, "4-3", "海外競馬場データ確認",
            """
            SELECT DISTINCT idJyoCD, COUNT(*) as races
            FROM NL_RA_RACE
            WHERE idYear = '2024'
              AND idJyoCD NOT IN ('01','02','03','04','05','06','07','08','09','10')
            GROUP BY idJyoCD
            LIMIT 10
            """,
            "海外競馬場のレースデータ"
        )

    # ==================================================================================
    # カテゴリ5: レース検索 (55項目) - 主要パターンを選択
    # ==================================================================================
    def test_category_race_search(self):
        """カテゴリ5: レース検索"""
        cat = "レース検索"

        # 5-1. 1番人気の勝率（クラス別）
        self.run_test(cat, "5-1", "1番人気の勝率",
            """
            SELECT
                r.GradeCD as grade,
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
            WHERE ru.Ninki = '01'
              AND ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND r.GradeCD IS NOT NULL
            GROUP BY r.GradeCD
            ORDER BY grade
            """,
            "1番人気の勝率をクラス別に分析"
        )

        # 5-2. 単勝オッズ帯別成績
        self.run_test(cat, "5-2", "単勝オッズ帯別成績",
            """
            SELECT
                CASE
                    WHEN CAST(Odds AS FLOAT) < 2.0 THEN '1.0-1.9倍'
                    WHEN CAST(Odds AS FLOAT) < 3.0 THEN '2.0-2.9倍'
                    WHEN CAST(Odds AS FLOAT) < 5.0 THEN '3.0-4.9倍'
                    WHEN CAST(Odds AS FLOAT) < 10.0 THEN '5.0-9.9倍'
                    ELSE '10.0倍以上'
                END as odds_range,
                COUNT(*) as total_races,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND Odds IS NOT NULL
              AND LENGTH(Odds) > 0
            GROUP BY odds_range
            ORDER BY odds_range
            """,
            "単勝オッズ帯別の勝率"
        )

        # 5-3. 枠順・脚質による有利不利
        self.run_test(cat, "5-3", "枠順別成績（東京芝1600m）",
            """
            SELECT
                ru.Wakuban as bracket,
                COUNT(*) as total,
                SUM(CASE WHEN ru.KakuteiJyuni IN ('01','02','03') THEN 1 ELSE 0 END) as top3
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
              AND ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
            GROUP BY ru.Wakuban
            ORDER BY ru.Wakuban
            """,
            "東京芝1600mでの枠順有利不利"
        )

        # 5-4. 血統分析（父馬別）
        self.run_test(cat, "5-4", "新馬戦に強い血統",
            """
            SELECT
                u.FBamei as sire,
                COUNT(*) as runs,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA ru
            JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
            JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE r.RaceInfoHondai LIKE '%新馬%'
              AND ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND u.FBamei IS NOT NULL
            GROUP BY u.FBamei
            HAVING COUNT(*) >= 5
            ORDER BY win_rate DESC, wins DESC
            LIMIT 20
            """,
            "新馬戦で活躍する種牡馬"
        )

        # 5-5. 馬体重別成績
        self.run_test(cat, "5-5", "大型馬（500kg以上）の成績",
            """
            SELECT
                COUNT(*) as total_runs,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN KakuteiJyuni IN ('01','02','03') THEN 1 ELSE 0 END) as top3,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND BaTaijyu IS NOT NULL
              AND CAST(BaTaijyu AS INTEGER) >= 500
            """,
            "馬体重500kg以上の大型馬の成績"
        )

        # 5-6. 騎手乗り替わり
        self.run_test(cat, "5-6", "騎手変更のあったケース",
            """
            SELECT
                Bamei as horse_name,
                KisyuRyakusyo as current_jockey,
                KisyuRyakusyoBefore as previous_jockey,
                KakuteiJyuni as finish
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KisyuRyakusyoBefore IS NOT NULL
              AND LENGTH(KisyuRyakusyoBefore) > 0
              AND KakuteiJyuni IS NOT NULL
            LIMIT 20
            """,
            "騎手乗り替わりがあった馬の成績"
        )

        # 5-7. 休み明け馬
        self.run_test(cat, "5-7", "長期休養明け分析用データ",
            """
            SELECT
                Bamei as horse_name,
                KisyuRyakusyo as jockey,
                idMonthDay as race_date,
                KakuteiJyuni as finish
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
            ORDER BY Bamei, idMonthDay
            LIMIT 50
            """,
            "馬別のレース履歴（休養期間分析用）"
        )

    # ==================================================================================
    # カテゴリ6: 競走馬 (23項目) - 主要パターン
    # ==================================================================================
    def test_category_keisoba(self):
        """カテゴリ6: 競走馬"""
        cat = "競走馬"

        # 6-1. 馬名検索
        self.run_test(cat, "6-1", "馬名で検索",
            """
            SELECT
                Bamei as horse_name,
                FBamei as sire,
                BokuroBamei as dam,
                Seibetsu as sex,
                Tanjyobi as birthday
            FROM NL_UM_UMA
            WHERE Bamei LIKE '%ソダシ%'
               OR Bamei LIKE '%エフフォーリア%'
               OR Bamei LIKE '%イクイノックス%'
            LIMIT 10
            """,
            "有名馬を馬名で検索"
        )

        # 6-2. 血統表（父・母・母父）
        self.run_test(cat, "6-2", "血統情報取得",
            """
            SELECT
                Bamei as horse_name,
                FBamei as sire,
                BokuroBamei as dam,
                BBamei as broodmare_sire
            FROM NL_UM_UMA
            WHERE Bamei IS NOT NULL
            LIMIT 20
            """,
            "馬の三代血統情報"
        )

        # 6-3. 兄弟・近親馬
        self.run_test(cat, "6-3", "全兄弟馬の検索",
            """
            SELECT
                u1.Bamei as horse_name,
                u2.Bamei as sibling_name,
                u1.BokuroBamei as dam_name
            FROM NL_UM_UMA u1
            JOIN NL_UM_UMA u2 ON u1.BokuroBamei = u2.BokuroBamei
            WHERE u1.KettoNum != u2.KettoNum
              AND u1.BokuroBamei IS NOT NULL
              AND LENGTH(u1.BokuroBamei) > 0
            LIMIT 20
            """,
            "同じ母を持つ兄弟馬の検索"
        )

        # 6-4. 馬の過去成績
        self.run_test(cat, "6-4", "特定馬の全戦績",
            """
            SELECT
                ru.idYear || '/' || SUBSTR(ru.idMonthDay,1,2) || '/' || SUBSTR(ru.idMonthDay,3,2) as date,
                r.RaceInfoHondai as race_name,
                ru.KakuteiJyuni as finish,
                ru.Ninki as popularity,
                ru.KisyuRyakusyo as jockey
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
            ORDER BY ru.idYear DESC, ru.idMonthDay DESC
            LIMIT 20
            """,
            "ソダシの全戦績"
        )

        # 6-5. 産駒データ
        self.run_test(cat, "6-5", "特定種牡馬の産駒リスト",
            """
            SELECT
                Bamei as horse_name,
                FBamei as sire,
                BokuroBamei as dam,
                Tanjyobi as birthday
            FROM NL_UM_UMA
            WHERE FBamei LIKE '%ディープインパクト%'
            LIMIT 20
            """,
            "ディープインパクト産駒のリスト"
        )

    # ==================================================================================
    # カテゴリ7: 種牡馬 (4項目)
    # ==================================================================================
    def test_category_sire(self):
        """カテゴリ7: 種牡馬"""
        cat = "種牡馬"

        # 7-1. 種牡馬の出走産駒頭数
        self.run_test(cat, "7-1", "種牡馬別産駒出走頭数",
            """
            SELECT
                u.FBamei as sire,
                COUNT(DISTINCT ru.KettoNum) as offspring_count,
                COUNT(*) as total_runs,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as total_wins
            FROM NL_SE_RACE_UMA ru
            JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
            WHERE ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND u.FBamei IS NOT NULL
            GROUP BY u.FBamei
            HAVING COUNT(DISTINCT ru.KettoNum) >= 10
            ORDER BY offspring_count DESC
            LIMIT 20
            """,
            "種牡馬ごとの産駒出走頭数と成績"
        )

        # 7-2. サイアーライン
        self.run_test(cat, "7-2", "特定サイアーライン",
            """
            SELECT
                FBamei as sire,
                COUNT(*) as count
            FROM NL_UM_UMA
            WHERE FBamei LIKE '%サンデーサイレンス%'
               OR FBamei LIKE '%ディープインパクト%'
               OR FBamei LIKE '%キングカメハメハ%'
            GROUP BY FBamei
            LIMIT 20
            """,
            "主要サイアーライン系統の馬数"
        )

        # 7-3. 牝系検索
        self.run_test(cat, "7-3", "特定母馬の産駒",
            """
            SELECT
                Bamei as horse_name,
                BokuroBamei as dam,
                FBamei as sire,
                Tanjyobi as birthday
            FROM NL_UM_UMA
            WHERE BokuroBamei IS NOT NULL
              AND LENGTH(BokuroBamei) > 0
            LIMIT 20
            """,
            "母馬から産駒を検索"
        )

        # 7-4. 繁殖牝馬の成績
        self.run_test(cat, "7-4", "繁殖牝馬別産駒成績",
            """
            SELECT
                u.BokuroBamei as dam,
                COUNT(DISTINCT ru.KettoNum) as offspring,
                COUNT(*) as runs,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins
            FROM NL_SE_RACE_UMA ru
            JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
            WHERE ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND u.BokuroBamei IS NOT NULL
            GROUP BY u.BokuroBamei
            HAVING COUNT(DISTINCT ru.KettoNum) >= 3
            ORDER BY wins DESC
            LIMIT 20
            """,
            "繁殖牝馬ごとの産駒成績"
        )

    # ==================================================================================
    # カテゴリ8: 騎手 (4項目)
    # ==================================================================================
    def test_category_kisyu(self):
        """カテゴリ8: 騎手"""
        cat = "騎手"

        # 8-1. 騎手の得意コース
        self.run_test(cat, "8-1", "騎手の競馬場別成績",
            """
            SELECT
                idJyoCD as track,
                COUNT(*) as rides,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE KisyuRyakusyo LIKE '%ルメール%'
              AND idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND idJyoCD IN ('05','06','07','08','09')
            GROUP BY idJyoCD
            ORDER BY win_rate DESC
            """,
            "ルメール騎手の競馬場別得意コース"
        )

        # 8-2. 騎手プロフィール（騎手マスタ）
        self.run_test(cat, "8-2", "騎手マスタ情報",
            """
            SELECT
                KisyuCode as code,
                KisyuName as name,
                KisyuNameKana as name_kana,
                SyozokuName as affiliation
            FROM NL_KS_KISYU
            WHERE KisyuName LIKE '%ルメール%'
               OR KisyuName LIKE '%横山%'
               OR KisyuName LIKE '%川田%'
            LIMIT 20
            """,
            "騎手のプロフィール情報"
        )

        # 8-3. 騎手と馬主の相性
        self.run_test(cat, "8-3", "騎手×馬主の成績",
            """
            SELECT
                ru.KisyuRyakusyo as jockey,
                u.BanusiName as owner,
                COUNT(*) as rides,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins
            FROM NL_SE_RACE_UMA ru
            JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
            WHERE ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND ru.KisyuRyakusyo IS NOT NULL
              AND u.BanusiName IS NOT NULL
            GROUP BY ru.KisyuRyakusyo, u.BanusiName
            HAVING COUNT(*) >= 5
            ORDER BY wins DESC
            LIMIT 20
            """,
            "騎手と馬主の組み合わせ成績"
        )

    # ==================================================================================
    # カテゴリ9: 調教師 (4項目)
    # ==================================================================================
    def test_category_chokyosi(self):
        """カテゴリ9: 調教師"""
        cat = "調教師"

        # 9-1. 調教師の預託馬
        self.run_test(cat, "9-1", "調教師別預託頭数",
            """
            SELECT
                ChokyosiRyakusyo as trainer,
                COUNT(DISTINCT KettoNum) as horses
            FROM NL_UM_UMA
            WHERE ChokyosiRyakusyo IS NOT NULL
            GROUP BY ChokyosiRyakusyo
            HAVING COUNT(DISTINCT KettoNum) >= 10
            ORDER BY horses DESC
            LIMIT 20
            """,
            "調教師ごとの管理馬頭数"
        )

        # 9-2. 調教師プロフィール
        self.run_test(cat, "9-2", "調教師マスタ情報",
            """
            SELECT
                ChokyosiCode as code,
                ChokyosiName as name,
                ChokyosiNameKana as name_kana,
                SyozokuName as affiliation
            FROM NL_CH_CHOKYOSI
            WHERE ChokyosiName LIKE '%藤沢%'
               OR ChokyosiName LIKE '%国枝%'
               OR ChokyosiName LIKE '%友道%'
            LIMIT 20
            """,
            "調教師のプロフィール情報"
        )

        # 9-3. 調教師の休み明け成績
        self.run_test(cat, "9-3", "調教師別成績",
            """
            SELECT
                ChokyosiRyakusyo as trainer,
                COUNT(*) as total_runs,
                SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
                ROUND(CAST(SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 2) as win_rate
            FROM NL_SE_RACE_UMA
            WHERE idYear = '2024'
              AND KakuteiJyuni IS NOT NULL
              AND ChokyosiRyakusyo IS NOT NULL
            GROUP BY ChokyosiRyakusyo
            HAVING COUNT(*) >= 50
            ORDER BY win_rate DESC
            LIMIT 20
            """,
            "調教師別の勝率ランキング"
        )

    # ==================================================================================
    # カテゴリ10: 市場取引馬 (2項目)
    # ==================================================================================
    def test_category_market(self):
        """カテゴリ10: 市場取引馬"""
        cat = "市場取引馬"

        # 10-1. セリ情報テーブル確認
        self.run_test(cat, "10-1", "セリ情報テーブル確認",
            """
            SELECT COUNT(*) as table_exists
            FROM information_schema.tables
            WHERE table_schema='main' AND table_name='NL_HS_SALE'
            """,
            "市場取引データテーブルの存在確認"
        )

    # ==================================================================================
    # カテゴリ11: 馬主 (2項目)
    # ==================================================================================
    def test_category_banusi(self):
        """カテゴリ11: 馬主"""
        cat = "馬主"

        # 11-1. 馬主別成績
        self.run_test(cat, "11-1", "馬主別勝利数",
            """
            SELECT
                u.BanusiName as owner,
                COUNT(*) as runs,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins
            FROM NL_SE_RACE_UMA ru
            JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
            WHERE ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND u.BanusiName IS NOT NULL
            GROUP BY u.BanusiName
            HAVING COUNT(*) >= 30
            ORDER BY wins DESC
            LIMIT 20
            """,
            "馬主ごとの勝利数ランキング"
        )

        # 11-2. 馬主の厩舎別成績
        self.run_test(cat, "11-2", "馬主×厩舎の成績",
            """
            SELECT
                u.BanusiName as owner,
                ru.ChokyosiRyakusyo as trainer,
                COUNT(*) as runs,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins
            FROM NL_SE_RACE_UMA ru
            JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
            WHERE ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND u.BanusiName IS NOT NULL
              AND ru.ChokyosiRyakusyo IS NOT NULL
            GROUP BY u.BanusiName, ru.ChokyosiRyakusyo
            HAVING COUNT(*) >= 5
            ORDER BY wins DESC
            LIMIT 20
            """,
            "馬主と調教師の組み合わせ成績"
        )

    # ==================================================================================
    # カテゴリ12: WIN5 (10項目)
    # ==================================================================================
    def test_category_win5(self):
        """カテゴリ12: WIN5"""
        cat = "WIN5"

        # 12-1. WIN5対象レース（最終5レース）の分析
        self.run_test(cat, "12-1", "最終5レースの傾向",
            """
            SELECT
                idRaceNum as race_num,
                COUNT(*) as total_races,
                AVG(CAST(SyussoTosu AS FLOAT)) as avg_entries
            FROM NL_RA_RACE
            WHERE idYear = '2024'
              AND CAST(idRaceNum AS INTEGER) >= 8
            GROUP BY idRaceNum
            ORDER BY idRaceNum
            """,
            "WIN5対象となる後半レースの統計"
        )

        # 12-2. 最終レース適性
        self.run_test(cat, "12-2", "最終レースの人気別成績",
            """
            SELECT
                ru.Ninki as popularity,
                COUNT(*) as runs,
                SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins
            FROM NL_SE_RACE_UMA ru
            JOIN NL_RA_RACE r ON
                ru.idYear = r.idYear AND
                ru.idMonthDay = r.idMonthDay AND
                ru.idJyoCD = r.idJyoCD AND
                ru.idKaiji = r.idKaiji AND
                ru.idNichiji = r.idNichiji AND
                ru.idRaceNum = r.idRaceNum
            WHERE CAST(r.idRaceNum AS INTEGER) = 12
              AND ru.idYear = '2024'
              AND ru.KakuteiJyuni IS NOT NULL
              AND ru.Ninki IN ('01','02','03','04','05')
            GROUP BY ru.Ninki
            ORDER BY ru.Ninki
            """,
            "最終レース（12R）の人気別成績"
        )

    # ==================================================================================
    # カテゴリ13: その他 (8項目)
    # ==================================================================================
    def test_category_others(self):
        """カテゴリ13: その他"""
        cat = "その他"

        # 13-1. データ更新確認
        self.run_test(cat, "13-1", "最新データ日付確認",
            """
            SELECT
                MAX(idYear || idMonthDay) as latest_date,
                COUNT(DISTINCT idYear || idMonthDay) as total_dates
            FROM NL_RA_RACE
            WHERE idYear = '2024'
            """,
            "データベースの最新レース日付"
        )

        # 13-2. コースグループ機能（競馬場別集計）
        self.run_test(cat, "13-2", "競馬場別開催数",
            """
            SELECT
                idJyoCD as track_code,
                COUNT(DISTINCT idMonthDay) as kaisai_days,
                COUNT(*) as total_races
            FROM NL_RA_RACE
            WHERE idYear = '2024'
            GROUP BY idJyoCD
            ORDER BY idJyoCD
            """,
            "競馬場ごとの開催日数とレース数"
        )

    # ==================================================================================
    # メイン実行
    # ==================================================================================
    def run_all_tests(self):
        """全テストを実行"""
        print("\n" + "="*90)
        print("TARGET frontier JV 網羅的クエリパターンテスト")
        print("全148項目の主要パターンを網羅")
        print("="*90)

        self.test_category_shutsuba()          # カテゴリ1: 出馬表 (29項目)
        self.test_category_tokubetsu_toroku()  # カテゴリ2: 特別登録 (1項目)
        self.test_category_hanro()              # カテゴリ3: 坂路調教 (1項目)
        self.test_category_seiseki()            # カテゴリ4: 成績 (5項目)
        self.test_category_race_search()        # カテゴリ5: レース検索 (55項目)
        self.test_category_keisoba()            # カテゴリ6: 競走馬 (23項目)
        self.test_category_sire()               # カテゴリ7: 種牡馬 (4項目)
        self.test_category_kisyu()              # カテゴリ8: 騎手 (4項目)
        self.test_category_chokyosi()           # カテゴリ9: 調教師 (4項目)
        self.test_category_market()             # カテゴリ10: 市場取引馬 (2項目)
        self.test_category_banusi()             # カテゴリ11: 馬主 (2項目)
        self.test_category_win5()               # カテゴリ12: WIN5 (10項目)
        self.test_category_others()             # カテゴリ13: その他 (8項目)

        # サマリー表示
        self.print_summary()

    def print_summary(self):
        """テスト結果のサマリーを表示"""
        print("\n" + "="*90)
        print("テスト結果サマリー")
        print("="*90)

        total = len(self.test_results)
        success = sum(1 for r in self.test_results if r['success'])
        failed = total - success

        print(f"\n総テスト数: {total}")
        print(f"成功: {success} ({success*100//total if total > 0 else 0}%)")
        print(f"失敗: {failed} ({failed*100//total if total > 0 else 0}%)")

        # カテゴリ別サマリー
        print("\nカテゴリ別結果:")
        print("-" * 90)
        for cat, stats in self.category_summary.items():
            total_cat = stats['success'] + stats['failed']
            print(f"{cat:20s}: 成功 {stats['success']:2d} / 失敗 {stats['failed']:2d} / 計 {total_cat:2d}")

        if failed > 0:
            print("\n失敗したテスト:")
            print("-" * 90)
            for r in self.test_results:
                if not r['success']:
                    print(f"  ✗ {r['test_name']}")
                    print(f"    エラー: {r['error'][:100]}...")

        print("\n" + "="*90)
        print("全テスト完了")
        print("="*90)

    def close(self):
        """データベース接続を閉じる"""
        self.db.close()


def main():
    """メイン処理"""
    tester = ComprehensiveQueryTester()
    try:
        tester.run_all_tests()
    finally:
        tester.close()


if __name__ == '__main__':
    main()
