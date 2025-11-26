"""クエリテンプレートの使用例

このスクリプトは、query_templates.pyの使い方を示します。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.jvlink_mcp_server.database.query_templates import (
    render_template,
    list_templates,
    get_template_info,
)


def example_1_favorite_win_rate():
    """例1: 人気別勝率を計算"""
    print("\n=== 例1: 人気別勝率（1番人気、東京競馬場、2020年以降） ===")

    sql = render_template(
        'favorite_win_rate',
        ninki=1,
        venue='東京',
        year_from='2020'
    )

    print(sql)
    print("\n期待される結果: 東京競馬場での1番人気の勝率と連対率")


def example_2_jockey_stats():
    """例2: 騎手成績を集計"""
    print("\n=== 例2: 騎手成績（武豊騎手、2024年、TOP10） ===")

    sql = render_template(
        'jockey_stats',
        jockey_name='武豊',
        year='2024',
        limit=10
    )

    print(sql)
    print("\n期待される結果: 武豊騎手の2024年の成績")


def example_3_frame_stats():
    """例3: 枠番別成績"""
    print("\n=== 例3: 枠番別成績（東京1600m） ===")

    sql = render_template(
        'frame_stats',
        venue='東京',
        kyori='1600'
    )

    print(sql)
    print("\n期待される結果: 東京1600mでの枠番別勝率")


def example_4_race_result():
    """例4: レース結果を取得"""
    print("\n=== 例4: 特定レースの結果（2024年東京11R） ===")

    sql = render_template(
        'race_result',
        year='2024',
        month_day='1028',  # 10月28日
        jyo_cd='05',       # 東京
        kaiji='5',
        nichiji='8',
        race_num='11'
    )

    print(sql)
    print("\n期待される結果: 指定レースの着順、馬名、騎手、オッズなど")


def example_5_grade_race_list():
    """例5: 重賞レース一覧"""
    print("\n=== 例5: G1レース一覧（2024年） ===")

    sql = render_template(
        'grade_race_list',
        grade='G1',
        year='2024',
        limit=20
    )

    print(sql)
    print("\n期待される結果: 2024年のG1レース一覧")


def example_6_horse_pedigree():
    """例6: 馬の血統情報"""
    print("\n=== 例6: 馬の血統情報（ディープインパクト産駒） ===")

    sql = render_template(
        'horse_pedigree',
        horse_name='ディープ'
    )

    print(sql)
    print("\n期待される結果: ディープインパクトを含む馬名の血統情報")


def example_7_sire_stats():
    """例7: 種牡馬別成績"""
    print("\n=== 例7: 種牡馬別成績（ディープインパクト、2024年） ===")

    sql = render_template(
        'sire_stats',
        sire_name='ディープインパクト',
        year='2024',
        limit=10
    )

    print(sql)
    print("\n期待される結果: ディープインパクト産駒の2024年成績")


def example_8_track_condition_stats():
    """例8: 馬場状態別成績"""
    print("\n=== 例8: 馬場状態別成績（イクイノックス） ===")

    sql = render_template(
        'track_condition_stats',
        horse_name='イクイノックス'
    )

    print(sql)
    print("\n期待される結果: イクイノックスのトラック別成績")


def example_9_list_all_templates():
    """例9: すべてのテンプレート一覧"""
    print("\n=== 例9: 利用可能なテンプレート一覧 ===")

    templates = list_templates()

    for i, template in enumerate(templates, 1):
        print(f"\n{i}. {template['name']}")
        print(f"   説明: {template['description']}")
        print("   パラメータ:")
        for param_name, param_info in template['parameters'].items():
            required = "必須" if param_info.get('required', False) else "任意"
            print(f"     - {param_name} ({required}): {param_info['description']}")


def example_10_get_template_detail():
    """例10: 特定テンプレートの詳細情報"""
    print("\n=== 例10: テンプレート詳細情報（favorite_win_rate） ===")

    info = get_template_info('favorite_win_rate')

    if info:
        print(f"テンプレート名: {info['name']}")
        print(f"説明: {info['description']}")
        print("\nパラメータ:")
        for param_name, param_info in info['parameters'].items():
            required = "必須" if param_info.get('required', False) else "任意"
            print(f"  - {param_name} ({required}): {param_info['description']}")
        print(f"\nSQLテンプレート:\n{info['sql']}")


def example_11_error_handling():
    """例11: エラーハンドリング"""
    print("\n=== 例11: エラーハンドリング ===")

    # 存在しないテンプレート
    try:
        sql = render_template('non_existent_template')
    except ValueError as e:
        print(f"エラー1: {e}")

    # 必須パラメータ不足
    try:
        sql = render_template('race_result', year='2024')
    except ValueError as e:
        print(f"エラー2: {e}")

    print("\n正しいエラーハンドリングができています")


def main():
    """すべての例を実行"""
    print("=" * 70)
    print("JVLink クエリテンプレート使用例")
    print("=" * 70)

    example_1_favorite_win_rate()
    example_2_jockey_stats()
    example_3_frame_stats()
    example_4_race_result()
    example_5_grade_race_list()
    example_6_horse_pedigree()
    example_7_sire_stats()
    example_8_track_condition_stats()
    example_9_list_all_templates()
    example_10_get_template_detail()
    example_11_error_handling()

    print("\n" + "=" * 70)
    print("すべての例が完了しました")
    print("=" * 70)


if __name__ == "__main__":
    main()
