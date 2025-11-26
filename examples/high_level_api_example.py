"""High-level API使用例

このスクリプトは、high_level_api.pyの各関数の使用方法を示します。
"""

import sys
import os

# パスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jvlink_mcp_server.database.connection import DatabaseConnection
from jvlink_mcp_server.database.high_level_api import (
    get_favorite_performance,
    get_jockey_stats,
    get_frame_stats,
    get_horse_history,
    get_sire_stats
)


def main():
    """各関数の使用例を実行"""

    # データベース接続
    # 環境変数を設定するか、.envファイルを使用してください
    db = DatabaseConnection()

    print("=" * 80)
    print("High-level API使用例")
    print("=" * 80)

    # 例1: 人気別成績
    print("\n[例1] 東京競馬場G1での1番人気成績（2020年以降）")
    print("-" * 80)
    try:
        result = get_favorite_performance(
            db,
            venue='東京',
            ninki=1,
            grade='G1',
            year_from='2020'
        )
        print(f"条件: {result['conditions']}")
        print(f"総レース数: {result['total']}")
        print(f"1着回数: {result['wins']}")
        print(f"勝率: {result['win_rate']:.1f}%")
        print(f"連対率: {result['place_rate_2']:.1f}%")
        print(f"複勝率: {result['place_rate_3']:.1f}%")
    except Exception as e:
        print(f"エラー: {e}")

    # 例2: 騎手成績
    print("\n[例2] ルメール騎手の東京競馬場成績（2023年以降）")
    print("-" * 80)
    try:
        result = get_jockey_stats(
            db,
            jockey_name='ルメール',
            venue='東京',
            year_from='2023'
        )
        print(f"条件: {result['conditions']}")
        print(f"騎手名: {result['jockey_name']}")
        print(f"騎乗回数: {result['total_rides']}")
        print(f"勝利数: {result['wins']}")
        print(f"勝率: {result['win_rate']:.1f}%")
        print(f"連対率: {result['place_rate_2']:.1f}%")
        print(f"複勝率: {result['place_rate_3']:.1f}%")
        if 'matched_jockeys' in result:
            print(f"マッチした騎手: {', '.join(result['matched_jockeys'])}")
    except Exception as e:
        print(f"エラー: {e}")

    # 例3: 枠番別成績
    print("\n[例3] 東京競馬場1600mの枠番別成績")
    print("-" * 80)
    try:
        df = get_frame_stats(
            db,
            venue='東京',
            distance=1600
        )
        if not df.empty:
            print(f"条件: {df.attrs.get('conditions', '不明')}")
            print(df.to_string(index=False))
        else:
            print("データが見つかりませんでした")
    except Exception as e:
        print(f"エラー: {e}")

    # 例4: 馬の戦績
    print("\n[例4] ディープインパクトの戦績（2005年以降）")
    print("-" * 80)
    try:
        df = get_horse_history(
            db,
            horse_name='ディープインパクト',
            year_from='2005'
        )
        if not df.empty:
            print(f"戦績数: {len(df)}")
            print(df.head(10).to_string(index=False))
            if len(df) > 10:
                print(f"\n... 他 {len(df) - 10} 件")
        else:
            print("データが見つかりませんでした")
    except Exception as e:
        print(f"エラー: {e}")

    # 例5: 種牡馬成績
    print("\n[例5] ディープインパクト産駒の東京1600m成績（2020年以降）")
    print("-" * 80)
    try:
        result = get_sire_stats(
            db,
            sire_name='ディープインパクト',
            venue='東京',
            distance=1600,
            year_from='2020'
        )
        print(f"条件: {result['conditions']}")
        print(f"種牡馬名: {result['sire_name']}")
        print(f"出走数: {result['total_runs']}")
        print(f"勝利数: {result['wins']}")
        print(f"勝率: {result['win_rate']:.1f}%")
        print(f"連対率: {result['place_rate_2']:.1f}%")
        print(f"複勝率: {result['place_rate_3']:.1f}%")
    except Exception as e:
        print(f"エラー: {e}")

    # データベース接続を閉じる
    db.close()

    print("\n" + "=" * 80)
    print("すべての例の実行が完了しました")
    print("=" * 80)


if __name__ == '__main__':
    main()
