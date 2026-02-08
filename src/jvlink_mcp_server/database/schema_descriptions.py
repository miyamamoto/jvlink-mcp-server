"""JVLink Database Schema Descriptions (jrvltsql版)

カラムごとの詳細な説明を提供します。
LLMがより正確にクエリを生成できるようにするための情報です。
"""

from .schema_auto_descriptions import generate_column_description as auto_generate

# テーブルの説明
# テーブルプレフィックス: NL_=蓄積系（確定）、RT_=速報系（当日）、TS_=時系列オッズ
TABLE_DESCRIPTIONS = {
    # === 蓄積系 (NL_) - レース・出走情報 ===
    "NL_RA": {
        "description": "レース情報テーブル（確定） - 各レースの基本情報、条件、グレード等",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_SE": {
        "description": "出馬表テーブル（確定） - レース出走馬情報、結果、オッズ、枠番等",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_TK": {
        "description": "特別登録馬テーブル - 特別レースへの登録馬情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"],
    },
    "NL_HR": {
        "description": "払戻テーブル（確定） - レースの払戻情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    # === 蓄積系 (NL_) - マスタ情報 ===
    "NL_UM": {
        "description": "馬マスタテーブル - 馬の基本情報、血統情報、生産者等。NL_SE.KettoNumでJOIN可能（JRA中央競馬のみ）",
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
    "NL_BN": {
        "description": "馬主マスタテーブル - 馬主の基本情報、服色",
        "primary_keys": ["BanusiCode"],
    },
    "NL_BR": {
        "description": "生産者マスタテーブル - 生産者の基本情報",
        "primary_keys": ["BreederCode"],
    },
    # === 蓄積系 (NL_) - 血統・繁殖情報 ===
    "NL_HN": {
        "description": "繁殖馬マスタテーブル - 繁殖馬の血統情報",
        "primary_keys": ["HansyokuNum"],
    },
    "NL_SK": {
        "description": "産駒マスタテーブル - 産駒情報",
        "primary_keys": ["KettoNum"],
    },
    "NL_BT": {
        "description": "系統情報テーブル - 血統系統情報",
        "primary_keys": ["HansyokuNum"],
    },
    # === 蓄積系 (NL_) - 成績・統計情報 ===
    "NL_CK": {
        "description": "競走馬成績詳細テーブル - 馬の詳細成績・適性情報（コース別、距離別等）",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"],
    },
    "NL_HC": {
        "description": "調教師賞金テーブル - 調教師の本賞金・付加賞金情報",
        "primary_keys": ["ChokyosiCode", "SetYear"],
    },
    "NL_HS": {
        "description": "馬市場取引価格テーブル - 馬のセリ・取引価格情報",
        "primary_keys": ["KettoNum"],
    },
    "NL_HY": {
        "description": "抹消馬名テーブル - 抹消された馬の情報",
        "primary_keys": [],
    },
    # === 蓄積系 (NL_) - オッズ・票数テーブル ===
    "NL_O1": {"description": "単勝・複勝オッズ（確定）", "primary_keys": []},
    "NL_O2": {"description": "馬連オッズ（確定）", "primary_keys": []},
    "NL_O3": {"description": "ワイドオッズ（確定）", "primary_keys": []},
    "NL_O4": {"description": "馬単オッズ（確定）", "primary_keys": []},
    "NL_O5": {"description": "3連複オッズ（確定）", "primary_keys": []},
    "NL_O6": {"description": "3連単オッズ（確定）", "primary_keys": []},
    "NL_H1": {
        "description": "単勝・複勝票数（確定） - 単勝・複勝の投票数情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_H6": {
        "description": "3連単票数（確定） - 3連単の投票数情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    # === 蓄積系 (NL_) - 変更情報 ===
    "NL_JC": {
        "description": "騎手変更テーブル - 騎手の変更情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_CC": {
        "description": "コース変更テーブル - コース・距離の変更情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_TC": {
        "description": "発走時刻変更テーブル - 発走時刻の変更情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_JG": {
        "description": "出走取消・競走除外テーブル",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"],
    },
    # === 蓄積系 (NL_) - 天候・馬場情報 ===
    "NL_WE": {
        "description": "天候馬場状態テーブル - 天候と馬場状態の情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji"],
    },
    "NL_WH": {
        "description": "天候馬場変更テーブル - 天候・馬場状態の変更情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji"],
    },
    # === 蓄積系 (NL_) - 調教・その他 ===
    "NL_WC": {
        "description": "調教タイムテーブル - 調教時計・ラップタイム情報",
        "primary_keys": ["KettoNum", "ChokyoDate"],
    },
    "NL_DM": {
        "description": "デジタルメモテーブル - レース中の通過タイム情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_TM": {
        "description": "タイムマスタテーブル - タイムスコア情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_CS": {
        "description": "コース情報マスタ - 競馬場・コースの詳細情報",
        "primary_keys": ["JyoCD", "Kyori", "TrackCD"],
    },
    "NL_RC": {
        "description": "レコードタイムテーブル - コース別レコードタイム情報",
        "primary_keys": [],
    },
    "NL_YS": {
        "description": "開催スケジュールテーブル - 開催日程・重賞レース情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji"],
    },
    "NL_WF": {
        "description": "WIN5情報テーブル - WIN5の発売・払戻情報",
        "primary_keys": ["Year", "MonthDay"],
    },
    "NL_AV": {
        "description": "セリ市情報テーブル - 馬のセリ市取引情報",
        "primary_keys": ["KettoNum"],
    },
    # === 速報系 (RT_) ===
    "RT_RA": {
        "description": "レース情報テーブル（速報） - 当日のレース情報",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "RT_SE": {
        "description": "出馬表テーブル（速報） - 当日の出走馬情報・結果",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "RT_HR": {"description": "払戻テーブル（速報）", "primary_keys": []},
    "RT_O1": {"description": "単勝・複勝オッズ（速報）", "primary_keys": []},
    "RT_O2": {"description": "馬連オッズ（速報）", "primary_keys": []},
    "RT_O3": {"description": "ワイドオッズ（速報）", "primary_keys": []},
    "RT_O4": {"description": "馬単オッズ（速報）", "primary_keys": []},
    "RT_O5": {"description": "3連複オッズ（速報）", "primary_keys": []},
    "RT_O6": {"description": "3連単オッズ（速報）", "primary_keys": []},
    "RT_H1": {"description": "単勝・複勝票数（速報）", "primary_keys": []},
    "RT_H6": {"description": "3連単票数（速報）", "primary_keys": []},
    "RT_AV": {"description": "セリ市情報（速報）", "primary_keys": []},
    "RT_CC": {"description": "コース変更（速報）", "primary_keys": []},
    "RT_DM": {"description": "デジタルメモ（速報）", "primary_keys": []},
    "RT_JC": {"description": "騎手変更（速報）", "primary_keys": []},
    "RT_TC": {"description": "発走時刻変更（速報）", "primary_keys": []},
    "RT_RC": {"description": "レコードタイム（速報）", "primary_keys": []},
    "RT_TM": {"description": "タイムマスタ（速報）", "primary_keys": []},
    "RT_WE": {"description": "天候馬場状態（速報）", "primary_keys": []},
    "RT_WH": {"description": "天候馬場変更（速報）", "primary_keys": []},
    # === 時系列オッズ (TS_) ===
    "TS_O1": {
        "description": "時系列単勝・複勝オッズ - オッズの時間推移を記録",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "HassoTime", "Umaban"],
    },
    "TS_O2": {"description": "時系列馬連オッズ", "primary_keys": []},
    "TS_O3": {"description": "時系列ワイドオッズ", "primary_keys": []},
    "TS_O4": {"description": "時系列馬単オッズ", "primary_keys": []},
    "TS_O5": {"description": "時系列3連複オッズ", "primary_keys": []},
    "TS_O6": {"description": "時系列3連単オッズ", "primary_keys": []},
    # === NAR（地方競馬）蓄積系 (NL_*_NAR) ===
    "NL_RA_NAR": {
        "description": "【NAR地方競馬】レース情報テーブル（確定） - 地方競馬の各レース基本情報。JyoCD=30-57",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_SE_NAR": {
        "description": "【NAR地方競馬】出馬表テーブル（確定） - 地方競馬の出走馬情報・結果",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban"],
    },
    "NL_TK_NAR": {
        "description": "【NAR地方競馬】特別登録馬テーブル",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"],
    },
    "NL_HR_NAR": {
        "description": "【NAR地方競馬】払戻テーブル（確定）",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum"],
    },
    "NL_UM_NAR": {
        "description": "【NAR地方競馬】馬マスタテーブル - 地方競馬馬の基本情報・血統",
        "primary_keys": ["KettoNum"],
    },
    "NL_KS_NAR": {
        "description": "【NAR地方競馬】騎手マスタテーブル",
        "primary_keys": ["KisyuCode"],
    },
    "NL_CH_NAR": {
        "description": "【NAR地方競馬】調教師マスタテーブル",
        "primary_keys": ["ChokyosiCode"],
    },
    "NL_BN_NAR": {"description": "【NAR地方競馬】馬主マスタテーブル", "primary_keys": ["BanusiCode"]},
    "NL_BR_NAR": {"description": "【NAR地方競馬】生産者マスタテーブル", "primary_keys": ["BreederCode"]},
    "NL_HN_NAR": {"description": "【NAR地方競馬】繁殖馬マスタテーブル", "primary_keys": ["HansyokuNum"]},
    "NL_SK_NAR": {"description": "【NAR地方競馬】産駒マスタテーブル", "primary_keys": ["KettoNum"]},
    "NL_BT_NAR": {"description": "【NAR地方競馬】系統情報テーブル", "primary_keys": ["HansyokuNum"]},
    "NL_CK_NAR": {
        "description": "【NAR地方競馬】競走馬成績詳細テーブル",
        "primary_keys": ["Year", "MonthDay", "JyoCD", "Kaiji", "Nichiji", "RaceNum", "KettoNum"],
    },
    "NL_HC_NAR": {"description": "【NAR地方競馬】調教師賞金テーブル", "primary_keys": ["ChokyosiCode", "SetYear"]},
    "NL_HS_NAR": {"description": "【NAR地方競馬】馬市場取引価格テーブル", "primary_keys": ["KettoNum"]},
    "NL_HY_NAR": {"description": "【NAR地方競馬】抹消馬名テーブル", "primary_keys": []},
    "NL_O1_NAR": {"description": "【NAR地方競馬】単勝・複勝オッズ（確定）", "primary_keys": []},
    "NL_O2_NAR": {"description": "【NAR地方競馬】馬連オッズ（確定）", "primary_keys": []},
    "NL_O3_NAR": {"description": "【NAR地方競馬】ワイドオッズ（確定）", "primary_keys": []},
    "NL_O4_NAR": {"description": "【NAR地方競馬】馬単オッズ（確定）", "primary_keys": []},
    "NL_O5_NAR": {"description": "【NAR地方競馬】3連複オッズ（確定）", "primary_keys": []},
    "NL_O6_NAR": {"description": "【NAR地方競馬】3連単オッズ（確定）", "primary_keys": []},
    "NL_H1_NAR": {"description": "【NAR地方競馬】単勝・複勝票数（確定）", "primary_keys": []},
    "NL_H6_NAR": {"description": "【NAR地方競馬】3連単票数（確定）", "primary_keys": []},
    "NL_JC_NAR": {"description": "【NAR地方競馬】騎手変更テーブル", "primary_keys": []},
    "NL_CC_NAR": {"description": "【NAR地方競馬】コース変更テーブル", "primary_keys": []},
    "NL_TC_NAR": {"description": "【NAR地方競馬】発走時刻変更テーブル", "primary_keys": []},
    "NL_JG_NAR": {"description": "【NAR地方競馬】出走取消・競走除外テーブル", "primary_keys": []},
    "NL_WE_NAR": {"description": "【NAR地方競馬】天候馬場状態テーブル", "primary_keys": []},
    "NL_WH_NAR": {"description": "【NAR地方競馬】天候馬場変更テーブル", "primary_keys": []},
    "NL_WC_NAR": {"description": "【NAR地方競馬】調教タイムテーブル", "primary_keys": []},
    "NL_DM_NAR": {"description": "【NAR地方競馬】デジタルメモテーブル", "primary_keys": []},
    "NL_TM_NAR": {"description": "【NAR地方競馬】タイムマスタテーブル", "primary_keys": []},
    "NL_CS_NAR": {"description": "【NAR地方競馬】コース情報マスタ", "primary_keys": []},
    "NL_RC_NAR": {"description": "【NAR地方競馬】レコードタイムテーブル", "primary_keys": []},
    "NL_YS_NAR": {"description": "【NAR地方競馬】開催スケジュールテーブル", "primary_keys": []},
    "NL_WF_NAR": {"description": "【NAR地方競馬】WIN5情報テーブル", "primary_keys": []},
    "NL_AV_NAR": {"description": "【NAR地方競馬】セリ市情報テーブル", "primary_keys": []},
    # === NAR 速報系 (RT_*_NAR) ===
    "RT_RA_NAR": {"description": "【NAR地方競馬】レース情報（速報）", "primary_keys": []},
    "RT_SE_NAR": {"description": "【NAR地方競馬】出馬表・結果（速報）", "primary_keys": []},
    "RT_HR_NAR": {"description": "【NAR地方競馬】払戻（速報）", "primary_keys": []},
    "RT_O1_NAR": {"description": "【NAR地方競馬】単勝複勝オッズ（速報）", "primary_keys": []},
    "RT_O2_NAR": {"description": "【NAR地方競馬】馬連オッズ（速報）", "primary_keys": []},
    "RT_O3_NAR": {"description": "【NAR地方競馬】ワイドオッズ（速報）", "primary_keys": []},
    "RT_O4_NAR": {"description": "【NAR地方競馬】馬単オッズ（速報）", "primary_keys": []},
    "RT_O5_NAR": {"description": "【NAR地方競馬】3連複オッズ（速報）", "primary_keys": []},
    "RT_O6_NAR": {"description": "【NAR地方競馬】3連単オッズ（速報）", "primary_keys": []},
    "RT_H1_NAR": {"description": "【NAR地方競馬】単勝複勝票数（速報）", "primary_keys": []},
    "RT_H6_NAR": {"description": "【NAR地方競馬】3連単票数（速報）", "primary_keys": []},
    "RT_AV_NAR": {"description": "【NAR地方競馬】セリ市情報（速報）", "primary_keys": []},
    "RT_CC_NAR": {"description": "【NAR地方競馬】コース変更（速報）", "primary_keys": []},
    "RT_DM_NAR": {"description": "【NAR地方競馬】デジタルメモ（速報）", "primary_keys": []},
    "RT_JC_NAR": {"description": "【NAR地方競馬】騎手変更（速報）", "primary_keys": []},
    "RT_TC_NAR": {"description": "【NAR地方競馬】発走時刻変更（速報）", "primary_keys": []},
    "RT_RC_NAR": {"description": "【NAR地方競馬】レコードタイム（速報）", "primary_keys": []},
    "RT_TM_NAR": {"description": "【NAR地方競馬】タイムマスタ（速報）", "primary_keys": []},
    "RT_WE_NAR": {"description": "【NAR地方競馬】天候馬場状態（速報）", "primary_keys": []},
    "RT_WH_NAR": {"description": "【NAR地方競馬】天候馬場変更（速報）", "primary_keys": []},
    # === NAR 時系列オッズ (TS_*_NAR) ===
    "TS_O1_NAR": {"description": "【NAR地方競馬】時系列単勝複勝オッズ", "primary_keys": []},
    "TS_O2_NAR": {"description": "【NAR地方競馬】時系列馬連オッズ", "primary_keys": []},
    "TS_O3_NAR": {"description": "【NAR地方競馬】時系列ワイドオッズ", "primary_keys": []},
    "TS_O4_NAR": {"description": "【NAR地方競馬】時系列馬単オッズ", "primary_keys": []},
    "TS_O5_NAR": {"description": "【NAR地方競馬】時系列3連複オッズ", "primary_keys": []},
    "TS_O6_NAR": {"description": "【NAR地方競馬】時系列3連単オッズ", "primary_keys": []},
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

# NAR主要テーブルのカラム説明（JRAと同構造だがJyoCDが異なる）
COLUMN_DESCRIPTIONS["NL_RA_NAR"] = {
    **COLUMN_DESCRIPTIONS.get("NL_RA", {}),
    "JyoCD": "地方競馬場コード（30=門別, 31=北見, 32=岩見沢, 33=帯広, 34=旭川, 35=盛岡, 36=水沢, 37=上山, 38=三条, 39=足利, 40=宇都宮, 41=高崎, 42=浦和, 43=船橋, 44=大井, 45=川崎, 46=金沢, 47=笠松, 48=名古屋, 49=園田, 50=姫路, 51=益田, 52=福山, 53=高知, 54=佐賀, 55=荒尾, 56=中津, 57=札幌(地)）",
}
COLUMN_DESCRIPTIONS["NL_SE_NAR"] = {
    **COLUMN_DESCRIPTIONS.get("NL_SE", {}),
    "JyoCD": "地方競馬場コード（30-57、NL_RA_NARのJyoCD参照）",
}

# コード値の説明
CODE_MAPPINGS = {
    "競馬場コード": {
        "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
        "05": "東京", "06": "中山", "07": "中京", "08": "京都",
        "09": "阪神", "10": "小倉",
    },
    "地方競馬場コード": {
        "30": "門別", "31": "北見", "32": "岩見沢", "33": "帯広", "34": "旭川",
        "35": "盛岡", "36": "水沢", "37": "上山", "38": "三条", "39": "足利",
        "40": "宇都宮", "41": "高崎", "42": "浦和", "43": "船橋", "44": "大井",
        "45": "川崎", "46": "金沢", "47": "笠松", "48": "名古屋", "49": "園田",
        "50": "姫路", "51": "益田", "52": "福山", "53": "高知", "54": "佐賀",
        "55": "荒尾", "56": "中津", "57": "札幌(地)",
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

### テーブルプレフィックス

- NL_: 蓄積系（確定データ）- 過去の全データ
- RT_: 速報系（当日データ）- 当日のみ
- TS_: 時系列オッズ - オッズの時間推移

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

### 速報系・時系列オッズの使い方

- 当日のレース情報: RT_RA, RT_SE を使用
- 過去データ分析: NL_RA, NL_SE を使用
- オッズの時間推移: TS_O1〜TS_O6 を使用
  - 例: SELECT HassoTime, TanOdds FROM TS_O1 WHERE ... ORDER BY HassoTime

### 重要な制限事項

#### NL_SE.Bamei1/KettoNum1について
- Bamei1: 対戦相手の馬名（1着馬は2着馬、2着以下は1着馬）。父馬名ではない
- KettoNum1: 対戦相手の血統登録番号。父馬の血統番号ではない
- 血統情報は必ずNL_UMテーブルを使用すること

#### 地方競馬のJOIN制限
- NL_SE + NL_UM のJOINはJRA中央競馬のみ100%マッチ
- 地方競馬（JyoCD > 10）はNL_UMにデータがないためJOIN不可

### NAR（地方競馬）テーブルについて

- NARテーブルはJRAテーブルに `_NAR` サフィックスを付けた同構造テーブル
  - 例: NL_RA_NAR, NL_SE_NAR, RT_RA_NAR, TS_O1_NAR
- カラム構造はJRAテーブルと同一
- NARの競馬場コード（JyoCD）: 30-57（JRA: 01-10）
  - 主要: 44=大井, 43=船橋, 42=浦和, 45=川崎, 48=名古屋, 49=園田, 53=高知, 54=佐賀
- NAR馬マスタ: NL_UM_NAR（NL_SE_NAR.KettoNumでJOIN可能）
- JRAとNARの横断分析: UNION ALLでNL_SE + NL_SE_NARを結合

### JRA/NAR横断クエリ例

```sql
-- JRA + NAR全レースの1番人気勝率
SELECT
    CASE WHEN JyoCD <= '10' THEN 'JRA' ELSE 'NAR' END as org,
    COUNT(*) as total,
    SUM(CASE WHEN KakuteiJyuni = 1 THEN 1 ELSE 0 END) as wins
FROM (
    SELECT JyoCD, Ninki, KakuteiJyuni FROM NL_SE WHERE Ninki = 1 AND KakuteiJyuni IS NOT NULL
    UNION ALL
    SELECT JyoCD, Ninki, KakuteiJyuni FROM NL_SE_NAR WHERE Ninki = 1 AND KakuteiJyuni IS NOT NULL
) combined
GROUP BY org
```
"""


def get_column_description(table_name: str, column_name: str) -> str:
    # Try exact table name first
    if table_name in COLUMN_DESCRIPTIONS:
        manual_desc = COLUMN_DESCRIPTIONS[table_name].get(column_name, "")
        if manual_desc:
            return manual_desc
    # For NAR tables, fall back to JRA table descriptions
    if table_name.endswith("_NAR"):
        jra_table = table_name[:-4]  # Remove _NAR suffix
        if jra_table in COLUMN_DESCRIPTIONS:
            manual_desc = COLUMN_DESCRIPTIONS[jra_table].get(column_name, "")
            if manual_desc:
                return manual_desc
    return auto_generate(table_name, column_name)


def get_table_description(table_name: str) -> dict:
    return TABLE_DESCRIPTIONS.get(table_name, {
        "description": "（説明未登録）",
        "primary_keys": [],
    })