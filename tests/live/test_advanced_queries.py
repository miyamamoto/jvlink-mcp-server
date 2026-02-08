#!/usr/bin/env python3
"""jvlink-mcp-server 実データクエリテスト第2弾
35パターンの多様なクエリを実行し、PASS/FAILを判定する。
"""
import os, sys, time, traceback
os.environ["DB_PATH"] = "/tmp/keiba.db"
os.environ["DB_TYPE"] = "sqlite"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jvlink_mcp_server.database.connection import DatabaseConnection
from jvlink_mcp_server.database.high_level_api import (
    get_horse_history, get_jockey_stats, get_sire_stats,
    get_favorite_performance, get_frame_stats,
    get_nar_horse_history, get_nar_jockey_stats, get_nar_favorite_performance,
)
from jvlink_mcp_server.database.query_templates import render_template, list_templates
import pandas as pd

results = []

def test(name, fn):
    """テスト実行ヘルパー"""
    t0 = time.time()
    try:
        val = fn()
        elapsed = time.time() - t0
        results.append({"name": name, "status": "PASS", "time": elapsed, "detail": val})
        print(f"  ✅ PASS [{elapsed:.2f}s] {name}")
        if val: print(f"     → {str(val)[:200]}")
    except Exception as e:
        elapsed = time.time() - t0
        results.append({"name": name, "status": "FAIL", "time": elapsed, "detail": str(e)})
        print(f"  ❌ FAIL [{elapsed:.2f}s] {name}: {e}")
        traceback.print_exc()

db = DatabaseConnection()
db.connect()

print("=" * 70)
print("A. 年代別・時期別クエリ")
print("=" * 70)

# 1. 古いデータ（2000年代）
def t1():
    df = db.execute_safe_query("SELECT COUNT(*) as cnt FROM NL_SE WHERE Year BETWEEN 2000 AND 2005")
    cnt = int(df.iloc[0]['cnt'])
    assert cnt > 0, "2000-2005年のデータなし"
    return f"2000-2005年: {cnt}件"
test("A1: 2000年代レース結果", t1)

# 2. 最新データ（2025-2026年）
def t2():
    df = db.execute_safe_query("SELECT Year, COUNT(*) as cnt FROM NL_SE WHERE Year >= 2025 GROUP BY Year ORDER BY Year")
    if df.empty: return "2025年以降データなし（正常）"
    return df.to_dict('records')
test("A2: 2025-2026年レース結果", t2)

# 3. 特定開催（有馬記念2024）
def t3():
    df = db.execute_safe_query("""
        SELECT r.Year, r.MonthDay, r.Hondai, r.Kyori, s.KakuteiJyuni, s.Bamei, s.KisyuRyakusyo
        FROM NL_RA r JOIN NL_SE s
        ON r.Year=s.Year AND r.MonthDay=s.MonthDay AND r.JyoCD=s.JyoCD
        AND r.Kaiji=s.Kaiji AND r.Nichiji=s.Nichiji AND r.RaceNum=s.RaceNum
        WHERE r.Year=2024 AND r.Hondai LIKE '%有馬記念%'
        ORDER BY s.KakuteiJyuni LIMIT 5
    """)
    if df.empty: return "有馬記念2024 データなし"
    return f"1着: {df.iloc[0]['Bamei']} ({df.iloc[0]['KisyuRyakusyo']}), {len(df)}頭表示"
test("A3: 有馬記念2024", t3)

# 3b. ダービー2024
def t3b():
    df = db.execute_safe_query("""
        SELECT r.Year, r.Hondai, s.KakuteiJyuni, s.Bamei, s.KisyuRyakusyo
        FROM NL_RA r JOIN NL_SE s
        ON r.Year=s.Year AND r.MonthDay=s.MonthDay AND r.JyoCD=s.JyoCD
        AND r.Kaiji=s.Kaiji AND r.Nichiji=s.Nichiji AND r.RaceNum=s.RaceNum
        WHERE r.Year=2024 AND r.Hondai LIKE '%ダービー%' AND r.GradeCD='A'
        ORDER BY s.KakuteiJyuni LIMIT 5
    """)
    if df.empty: return "ダービー2024 データなし"
    return f"1着: {df.iloc[0]['Bamei']}"
test("A3b: ダービー2024", t3b)

# 4. 年をまたぐ期間
def t4():
    df = db.execute_safe_query("""
        SELECT Year, COUNT(*) as cnt FROM NL_SE
        WHERE (Year=2023 AND MonthDay>=1201) OR (Year=2024 AND MonthDay<=0131)
        GROUP BY Year
    """)
    return df.to_dict('records')
test("A4: 年をまたぐ期間(2023/12-2024/01)", t4)

print("\n" + "=" * 70)
print("B. 様々な馬の検索")
print("=" * 70)

# 5. 現役馬
for name in ['ドウデュース', 'リバティアイランド', 'イクイノックス']:
    def t5(n=name):
        df = get_horse_history(db, n)
        if df.empty: return f"{n}: データなし"
        return f"{n}: {len(df)}戦, 最新={df.iloc[0]['race_date']}, 着順={df.iloc[0]['finish']}"
    test(f"B5: 現役馬 {name}", t5)

# 6. 歴史的名馬
for name in ['オグリキャップ', 'ナリタブライアン', 'ディープインパクト']:
    def t6(n=name):
        df = get_horse_history(db, n)
        if df.empty: return f"{n}: データなし（古すぎる可能性）"
        return f"{n}: {len(df)}戦"
    test(f"B6: 歴史的名馬 {name}", t6)

# 7. 地方馬（NARテーブル）
def t7():
    df = db.execute_safe_query("SELECT COUNT(*) as cnt FROM NL_SE_NAR")
    cnt = int(df.iloc[0]['cnt'])
    return f"NL_SE_NAR: {cnt}件"
test("B7: NARデータ件数", t7)

# 8. 短い/長い名前の馬
def t8():
    df = db.execute_safe_query("""
        SELECT Bamei, LENGTH(Bamei) as namelen FROM NL_UM
        ORDER BY LENGTH(Bamei) DESC LIMIT 5
    """)
    longest = df.iloc[0]['Bamei'] if not df.empty else "N/A"
    df2 = db.execute_safe_query("""
        SELECT Bamei, LENGTH(Bamei) as namelen FROM NL_UM
        WHERE Bamei IS NOT NULL AND LENGTH(Bamei) > 0
        ORDER BY LENGTH(Bamei) ASC LIMIT 5
    """)
    shortest = df2.iloc[0]['Bamei'] if not df2.empty else "N/A"
    return f"最長: {longest}, 最短: {shortest}"
test("B8: 短い/長い馬名", t8)

# 9. 同名馬
def t9():
    df = db.execute_safe_query("""
        SELECT Bamei, COUNT(*) as cnt FROM NL_UM
        GROUP BY Bamei HAVING COUNT(*) > 1
        ORDER BY cnt DESC LIMIT 5
    """)
    if df.empty: return "同名馬なし"
    return df.to_dict('records')
test("B9: 同名馬", t9)

print("\n" + "=" * 70)
print("C. 騎手・調教師")
print("=" * 70)

# 10. 武豊
def t10():
    r = get_jockey_stats(db, '武豊')
    return f"{r['jockey_name']}: {r['total_rides']}騎乗, 勝率{r['win_rate']:.1f}%"
test("C10: 武豊の全成績", t10)

# 11. 外国人騎手
for name in ['ムーア', 'デムーロ']:
    def t11(n=name):
        r = get_jockey_stats(db, n)
        return f"{r['jockey_name']}: {r['total_rides']}騎乗, 勝率{r['win_rate']:.1f}%"
    test(f"C11: 外国人騎手 {name}", t11)

# 12. 新人騎手（勝利数少ない）
def t12():
    df = db.execute_safe_query("""
        SELECT KisyuRyakusyo, COUNT(*) as rides,
            SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END) as wins
        FROM NL_SE WHERE KakuteiJyuni IS NOT NULL AND KakuteiJyuni > 0
        GROUP BY KisyuRyakusyo HAVING wins BETWEEN 1 AND 5
        ORDER BY rides DESC LIMIT 5
    """)
    return df.to_dict('records')
test("C12: 新人騎手（1-5勝）", t12)

# 13. リーディングトレーナー
def t13():
    df = db.execute_safe_query("""
        SELECT ChokyosiRyakusyo, COUNT(*) as cnt FROM NL_CH
        WHERE ChokyosiRyakusyo LIKE '%矢作%' OR ChokyosiRyakusyo LIKE '%国枝%'
        GROUP BY ChokyosiRyakusyo
    """)
    return df.to_dict('records') if not df.empty else "調教師マスタに該当なし"
test("C13: 調教師マスタ検索", t13)

print("\n" + "=" * 70)
print("D. 統計・集計クエリ")
print("=" * 70)

# 14. 競馬場別勝率ランキング（騎手）
def t14():
    df = db.execute_safe_query("""
        SELECT JyoCD, KisyuRyakusyo,
            COUNT(*) as rides,
            SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END) as wins,
            ROUND(100.0*SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END)/COUNT(*),1) as win_rate
        FROM NL_SE WHERE KakuteiJyuni IS NOT NULL AND KakuteiJyuni > 0
            AND Year >= 2023
        GROUP BY JyoCD, KisyuRyakusyo
        HAVING rides >= 50
        ORDER BY win_rate DESC LIMIT 10
    """)
    return f"{len(df)}件, top: {df.iloc[0].to_dict()}" if not df.empty else "データなし"
test("D14: 競馬場別騎手勝率ランキング", t14)

# 15. 距離別成績（ドウデュース）
def t15():
    df = db.execute_safe_query("""
        SELECT r.Kyori, COUNT(*) as runs,
            SUM(CASE WHEN s.KakuteiJyuni=1 THEN 1 ELSE 0 END) as wins
        FROM NL_SE s JOIN NL_RA r
        ON s.Year=r.Year AND s.MonthDay=r.MonthDay AND s.JyoCD=r.JyoCD
        AND s.Kaiji=r.Kaiji AND s.Nichiji=r.Nichiji AND s.RaceNum=r.RaceNum
        WHERE s.Bamei LIKE '%ドウデュース%' AND s.KakuteiJyuni > 0
        GROUP BY r.Kyori ORDER BY r.Kyori
    """)
    return df.to_dict('records') if not df.empty else "データなし"
test("D15: ドウデュース距離別成績", t15)

# 16. 馬場状態別成績
def t16():
    df = db.execute_safe_query("""
        SELECT
            CASE r.SibaBabaCD WHEN 1 THEN '良' WHEN 2 THEN '稍重' WHEN 3 THEN '重' WHEN 4 THEN '不良' ELSE 'その他' END as baba,
            COUNT(*) as runs,
            ROUND(100.0*SUM(CASE WHEN s.KakuteiJyuni=1 THEN 1 ELSE 0 END)/COUNT(*),1) as fav_win_rate
        FROM NL_SE s JOIN NL_RA r
        ON s.Year=r.Year AND s.MonthDay=r.MonthDay AND s.JyoCD=r.JyoCD
        AND s.Kaiji=r.Kaiji AND s.Nichiji=r.Nichiji AND s.RaceNum=r.RaceNum
        WHERE s.Ninki=1 AND s.KakuteiJyuni > 0 AND r.SibaBabaCD BETWEEN 1 AND 4
        GROUP BY r.SibaBabaCD ORDER BY r.SibaBabaCD
    """)
    return df.to_dict('records')
test("D16: 馬場状態別1番人気勝率", t16)

# 17. 月別レース数推移
def t17():
    df = db.execute_safe_query("""
        SELECT Year, CAST(MonthDay/100 AS INTEGER) as month, COUNT(DISTINCT Year||MonthDay||JyoCD||RaceNum) as races
        FROM NL_RA WHERE Year >= 2023
        GROUP BY Year, month ORDER BY Year, month
    """)
    return f"{len(df)}行"
test("D17: 月別レース数(2023-)", t17)

# 18. 賞金ランキング（年間トップ10）- NL_SEにHonsyokinがあるか確認
def t18():
    # まずカラム確認
    schema = db.get_table_schema('NL_SE')
    cols = schema['column_name'].tolist()
    if 'Honsyokin' in cols:
        df = db.execute_safe_query("""
            SELECT Bamei, SUM(Honsyokin) as total_prize FROM NL_SE
            WHERE Year=2024 AND Honsyokin > 0
            GROUP BY Bamei ORDER BY total_prize DESC LIMIT 10
        """)
        return df.to_dict('records') if not df.empty else "データなし"
    else:
        # 代替: KyosoPrize等を探す
        prize_cols = [c for c in cols if 'prize' in c.lower() or 'syokin' in c.lower() or 'kin' in c.lower()]
        return f"Honsyokinなし。関連カラム: {prize_cols}"
test("D18: 賞金ランキング2024", t18)

print("\n" + "=" * 70)
print("E. オッズ・払戻関連")
print("=" * 70)

# 19. 高額払戻
def t19():
    schema = db.get_table_schema('NL_HR')
    cols = schema['column_name'].tolist()
    # 払戻テーブルのカラム構造を確認
    return f"NL_HRカラム: {cols[:20]}"
test("E19: 払戻テーブル構造確認", t19)

# 19b. 実際に高額払戻検索
def t19b():
    # まずサンプルデータを取得
    df = db.execute_safe_query("SELECT * FROM NL_HR LIMIT 3")
    if df.empty: return "NL_HR空"
    cols = df.columns.tolist()
    # 払戻金額っぽいカラムを探す
    pay_cols = [c for c in cols if 'Pay' in c or 'Haraimodosi' in c or 'pay' in c.lower()]
    return f"カラム: {cols[:15]}..., 払戻系: {pay_cols}"
test("E19b: 払戻データサンプル", t19b)

# 20. 万馬券の出現頻度 - Oddsから
def t20():
    df = db.execute_safe_query("""
        SELECT Year, COUNT(*) as manba_cnt FROM NL_SE
        WHERE KakuteiJyuni=1 AND Odds >= 100.0 AND Year >= 2020
        GROUP BY Year ORDER BY Year
    """)
    return df.to_dict('records') if not df.empty else "データなし"
test("E20: 万馬券(単勝100倍以上)出現数", t20)

# 21. 1番人気連対率推移
def t21():
    r = get_favorite_performance(db, ninki=1, year_from='2015')
    return f"2015年以降: {r['total']}戦, 勝率{r['win_rate']:.1f}%, 連対率{r['place_rate_2']:.1f}%"
test("E21: 1番人気成績(2015-)", t21)

# 21b. 年別推移
def t21b():
    df = db.execute_safe_query("""
        SELECT Year,
            COUNT(*) as total,
            ROUND(100.0*SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END)/COUNT(*),1) as win_rate,
            ROUND(100.0*SUM(CASE WHEN KakuteiJyuni<=2 THEN 1 ELSE 0 END)/COUNT(*),1) as place_rate
        FROM NL_SE WHERE Ninki=1 AND KakuteiJyuni > 0 AND Year >= 2015
        GROUP BY Year ORDER BY Year
    """)
    return df.to_dict('records')
test("E21b: 1番人気年別推移", t21b)

print("\n" + "=" * 70)
print("F. 血統関連")
print("=" * 70)

# 22. 種牡馬産駒一覧
def t22():
    r = get_sire_stats(db, 'ディープインパクト')
    return f"{r['sire_name']}: {r['total_runs']}出走, 勝率{r['win_rate']:.1f}%"
test("F22: ディープインパクト産駒成績", t22)

# 23. 母父別成績
def t23():
    df = db.execute_safe_query("""
        SELECT u.Ketto3InfoBamei5 as bms, COUNT(*) as runs,
            SUM(CASE WHEN s.KakuteiJyuni=1 THEN 1 ELSE 0 END) as wins,
            ROUND(100.0*SUM(CASE WHEN s.KakuteiJyuni=1 THEN 1 ELSE 0 END)/COUNT(*),1) as win_rate
        FROM NL_SE s JOIN NL_UM u ON s.KettoNum=u.KettoNum
        WHERE s.KakuteiJyuni > 0 AND u.Ketto3InfoBamei5 IS NOT NULL
            AND LENGTH(u.Ketto3InfoBamei5) > 0 AND s.Year >= 2023
        GROUP BY u.Ketto3InfoBamei5 HAVING runs >= 50
        ORDER BY wins DESC LIMIT 10
    """)
    return df.to_dict('records') if not df.empty else "データなし"
test("F23: 母父別成績(2023-)", t23)

# 24. 2世代血統探索
def t24():
    df = db.execute_safe_query("""
        SELECT u.Bamei as horse, u.Ketto3InfoBamei1 as sire,
            u2.Ketto3InfoBamei1 as grandsire
        FROM NL_UM u
        LEFT JOIN NL_UM u2 ON u.Ketto3InfoBamei1 = u2.Bamei
        WHERE u.Bamei LIKE '%ドウデュース%'
        LIMIT 5
    """)
    return df.to_dict('records') if not df.empty else "データなし"
test("F24: 2世代血統（ドウデュース）", t24)

print("\n" + "=" * 70)
print("G. 複雑なクエリ")
print("=" * 70)

# 25. 3テーブルJOIN
def t25():
    df = db.execute_safe_query("""
        SELECT s.Bamei, s.KisyuRyakusyo, r.Hondai, r.Kyori, u.Ketto3InfoBamei1 as sire
        FROM NL_SE s
        JOIN NL_RA r ON s.Year=r.Year AND s.MonthDay=r.MonthDay AND s.JyoCD=r.JyoCD
            AND s.Kaiji=r.Kaiji AND s.Nichiji=r.Nichiji AND s.RaceNum=r.RaceNum
        JOIN NL_UM u ON s.KettoNum=u.KettoNum
        WHERE s.KakuteiJyuni=1 AND r.GradeCD='A' AND s.Year=2024
        ORDER BY r.MonthDay LIMIT 10
    """)
    return f"{len(df)}件, 例: {df.iloc[0].to_dict()}" if not df.empty else "データなし"
test("G25: 3テーブルJOIN(G1勝ち馬+血統)", t25)

# 26. サブクエリ
def t26():
    df = db.execute_safe_query("""
        SELECT Bamei, total_wins FROM (
            SELECT Bamei, SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END) as total_wins
            FROM NL_SE WHERE KakuteiJyuni > 0 AND Year >= 2023
            GROUP BY Bamei
        ) sub WHERE total_wins >= 5
        ORDER BY total_wins DESC LIMIT 10
    """)
    return df.to_dict('records')
test("G26: サブクエリ（多勝馬）", t26)

# 27. HAVING句
def t27():
    df = db.execute_safe_query("""
        SELECT KisyuRyakusyo, COUNT(*) as rides,
            SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END) as wins
        FROM NL_SE WHERE KakuteiJyuni > 0 AND Year=2024
        GROUP BY KisyuRyakusyo
        HAVING wins >= 30
        ORDER BY wins DESC
    """)
    return df.to_dict('records')
test("G27: HAVING句（30勝以上騎手）", t27)

# 28. CASE文
def t28():
    df = db.execute_safe_query("""
        SELECT
            CASE
                WHEN Odds < 2.0 THEN '1倍台'
                WHEN Odds < 5.0 THEN '2-4倍台'
                WHEN Odds < 10.0 THEN '5-9倍台'
                WHEN Odds < 100.0 THEN '10-99倍台'
                ELSE '100倍以上'
            END as odds_range,
            COUNT(*) as cnt,
            ROUND(100.0*SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END)/COUNT(*),1) as win_rate
        FROM NL_SE WHERE KakuteiJyuni > 0 AND Odds > 0 AND Year >= 2020
        GROUP BY odds_range ORDER BY MIN(Odds)
    """)
    return df.to_dict('records')
test("G28: CASE文（オッズ帯別勝率）", t28)

# 29. ウィンドウ関数
def t29():
    df = db.execute_safe_query("""
        SELECT * FROM (
            SELECT KisyuRyakusyo,
                SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END) as wins,
                RANK() OVER (ORDER BY SUM(CASE WHEN KakuteiJyuni=1 THEN 1 ELSE 0 END) DESC) as rnk
            FROM NL_SE WHERE KakuteiJyuni > 0 AND Year=2024
            GROUP BY KisyuRyakusyo
        ) WHERE rnk <= 10
    """)
    return df.to_dict('records')
test("G29: ウィンドウ関数（RANK）", t29)

# 30. UNION
def t30():
    df = db.execute_safe_query("""
        SELECT 'JRA' as source, COUNT(*) as cnt FROM NL_SE WHERE Year=2024
        UNION ALL
        SELECT 'NAR' as source, COUNT(*) as cnt FROM NL_SE_NAR WHERE Year=2024
    """)
    return df.to_dict('records')
test("G30: UNION (JRA+NAR)", t30)

print("\n" + "=" * 70)
print("H. 境界値・ストレス")
print("=" * 70)

# 31. 全テーブル一覧
def t31():
    tables = db.get_tables()
    return f"{len(tables)}テーブル: {tables[:10]}..."
test("H31: 全テーブル一覧", t31)

# 32. 巨大テーブルLIMITなし → num_rowsキャップ
def t32():
    df = db.execute_safe_query("SELECT COUNT(*) as cnt FROM NL_SE")
    cnt = int(df.iloc[0]['cnt'])
    # LIMITなしで取得試行（execute_safe_queryにキャップがあるか確認）
    t0 = time.time()
    df2 = db.execute_safe_query("SELECT Year, JyoCD FROM NL_SE LIMIT 1000")
    elapsed = time.time() - t0
    return f"NL_SE: {cnt}行, LIMIT 1000取得: {elapsed:.2f}s, shape={df2.shape}"
test("H32: NL_SE行数 + LIMIT取得", t32)

# 33. WHERE句なし大量データ
def t33():
    t0 = time.time()
    df = db.execute_safe_query("SELECT Year, COUNT(*) as cnt FROM NL_SE GROUP BY Year ORDER BY Year")
    return f"{len(df)}年分, 合計={df['cnt'].sum()}, {time.time()-t0:.2f}s"
test("H33: WHERE句なし年別集計", t33)

# 34. NULL値カラム集計
def t34():
    df = db.execute_safe_query("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN Odds IS NULL THEN 1 ELSE 0 END) as null_odds,
            SUM(CASE WHEN Time IS NULL THEN 1 ELSE 0 END) as null_time,
            SUM(CASE WHEN HaronTimeL3 IS NULL THEN 1 ELSE 0 END) as null_l3
        FROM NL_SE
    """)
    return df.iloc[0].to_dict()
test("H34: NULL値カラム集計", t34)

# 35. 空のNARテーブル
def t35():
    nar_tables = ['NL_SE_NAR', 'NL_RA_NAR']
    info = {}
    for t in nar_tables:
        try:
            df = db.execute_safe_query(f"SELECT COUNT(*) as cnt FROM {t}")
            info[t] = int(df.iloc[0]['cnt'])
        except Exception as e:
            info[t] = f"ERROR: {e}"
    return info
test("H35: NARテーブル件数", t35)

# ============================================================
# サマリ
# ============================================================
print("\n" + "=" * 70)
print("サマリ")
print("=" * 70)

pass_cnt = sum(1 for r in results if r['status'] == 'PASS')
fail_cnt = sum(1 for r in results if r['status'] == 'FAIL')
total = len(results)
print(f"\n合計: {total}テスト, ✅ PASS: {pass_cnt}, ❌ FAIL: {fail_cnt}")

if fail_cnt > 0:
    print("\n--- FAIL詳細 ---")
    for r in results:
        if r['status'] == 'FAIL':
            print(f"  ❌ {r['name']}: {r['detail']}")

slow = [r for r in results if r['time'] > 5.0]
if slow:
    print("\n--- 遅いクエリ (>5s) ---")
    for r in sorted(slow, key=lambda x: -x['time']):
        print(f"  ⏱️ {r['name']}: {r['time']:.2f}s")

db.close()
