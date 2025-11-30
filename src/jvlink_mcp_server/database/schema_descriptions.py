"""JVLink Database Schema Descriptions (jrvltsql版)

カラムごとの詳細な説明を提供します。
LLMがより正確にクエリを生成できるようにするための情報です。
"""

from .schema_auto_descriptions import generate_column_description as auto_generate

# テーブルの説明
TABLE_DESCRIPTIONS = {
    "NL_RA": {
        "description": "レース情報テーブル - 各レースの基本情報、条件、グレード等",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_SE": {
        "description": "出馬表テーブル - レース出走馬情報、結果、オッズ、枠番等",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_UM": {
        "description": "馬マスタテーブル - 馬の基本情報、血統情報、生産者等。NL_SE.KettoNumでJOIN可能（JRA中央競馬のみ。地方競馬はマッチしない）",
        "primary_keys": ["KettoNum"],
    },
    "NL_KS": {
        "description": "騎手マスタテーブル - 騎手の基本情報",
        "primary_keys": ["KisyuCode"],
    },
    "NL_CH": {
        "description": "調教師マスタテーブル - 調教師の基本情報",
        "primary_keys": ["ChokyosiCode"],
    },
    "NL_HR": {
        "description": "払戻テーブル - レースの払戻情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_O1": {
        "description": "単勝・複勝オッズテーブル",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_WE": {
        "description": "馬場状態テーブル - 現在未対応（テーブルは存在するがデータが空。JVLinkの0B11/0B14/0B16 SPECが必要）",
        "primary_keys": [],
    },
}

# カラムの説明（主要カラムのみ）
COLUMN_DESCRIPTIONS = {
    # === NL_RA (レース情報) ===
    "NL_RA": {
        "Year": "開催年（YYYY形式）",
        "MonthDay": "開催月日（MMDD形式）",
        "JyoCD": "競馬場コード（01=札幌, 02=函館, 03=福島, 04=新潟, 05=東京, 06=中山, 07=中京, 08=京都, 09=阪神, 10=小倉）",
        "Kaiji": "開催回次（第何回開催か）",
        "Nichiji": "開催日次（何日目か）",
        "RaceNum": "レース番号（1-12）",
        "Hondai": "レース正式名称（例：日本ダービー）",
        "Fukudai": "レース副題",
        "Kakko": "レースカッコ内表記",
        "GradeCD": "グレードコード（A=G1, B=G2, C=G3, D=リステッド, etc.）",
        "SyubetuCD": "競走種別コード（11=芝, 21=ダート, 23=障害芝, 24=障害ダート）",
        "KigoCD": "競走記号コード",
        "JyuryoCD": "重量種別コード（1=ハンデ, 2=別定, 3=馬齢, 4=定量）",
        "Kyori": "距離（メートル単位、例：1600）",
        "TrackCD": "トラックコード（10=芝・右, 11=芝・左, 18=芝・直, 20=ダート・右, etc.）",
        "HassoTime": "発走時刻（HHmm形式）",
        "TorokuTosu": "登録頭数",
        "SyussoTosu": "出走頭数",
    },
    # === NL_SE (出馬表) ===
    "NL_SE": {
        "Umaban": "馬番 (INTEGER, 1-18)",
        "Wakuban": "枠番 (INTEGER, 1-8)",
        "KettoNum": "血統登録番号（馬の一意識別子）",
        "Bamei": "馬名",
        "SexCD": "性別コード（1=牡, 2=牝, 3=セン）",
        "Barei": "馬齢 (INTEGER)",
        "KisyuCode": "騎手コード",
        "KisyuRyakusyo": "騎手名略称",
        "ChokyosiCode": "調教師コード",
        "ChokyosiRyakusyo": "調教師名略称",
        "Futan": "斤量 (REAL, kg)",
        "Ninki": "人気順位 (INTEGER, 1=1番人気, 2=2番人気...)",
        "Odds": "単勝オッズ (REAL)",
        "ZogenFugo": "増減記号（+, -, ±）",
        "ZogenSa": "増減差 (REAL, 馬体重の増減kg)",
        "IJyoCD": "異常区分コード（取消、除外、中止など）",
        "KakuteiJyuni": "確定着順 (INTEGER, 1=1着, 2=2着...)",
        "Time": "走破タイム (REAL, 秒)",
        "ChakusaCD": "着差コード（1=ハナ, 2=クビ, 3=1/2馬身, etc.）",
        "HaronTimeL3": "上がり3Fタイム (REAL, 秒)",
        "HaronTimeL4": "上がり4Fタイム (REAL, 秒)",
        "Jyuni1c": "1コーナー通過順位 (INTEGER)",
        "Jyuni2c": "2コーナー通過順位 (INTEGER)",
        "Jyuni3c": "3コーナー通過順位 (INTEGER)",
        "Jyuni4c": "4コーナー通過順位 (INTEGER)",
        "BaTaijyu": "馬体重 (REAL, kg)",
        "Bamei1": "対戦相手の馬名（1着馬は2着馬、2着以下は1着馬の名前）。父馬名ではない。血統情報はNL_UMを使用",
        "KettoNum1": "対戦相手の血統登録番号（1着馬は2着馬、2着以下は1着馬）。父馬の血統番号ではない",
        "TimeDiff": "タイム差 (REAL, 秒)",
    },
    # === NL_UM (馬マスタ) ===
    "NL_UM": {
        "KettoNum": "血統登録番号（10桁、馬の一意識別子）",
        "Bamei": "馬名（カタカナ）",
        "BameiKana": "馬名カナ",
        "BameiEng": "馬名英字",
        "SexCD": "性別コード（1=牡, 2=牝, 3=セン）",
        "KeiroCD": "毛色コード",
        "BirthDate": "誕生日",
        "SanchiName": "産地名",
        "BreederName": "生産者名",
        "BanusiName": "馬主名",
        "ChokyosiCode": "所属調教師コード",
        "ChokyosiRyakusyo": "調教師略称",
        "Ketto3InfoBamei1": "父馬名",
        "Ketto3InfoBamei2": "母馬名",
        "Ketto3InfoBamei3": "父父馬名",
        "Ketto3InfoBamei4": "父母馬名",
        "Ketto3InfoBamei5": "母父馬名",
        "Ketto3InfoBamei6": "母母馬名",
    },
    # === NL_KS (騎手マスタ) ===
    "NL_KS": {
        "KisyuCode": "騎手コード",
        "KisyuName": "騎手名",
        "KisyuNameKana": "騎手名カナ",
        "KisyuRyakusyo": "騎手名略称",
        "TozaiCD": "東西コード（1=美浦, 2=栗東）",
    },
    # === NL_CH (調教師マスタ) ===
    "NL_CH": {
        "ChokyosiCode": "調教師コード",
        "ChokyosiName": "調教師名",
        "ChokyosiNameKana": "調教師名カナ",
        "ChokyosiRyakusyo": "調教師名略称",
        "TozaiCD": "東西コード（1=美浦, 2=栗東）",
    },
}

# コード値の説明
CODE_MAPPINGS = {
    "競馬場コード": {
        "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
        "05": "東京", "06": "中山", "07": "中京", "08": "京都",
        "09": "阪神", "10": "小倉",
    },
    "グレードコード": {
        "A": "G1（最高グレード）", "B": "G2", "C": "G3",
        "D": "リステッド競走", "E": "オープン特別",
        "F": "3勝クラス", "G": "2勝クラス", "H": "1勝クラス",
        "I": "未勝利", "J": "新馬",
    },
    "競走種別コード": {
        "11": "芝（平地）", "21": "ダート（平地）",
        "23": "障害・芝", "24": "障害・ダート",
    },
    "馬場状態コード": {
        "1": "良", "2": "稍重", "3": "重", "4": "不良",
    },
    "性別コード": {
        "1": "牡馬", "2": "牝馬", "3": "セン馬",
    },
}

# LLM向けのクエリ生成ヒント
QUERY_GENERATION_HINTS = """
## JVLinkデータベースでのクエリ生成ヒント

### データ型について（重要）

jrvltsql v2.0以降では適切な型が使用されています：
- INTEGER: KakuteiJyuni(着順), Ninki(人気), Umaban(馬番), Wakuban(枠番), Year, Kyori(距離), Barei(馬齢)
- REAL: Odds(オッズ), Time(タイム), HaronTimeL3(上がり3F), BaTaijyu(馬体重), Futan(斤量)
- TEXT: JyoCD(競馬場コード), GradeCD(グレード), Bamei(馬名), KettoNum(血統番号)

クエリ例：
- 1番人気: WHERE Ninki = 1 （文字列ではなく数値）
- 1着: WHERE KakuteiJyuni = 1
- 東京: WHERE JyoCD = '05' （コードは文字列のまま）

### 主要な結合パターン

1. レース情報 + 出馬表: NL_RA JOIN NL_SE ON 6カラム
2. 出馬表 + 馬マスタ: NL_SE JOIN NL_UM ON KettoNum
3. 出馬表 + 騎手マスタ: NL_SE JOIN NL_KS ON KisyuCode

### 重要な制限事項

#### NL_SE.Bamei1/KettoNum1について
- Bamei1: 対戦相手の馬名（1着馬は2着馬、2着以下は1着馬）。父馬名ではない
- KettoNum1: 対戦相手の血統登録番号。父馬の血統番号ではない
- 血統情報は必ずNL_UMテーブルを使用すること

#### 地方競馬のJOIN制限
- NL_SE + NL_UM のJOINはJRA中央競馬のみ100%マッチ
- 地方競馬（JyoCD > 10）はNL_UMにデータがないためJOIN不可
"""


def get_column_description(table_name: str, column_name: str) -> str:
    if table_name in COLUMN_DESCRIPTIONS:
        manual_desc = COLUMN_DESCRIPTIONS[table_name].get(column_name, "")
        if manual_desc:
            return manual_desc
    return auto_generate(table_name, column_name)


def get_table_description(table_name: str) -> dict:
    return TABLE_DESCRIPTIONS.get(table_name, {
        "description": "（説明未登録）",
        "primary_keys": [],
    })