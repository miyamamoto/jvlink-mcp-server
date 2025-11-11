#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""質問リストのテスト実行"""
import sys
import os

# プロジェクトのルートをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from src.jvlink_mcp_server.database.connection import DatabaseConnection

def test_question(db, category, question, query, description=""):
    """質問をテストして結果を表示"""
    print(f"\n{'='*80}")
    print(f"[{category}] {question}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*80}")

    try:
        result = db.execute_safe_query(query)
        rows = len(result)
        print(f"[OK] Success: {rows} records")

        if rows > 0:
            print(f"\nSample results (max 3):")
            print(result.head(3).to_string(index=False))
        else:
            print("Note: No data found")

        return True, None

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False, str(e)

def main():
    """テストを実行"""
    db = DatabaseConnection()
    db.connect()

    results = []
    errors = []

    # A1. 競走馬の基本情報
    success, error = test_question(
        db, "A1", "ソダシの戦績を教えてください",
        """
        SELECT
            ru.idYear || '-' || SUBSTR(ru.idMonthDay, 1, 2) || '-' || SUBSTR(ru.idMonthDay, 3, 2) as date,
            ru.KakuteiJyuni as finish,
            ru.Ninki as popularity,
            r.GradeCD as grade
        FROM NL_SE_RACE_UMA ru
        LEFT JOIN NL_RA_RACE r ON
            ru.idYear = r.idYear AND ru.idMonthDay = r.idMonthDay AND
            ru.idJyoCD = r.idJyoCD AND ru.idKaiji = r.idKaiji AND
            ru.idNichiji = r.idNichiji AND ru.idRaceNum = r.idRaceNum
        WHERE ru.Bamei LIKE '%ソダシ%'
            AND ru.KakuteiJyuni IS NOT NULL
            AND LENGTH(ru.KakuteiJyuni) > 0
        ORDER BY ru.idYear DESC, ru.idMonthDay DESC
        LIMIT 10
        """
    )
    results.append(("A1-ソダシの戦績", success))
    if not success:
        errors.append(("A1-ソダシの戦績", error))

    # A2. 血統情報
    success, error = test_question(
        db, "A2", "エビスオー産駒のリストを教えてください",
        """
        SELECT
            Bamei as horse_name,
            BirthDate as birth_date,
            SexCD as sex
        FROM NL_UM_UMA
        WHERE Ketto3Info1Bamei = 'エビスオー'
        ORDER BY BirthDate DESC
        LIMIT 20
        """
    )
    results.append(("A2-ディープインパクト産駒", success))
    if not success:
        errors.append(("A2-ディープインパクト産駒", error))

    # A3. 騎手情報
    success, error = test_question(
        db, "A3", "ルメール騎手の競馬場別成績を教えてください",
        """
        SELECT
            ru.idJyoCD as track_code,
            COUNT(*) as rides,
            SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
            ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
        FROM NL_SE_RACE_UMA ru
        WHERE ru.KisyuRyakusyo LIKE '%ルメール%'
            AND ru.KakuteiJyuni IS NOT NULL
            AND LENGTH(ru.KakuteiJyuni) > 0
            AND ru.idYear >= '2023'
        GROUP BY ru.idJyoCD
        ORDER BY wins DESC
        LIMIT 10
        """
    )
    results.append(("A3-ルメール騎手競馬場別", success))
    if not success:
        errors.append(("A3-ルメール騎手競馬場別", error))

    # D1. 人気・オッズ別傾向
    success, error = test_question(
        db, "D1", "1番人気の勝率をクラス別に教えてください",
        """
        SELECT
            r.GradeCD as grade,
            COUNT(*) as total_races,
            SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
            ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
        FROM NL_SE_RACE_UMA ru
        JOIN NL_RA_RACE r ON
            ru.idYear = r.idYear AND ru.idMonthDay = r.idMonthDay AND
            ru.idJyoCD = r.idJyoCD AND ru.idKaiji = r.idKaiji AND
            ru.idNichiji = r.idNichiji AND ru.idRaceNum = r.idRaceNum
        WHERE ru.Ninki = '01'
            AND ru.KakuteiJyuni IS NOT NULL
            AND LENGTH(ru.KakuteiJyuni) > 0
            AND r.GradeCD IN ('A', 'B', 'C')
            AND ru.idYear >= '2023'
        GROUP BY r.GradeCD
        ORDER BY grade
        """
    )
    results.append(("D1-1番人気の勝率", success))
    if not success:
        errors.append(("D1-1番人気の勝率", error))

    # D2. 枠番・馬番別傾向
    success, error = test_question(
        db, "D2", "東京競馬場芝1600mでの枠順別成績を教えてください",
        """
        SELECT
            ru.Wakuban as frame,
            COUNT(*) as runs,
            SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
            ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
        FROM NL_SE_RACE_UMA ru
        JOIN NL_RA_RACE r ON
            ru.idYear = r.idYear AND ru.idMonthDay = r.idMonthDay AND
            ru.idJyoCD = r.idJyoCD AND ru.idKaiji = r.idKaiji AND
            ru.idNichiji = r.idNichiji AND ru.idRaceNum = r.idRaceNum
        WHERE r.idJyoCD = '05'
            AND r.TrackCD LIKE '1%'
            AND r.Kyori = '1600'
            AND ru.KakuteiJyuni IS NOT NULL
            AND LENGTH(ru.KakuteiJyuni) > 0
            AND ru.Wakuban IS NOT NULL
            AND ru.idYear >= '2022'
        GROUP BY ru.Wakuban
        ORDER BY ru.Wakuban
        """
    )
    results.append(("D2-東京芝1600m枠順別", success))
    if not success:
        errors.append(("D2-東京芝1600m枠順別", error))

    # D5. 血統・種牡馬傾向
    success, error = test_question(
        db, "D5", "エビスオー産駒の芝適性を教えてください",
        """
        SELECT
            CASE
                WHEN r.TrackCD LIKE '1%' THEN 'turf'
                WHEN r.TrackCD LIKE '2%' THEN 'dirt'
                ELSE 'other'
            END as surface,
            COUNT(*) as runs,
            SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) as wins,
            ROUND(CAST(SUM(CASE WHEN ru.KakuteiJyuni = '01' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as win_rate
        FROM NL_SE_RACE_UMA ru
        JOIN NL_RA_RACE r ON
            ru.idYear = r.idYear AND ru.idMonthDay = r.idMonthDay AND
            ru.idJyoCD = r.idJyoCD AND ru.idKaiji = r.idKaiji AND
            ru.idNichiji = r.idNichiji AND ru.idRaceNum = r.idRaceNum
        JOIN NL_UM_UMA u ON ru.KettoNum = u.KettoNum
        WHERE u.Ketto3Info1Bamei = 'エビスオー'
            AND ru.KakuteiJyuni IS NOT NULL
            AND LENGTH(ru.KakuteiJyuni) > 0
            AND ru.idYear >= '2023'
        GROUP BY surface
        ORDER BY surface
        """
    )
    results.append(("D5-エビスオー芝適性", success))
    if not success:
        errors.append(("D5-エビスオー芝適性", error))

    # E1. 馬のランキング
    success, error = test_question(
        db, "E1", "2024年の勝利数ランキングを教えてください",
        """
        SELECT
            ru.Bamei as horse_name,
            COUNT(*) as wins
        FROM NL_SE_RACE_UMA ru
        WHERE ru.KakuteiJyuni = '01'
            AND ru.idYear = '2024'
        GROUP BY ru.Bamei
        ORDER BY wins DESC
        LIMIT 10
        """
    )
    results.append(("E1-2024年勝利数ランキング", success))
    if not success:
        errors.append(("E1-2024年勝利数ランキング", error))

    # サマリー表示
    print(f"\n{'='*80}")
    print("Test Results Summary")
    print(f"{'='*80}")

    success_count = sum(1 for _, s in results if s)
    total_count = len(results)

    print(f"\nTotal tests: {total_count}")
    print(f"Success: {success_count}")
    print(f"Failed: {total_count - success_count}")
    print(f"Success rate: {success_count/total_count*100:.1f}%")

    if errors:
        print(f"\n\n{'='*80}")
        print("Error Details")
        print(f"{'='*80}")
        for test_name, error in errors:
            print(f"\n[{test_name}]")
            print(f"Error: {error}")

    return len(errors) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
