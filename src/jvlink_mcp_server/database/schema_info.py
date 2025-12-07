"""JVLinkデータベースのスキーマ情報（jrvltsql版）

重要: jrvltsql v2.0以降では適切な型が使用されています。
- INTEGER: 着順、人気、馬番、枠番、年、距離など
- REAL: オッズ、タイム、馬体重など
- TEXT: コード、名前など

テーブルプレフィックス:
- NL_: 蓄積系（確定データ）
- RT_: 速報系（当日データ）
- TS_: 時系列オッズ
"""

# === 蓄積系テーブル (NL_) ===
JVLINK_TABLES = {
    # レース・出走情報
    "NL_RA": {
        "description": "レース情報テーブル（確定）",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
        "key_columns": {
            "Year": "開催年 (INTEGER)",
            "MonthDay": "開催月日 (INTEGER, 例: 1225)",
            "JyoCD": "競馬場コード (TEXT, 01-10)",
            "Hondai": "レース名本題",
            "GradeCD": "グレードコード (A=G1, B=G2, C=G3)",
            "Kyori": "距離（INTEGER, メートル）",
            "TrackCD": "トラックコード（2桁: 1桁目=種別[1=芝,2=ダート], 2桁目=回り）",
            "SibaBabaCD": "芝馬場状態コード (1=良, 2=稍重, 3=重, 4=不良)",
            "DirtBabaCD": "ダート馬場状態コード",
        },
    },
    "NL_SE": {
        "description": "出馬表・レース結果テーブル（確定）。血統情報はNL_UMとKettoNumでJOINして取得",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
        "key_columns": {
            "KettoNum": "血統登録番号（NL_UMとJOINするためのキー）",
            "Umaban": "馬番 (INTEGER, 1-18)",
            "Wakuban": "枠番 (INTEGER, 1-8)",
            "Bamei": "馬名",
            "KisyuRyakusyo": "騎手名略称",
            "KakuteiJyuni": "確定着順 (INTEGER, 1=1着, 2=2着...)",
            "Ninki": "人気 (INTEGER, 1=1番人気, 2=2番人気...)",
            "Odds": "単勝オッズ (REAL)",
            "Time": "走破タイム (REAL, 秒)",
            "HaronTimeL3": "上がり3F (REAL, 秒)",
            "BaTaijyu": "馬体重 (REAL, kg)",
            "Futan": "斤量 (REAL, kg)",
            "Barei": "馬齢 (INTEGER)",
            "SexCD": "性別コード (1=牡, 2=牝, 3=セン)",
        },
    },
    "NL_TK": {
        "description": "特別登録馬テーブル - 特別レースへの登録馬情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"],
        "key_columns": {
            "KettoNum": "血統登録番号",
            "Bamei": "馬名",
            "Futan": "斤量 (REAL)",
        },
    },
    "NL_HR": {"description": "払戻テーブル（確定）", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"], "key_columns": {}},
    # 馬・騎手・調教師マスタ
    "NL_UM": {
        "description": "馬マスタ（JRA中央競馬のみ。地方競馬はJOIN不可）",
        "primary_keys": ["KettoNum"],
        "key_columns": {
            "Bamei": "馬名",
            "Ketto3InfoBamei1": "父馬名",
            "Ketto3InfoBamei2": "母馬名",
            "Ketto3InfoBamei5": "母父馬名",
        },
    },
    "NL_KS": {"description": "騎手マスタ", "primary_keys": ["KisyuCode"], "key_columns": {"KisyuName": "騎手名", "KisyuRyakusyo": "騎手名略称"}},
    "NL_CH": {"description": "調教師マスタ", "primary_keys": ["ChokyosiCode"], "key_columns": {"ChokyosiName": "調教師名", "ChokyosiRyakusyo": "調教師名略称"}},
    "NL_BN": {"description": "馬主マスタ", "primary_keys": ["BanusiCode"], "key_columns": {"BanusiName": "馬主名", "Fukusyoku": "服色"}},
    "NL_BR": {"description": "生産者マスタ", "primary_keys": ["BreederCode"], "key_columns": {"BreederName": "生産者名", "Address": "住所"}},
    # 血統・繁殖情報
    "NL_HN": {"description": "繁殖馬マスタ", "primary_keys": ["HansyokuNum"], "key_columns": {"Bamei": "馬名", "FHansyokuNum": "父繁殖番号", "MHansyokuNum": "母繁殖番号"}},
    "NL_SK": {"description": "産駒マスタ", "primary_keys": ["KettoNum"], "key_columns": {"BirthDate": "生年月日", "SexCD": "性別"}},
    "NL_BT": {"description": "系統情報テーブル", "primary_keys": ["HansyokuNum"], "key_columns": {"KeitoName": "系統名"}},
    # 成績・統計情報
    "NL_CK": {
        "description": "競走馬市場取引価格テーブル - 馬の詳細成績・適性情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"],
        "key_columns": {
            "KettoNum": "血統登録番号",
            "Bamei": "馬名",
            "KyakusituKeiko": "脚質傾向",
        },
    },
    "NL_HC": {"description": "調教師本賞金・付加賞金テーブル", "primary_keys": ["ChokyosiCode", "SetYear"], "key_columns": {}},
    "NL_HS": {"description": "馬市場取引価格テーブル", "primary_keys": ["KettoNum"], "key_columns": {"Price": "価格"}},
    "NL_HY": {"description": "抹消馬名テーブル", "primary_keys": [], "key_columns": {"Bamei": "馬名"}},
    # オッズ・票数テーブル
    "NL_O1": {"description": "単勝複勝オッズ（確定）", "primary_keys": [], "key_columns": {}},
    "NL_O2": {"description": "馬連オッズ（確定）", "primary_keys": [], "key_columns": {}},
    "NL_O3": {"description": "ワイドオッズ（確定）", "primary_keys": [], "key_columns": {}},
    "NL_O4": {"description": "馬単オッズ（確定）", "primary_keys": [], "key_columns": {}},
    "NL_O5": {"description": "3連複オッズ（確定）", "primary_keys": [], "key_columns": {}},
    "NL_O6": {"description": "3連単オッズ（確定）", "primary_keys": [], "key_columns": {}},
    "NL_H1": {"description": "単勝複勝票数（確定）", "primary_keys": [], "key_columns": {}},
    "NL_H6": {"description": "3連単票数（確定）", "primary_keys": [], "key_columns": {}},
    # 変更情報
    "NL_JC": {"description": "騎手変更テーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"], "key_columns": {}},
    "NL_CC": {"description": "コース変更テーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"], "key_columns": {}},
    "NL_TC": {"description": "発走時刻変更テーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"], "key_columns": {}},
    "NL_JG": {"description": "出走取消・競走除外テーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"], "key_columns": {}},
    # 天候・馬場情報
    "NL_WE": {"description": "天候馬場状態テーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji"], "key_columns": {}},
    "NL_WH": {"description": "天候馬場変更テーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji"], "key_columns": {}},
    # 調教・その他
    "NL_WC": {"description": "調教タイムテーブル", "primary_keys": ["KettoNum", "ChokyoDate"], "key_columns": {"Course": "コース", "HaronTime3Total": "3ハロンタイム"}},
    "NL_DM": {"description": "デジタルメモテーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"], "key_columns": {}},
    "NL_TM": {"description": "タイムマスタテーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"], "key_columns": {"TMScore": "タイムスコア"}},
    "NL_CS": {"description": "コース情報マスタ", "primary_keys": ["JyoCD", "Kyori", "TrackCD"], "key_columns": {}},
    "NL_RC": {"description": "レコードタイムテーブル", "primary_keys": [], "key_columns": {"RecTime": "レコードタイム"}},
    "NL_YS": {"description": "開催スケジュールテーブル", "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji"], "key_columns": {}},
    "NL_WF": {"description": "WIN5情報テーブル", "primary_keys": ["Year", "MonthDay"], "key_columns": {}},
    "NL_AV": {"description": "セリ市情報テーブル", "primary_keys": ["KettoNum"], "key_columns": {"Price": "価格"}},
}

# === 速報系テーブル (RT_) ===
REALTIME_TABLES = {
    "RT_RA": {
        "description": "レース情報テーブル（速報）- 当日のレース情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
        "key_columns": {
            "Year": "開催年 (INTEGER)",
            "MonthDay": "開催月日 (INTEGER)",
            "JyoCD": "競馬場コード (TEXT)",
            "Hondai": "レース名本題",
            "Kyori": "距離（INTEGER, メートル）",
        },
    },
    "RT_SE": {
        "description": "出馬表・レース結果テーブル（速報）- 当日の出走馬情報・結果",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
        "key_columns": {
            "Umaban": "馬番 (INTEGER)",
            "Bamei": "馬名",
            "KisyuRyakusyo": "騎手名略称",
            "KakuteiJyuni": "確定着順 (INTEGER)",
            "Ninki": "人気 (INTEGER)",
            "Odds": "単勝オッズ (REAL)",
        },
    },
    "RT_HR": {"description": "払戻テーブル（速報）", "primary_keys": [], "key_columns": {}},
    "RT_O1": {"description": "単勝複勝オッズ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_O2": {"description": "馬連オッズ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_O3": {"description": "ワイドオッズ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_O4": {"description": "馬単オッズ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_O5": {"description": "3連複オッズ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_O6": {"description": "3連単オッズ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_H1": {"description": "単勝複勝票数（速報）", "primary_keys": [], "key_columns": {}},
    "RT_H6": {"description": "3連単票数（速報）", "primary_keys": [], "key_columns": {}},
    # 変更情報（速報）
    "RT_AV": {"description": "セリ市情報（速報）", "primary_keys": [], "key_columns": {}},
    "RT_CC": {"description": "コース変更（速報）", "primary_keys": [], "key_columns": {}},
    "RT_DM": {"description": "デジタルメモ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_JC": {"description": "騎手変更（速報）", "primary_keys": [], "key_columns": {}},
    "RT_TC": {"description": "発走時刻変更（速報）", "primary_keys": [], "key_columns": {}},
    "RT_RC": {"description": "レコードタイム（速報）", "primary_keys": [], "key_columns": {}},
    "RT_TM": {"description": "タイムマスタ（速報）", "primary_keys": [], "key_columns": {}},
    "RT_WE": {"description": "天候馬場状態（速報）", "primary_keys": [], "key_columns": {}},
    "RT_WH": {"description": "天候馬場変更（速報）", "primary_keys": [], "key_columns": {}},
}

# === 時系列オッズテーブル (TS_) ===
TIMESERIES_TABLES = {
    "TS_O1": {
        "description": "時系列単勝複勝オッズ - オッズの時間推移を記録",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "HassoTime", "Umaban"],
        "key_columns": {
            "HassoTime": "発走時刻",
            "Umaban": "馬番 (INTEGER)",
            "TanOdds": "単勝オッズ (REAL)",
            "TanNinki": "単勝人気 (INTEGER)",
            "FukuOddsLow": "複勝オッズ下限 (REAL)",
            "FukuOddsHigh": "複勝オッズ上限 (REAL)",
            "TanVote": "単勝票数 (INTEGER)",
            "FukuVote": "複勝票数 (INTEGER)",
        },
    },
    "TS_O2": {"description": "時系列馬連オッズ", "primary_keys": [], "key_columns": {}},
    "TS_O3": {"description": "時系列ワイドオッズ", "primary_keys": [], "key_columns": {}},
    "TS_O4": {"description": "時系列馬単オッズ", "primary_keys": [], "key_columns": {}},
    "TS_O5": {"description": "時系列3連複オッズ", "primary_keys": [], "key_columns": {}},
    "TS_O6": {"description": "時系列3連単オッズ", "primary_keys": [], "key_columns": {}},
}

# 全テーブルを統合
ALL_TABLES = {**JVLINK_TABLES, **REALTIME_TABLES, **TIMESERIES_TABLES}

TRACK_CODES = {"01": "札幌", "02": "函館", "03": "福島", "04": "新潟", "05": "東京", "06": "中山", "07": "中京", "08": "京都", "09": "阪神", "10": "小倉"}
GRADE_CODES = {"A": "GI", "B": "GII", "C": "GIII", "D": "リステッド", "E": "オープン特別", "F": "3勝クラス", "G": "2勝クラス", "H": "1勝クラス", "I": "未勝利", "J": "新馬"}
TRACK_CONDITION_CODES = {"1": "良", "2": "稍重", "3": "重", "4": "不良"}
TRACK_TYPE_CODES = {"1": "芝", "2": "ダート", "5": "障害"}
SEX_CODES = {"1": "牡", "2": "牝", "3": "セン"}


def get_schema_description():
    return {
        "tables": ALL_TABLES,
        "track_codes": TRACK_CODES,
        "grade_codes": GRADE_CODES,
        "important_notes": [
            "NL_: 蓄積系（確定データ）、RT_: 速報系（当日データ）、TS_: 時系列オッズ",
            "KakuteiJyuni(着順)とNinki(人気)はINTEGER型（1, 2, 3...）",
            "Umaban(馬番)とWakuban(枠番)もINTEGER型",
            "JyoCD(競馬場)はTEXT型でゼロパディング（'05'=東京）",
            "Odds, Time, HaronTimeL3, BaTaijyuはREAL型",
            "地方競馬はNL_UMとJOIN不可",
            "速報系(RT_)は当日のみ、過去データはNL_を使用",
        ],
    }


def get_query_examples():
    return {
        "1番人気勝率": "SELECT COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE Ninki = 1 AND KakuteiJyuni IS NOT NULL",
        "騎手成績": "SELECT KisyuRyakusyo, COUNT(*) as rides, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE KakuteiJyuni IS NOT NULL GROUP BY KisyuRyakusyo ORDER BY wins DESC LIMIT 20",
        "東京1番人気": "SELECT COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE JyoCD = '05' AND Ninki = 1 AND KakuteiJyuni IS NOT NULL",
        "枠番別成績": "SELECT Wakuban, COUNT(*) as total, SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE WHERE KakuteiJyuni IS NOT NULL GROUP BY Wakuban ORDER BY Wakuban",
        "種牡馬成績": "SELECT u.Ketto3InfoBamei1 as sire, COUNT(*) as runs, SUM(CASE WHEN s.KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins FROM NL_SE s JOIN NL_UM u ON s.KettoNum = u.KettoNum WHERE s.KakuteiJyuni IS NOT NULL GROUP BY u.Ketto3InfoBamei1 HAVING COUNT(*) >= 100 ORDER BY wins DESC LIMIT 20",
        "当日オッズ推移": "SELECT HassoTime, Umaban, TanOdds, TanNinki FROM TS_O1 WHERE Year = 2024 AND MonthDay = 1222 AND JyoCD = '06' AND RaceNum = 11 ORDER BY HassoTime, Umaban",
    }


def get_target_equivalent_query_examples():
    return get_query_examples()
