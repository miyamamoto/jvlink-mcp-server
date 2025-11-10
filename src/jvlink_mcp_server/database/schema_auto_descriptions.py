"""JVLink Database - Auto-generated Schema Descriptions

カラム名の命名規則から自動的に説明を生成します。
全410+カラムを網羅的にカバーします。
"""

import re


# カラム名パターンマッチング関数
def generate_column_description(table_name: str, column_name: str) -> str:
    """カラム名のパターンから説明を自動生成

    Args:
        table_name: テーブル名
        column_name: カラム名

    Returns:
        カラムの説明（推測も含む）
    """
    col = column_name

    # === 共通ヘッダー項目 ===
    if col == "headRecordSpec":
        return "レコード種別ID"
    if col == "headDataKubun":
        return "データ区分"
    if col == "headMakeDate":
        return "データ作成年月日（YYYYMMDD形式）"

    # === 識別子（id*） ===
    if col == "idYear":
        return "開催年（YYYY形式）"
    if col == "idMonthDay":
        return "開催月日（MMDD形式）"
    if col == "idJyoCD":
        return "競馬場コード（01=札幌, 02=函館, 03=福島, 04=新潟, 05=東京, 06=中山, 07=中京, 08=京都, 09=阪神, 10=小倉）"
    if col == "idKaiji":
        return "開催回次（第何回開催か）"
    if col == "idNichiji":
        return "開催日次（何日目か）"
    if col == "idRaceNum":
        return "レース番号（1-12）"
    if col == "idUmaban" or col == "Umaban":
        return "馬番"

    # === レース情報（RaceInfo*） ===
    if col.startswith("RaceInfo"):
        if "Hondai" in col:
            if "Eng" in col:
                return "レース正式名称（英語）"
            return "レース正式名称（例：日本ダービー、天皇賞など）"
        if "Fukudai" in col:
            if "Eng" in col:
                return "レース副題（英語）"
            return "レース副題"
        if "Kakko" in col:
            if "Eng" in col:
                return "レースカッコ内表記（英語）"
            return "レースカッコ内表記"
        if "Ryakusyo" in col:
            if "10" in col:
                return "レース略称（10文字）"
            if "6" in col:
                return "レース略称（6文字）"
            if "3" in col:
                return "レース略称（3文字）"
        if "YoubiCD" in col:
            return "曜日コード"
        if "TokuNum" in col:
            return "特別競走番号"
        if "Kubun" in col:
            return "レース区分"
        if "Nkai" in col:
            return "第N回（回数）"

    # === グレード ===
    if col == "GradeCD":
        return "グレードコード（A=G1, B=G2, C=G3, D=リステッド, E=オープン特別, F=1600万下, G=1000万下, H=500万下, I=未勝利, J=新馬）"
    if col == "GradeCDBefore":
        return "グレードコード（変更前）"

    # === 条件情報（JyokenInfo*） ===
    if col.startswith("JyokenInfo"):
        if "SyubetuCD" in col:
            return "競走種別コード（11=芝, 21=ダート, 23=障害芝, 24=障害ダート）"
        if "KigoCD" in col:
            return "競走記号コード（000=平地, 051=障害など）"
        if "JyuryoCD" in col:
            return "重量種別コード（1=ハンデ, 2=別定, 3=馬齢, 4=定量）"
        if "JyokenCD" in col:
            return "競走条件コード"

    if col == "JyokenName":
        return "競走条件名"

    # === 距離（Kyori*） ===
    if col == "Kyori":
        return "距離（メートル単位、例：1600, 2000）"
    if col == "KyoriBefore":
        return "距離（変更前、メートル単位）"

    # === トラック（Track*） ===
    if col == "TrackCD":
        return "トラックコード（10=芝・右, 11=芝・左, 18=芝・直, 20=ダート・右, 21=ダート・左, 23=ダート・直, 29=障害）"
    if col == "TrackCDBefore":
        return "トラックコード（変更前）"

    # === コース区分 ===
    if col == "CourseKubunCD":
        return "コース区分コード"
    if col == "CourseKubunCDBefore":
        return "コース区分コード（変更前）"

    # === 賞金（配列パターン） ===
    # 本賞金（0=1着, 1=2着, ...）
    if col.startswith("Honsyokin") and col[-1].isdigit():
        if "Before" in col:
            place = re.search(r'Before(\d+)', col)
            if place:
                return f"本賞金{int(place.group(1))+1}着（変更前、単位：万円）"
        else:
            place = re.search(r'Honsyokin(\d+)$', col)
            if place:
                return f"本賞金{int(place.group(1))+1}着（単位：万円）"

    # 付加賞金
    if col.startswith("Fukasyokin") and col[-1].isdigit():
        if "Before" in col:
            place = re.search(r'Before(\d+)', col)
            if place:
                return f"付加賞金{int(place.group(1))+1}着（変更前、単位：万円）"
        else:
            place = re.search(r'Fukasyokin(\d+)$', col)
            if place:
                return f"付加賞金{int(place.group(1))+1}着（単位：万円）"

    # === 発走時刻 ===
    if col == "HassoTime":
        return "発走時刻（HHmm形式、例：1530=15時30分）"
    if col == "HassoTimeBefore":
        return "発走時刻（変更前）"

    # === 頭数 ===
    if col == "TorokuTosu":
        return "登録頭数"
    if col == "SyussoTosu":
        return "出走頭数"
    if col == "NyusenTosu":
        return "入線頭数"

    # === 天候・馬場 ===
    if "TenkoCD" in col:
        return "天候コード（1=晴, 2=曇, 3=雨, 4=小雨, 5=雪, 6=小雪）"
    if "SibaBabaCD" in col:
        return "芝馬場状態コード（1=良, 2=稍重, 3=重, 4=不良）"
    if "DirtBabaCD" in col:
        return "ダート馬場状態コード（1=良, 2=稍重, 3=重, 4=不良）"

    # === ラップタイム（LapTime0~LapTime24） ===
    if col.startswith("LapTime") and col[7:].isdigit():
        lap_num = int(col[7:])
        return f"ラップタイム{lap_num+1}ハロン目（0.1秒単位）"

    # === 障害マイルタイム ===
    if col == "SyogaiMileTime":
        return "障害マイルタイム（障害レースの1マイル通過タイム）"

    # === ハロンタイム ===
    if col.startswith("HaronTime"):
        if "S3" in col:
            return "前半3ハロンタイム（前3F、0.1秒単位）"
        if "S4" in col:
            return "前半4ハロンタイム（前4F、0.1秒単位）"
        if "L3" in col:
            return "上がり3ハロンタイム（ラスト3F、0.1秒単位）"
        if "L4" in col:
            return "上がり4ハロンタイム（ラスト4F、0.1秒単位）"

    # === コーナー情報 ===
    if col.startswith("CornerInfo"):
        match = re.search(r'CornerInfo(\d+)(\w+)', col)
        if match:
            corner_num = int(match.group(1)) + 1
            info_type = match.group(2)
            if info_type == "Corner":
                return f"{corner_num}コーナー位置"
            if info_type == "Syukaisu":
                return f"{corner_num}コーナー周回数"
            if info_type == "Jyuni":
                return f"{corner_num}コーナー通過順位"

    # === レコード更新 ===
    if col == "RecordUpKubun":
        return "レコード更新区分（1=レコード, 2=タイレコード）"

    # === 出馬表・馬情報 ===
    if col == "Wakuban":
        return "枠番"
    if col == "KettoNum":
        return "血統登録番号（10桁、馬の一意識別子）"
    if col == "Bamei":
        return "馬名"
    if col == "BameiKana":
        return "馬名カナ"
    if col == "BameiEng":
        return "馬名英字"

    # === 馬記号 ===
    if "UmaKigoCD" in col:
        return "馬記号コード（[地]=地方馬, [外]=外国馬, [抽]=抽選馬など）"

    # === 性別 ===
    if col == "SexCD":
        return "性別コード（1=牡, 2=牝, 3=セン）"

    # === 品種 ===
    if col == "HinsyuCD":
        return "品種コード（1=サラブレッド系, 2=アングロアラブ系）"

    # === 毛色 ===
    if col == "KeiroCD":
        return "毛色コード（1=栗, 2=栃栗, 3=鹿, 4=黒鹿, 5=青鹿, 6=青, 7=芦, 8=栗粕, 9=鹿粕, 10=青粕, 11=白）"

    # === 馬齢 ===
    if col == "Barei":
        return "馬齢（歳）"

    # === 東西所属 ===
    if col == "TozaiCD":
        return "東西所属コード（1=美浦, 2=栗東, 3=地方, 4=海外）"

    # === 調教師 ===
    if "ChokyosiCode" in col:
        return "調教師コード"
    if "ChokyosiRyakusyo" in col:
        return "調教師略称"
    if "ChokyosiName" in col:
        return "調教師名"

    # === 馬主 ===
    if "BanusiCode" in col:
        return "馬主コード"
    if "BanusiName" in col:
        return "馬主名"

    # === 服色 ===
    if col == "Fukusyoku":
        return "服色標示（服色の説明）"

    # === 斤量 ===
    if col == "Futan":
        return "斤量（kg、55.0のように小数点1桁）"
    if col == "FutanBefore":
        return "斤量（変更前）"

    # === ブリンカー ===
    if col == "Blinker":
        return "ブリンカー使用区分（0=使用なし, 1=使用）"

    # === 騎手 ===
    if "KisyuCode" in col:
        if "Before" in col:
            return "騎手コード（変更前）"
        return "騎手コード"
    if "KisyuRyakusyo" in col:
        if "Before" in col:
            return "騎手略称（変更前）"
        return "騎手略称"
    if "KisyuName" in col:
        return "騎手名"

    # === 見習い ===
    if "MinaraiCD" in col:
        if "Before" in col:
            return "見習い区分（変更前、☆, ▲, △, ●）"
        return "見習い区分（☆=☆減3kg, ▲=▲減2kg, △=△減1kg, ●=練習生）"

    # === 馬体重 ===
    if col == "BaTaijyu":
        return "馬体重（kg）"

    # === 増減 ===
    if col == "ZogenFugo":
        return "馬体重増減記号（+, -, ±）"
    if col == "ZogenSa":
        return "馬体重増減差（kg、前走比）"

    # === 異常区分 ===
    if col == "IJyoCD":
        return "異常区分コード（1=取消, 2=除外, 3=中止, 4=失格, 5=降着, 6=再騎乗）"

    # === 着順 ===
    if col == "NyusenJyuni":
        return "入線順位（入線時の順位）"
    if col == "KakuteiJyuni":
        return "確定着順（最終確定順位、0=着外）"

    # === 同着 ===
    if col == "DochakuKubun":
        return "同着区分（1=単独, 2=同着）"
    if col == "DochakuTosu":
        return "同着頭数"

    # === タイム ===
    if col == "Time":
        return "走破タイム（MMSSf形式、例：010435=1分04秒35、0=計測なし）"

    # === 着差 ===
    if col == "ChakusaCD":
        return "着差コード（前走との着差、1=ハナ, 2=クビ, 3=1/2馬身, 4=3/4馬身, 5=1馬身, ...）"
    if col == "ChakusaCDP":
        return "着差コード（前々走との着差）"
    if col == "ChakusaCDPP":
        return "着差コード（3走前との着差）"

    # === コーナー通過順位（Jyuni1c～4c） ===
    if re.match(r'Jyuni\dc', col):
        corner = col[5]
        return f"{corner}コーナー通過順位"

    # === オッズ ===
    if col == "Odds":
        return "単勝オッズ（確定オッズ）"
    if col == "OddsWin":
        return "単勝オッズ"
    if col == "OddsPlace":
        return "複勝オッズ"

    # === 人気 ===
    if col == "Ninki":
        return "人気順位（確定後、1=1番人気）"

    # === 賞金（単体） ===
    if col == "Honsyokin":
        return "獲得本賞金（単位：万円）"
    if col == "Fukasyokin":
        return "獲得付加賞金（単位：万円）"

    # === 着順情報（ChakuUmaInfo） ===
    if col.startswith("ChakuUmaInfo"):
        match = re.search(r'ChakuUmaInfo(\d+)(\w+)', col)
        if match:
            place = int(match.group(1)) + 1
            info_type = match.group(2)
            if info_type == "KettoNum":
                return f"{place}着馬の血統登録番号"
            if info_type == "Bamei":
                return f"{place}着馬の馬名"

    # === タイム差 ===
    if col == "TimeDiff":
        return "1着馬とのタイム差（0.1秒単位）"

    # === DM（デジタルメモ） ===
    if col.startswith("DM"):
        if col == "DMKubun":
            return "デジタルメモ区分"
        if col == "DMTime":
            return "デジタルメモタイム"
        if col == "DMGosaP":
            return "デジタルメモ誤差（プラス側）"
        if col == "DMGosaM":
            return "デジタルメモ誤差（マイナス側）"
        if col == "DMJyuni":
            return "デジタルメモ着順"

    # === 客質区分 ===
    if col == "KyakusituKubun":
        return "客質区分"

    # === 血統情報（Ketto3Info） ===
    if col.startswith("Ketto3Info"):
        match = re.search(r'Ketto3Info(\d+)(\w+)', col)
        if match:
            gen_num = int(match.group(1))
            info_type = match.group(2)
            # 3代血統の位置を計算
            generations = [
                "父", "母",  # 0, 1
                "父父", "父母", "母父", "母母",  # 2-5
                "父父父", "父父母", "父母父", "父母母", "母父父", "母父母", "母母父", "母母母"  # 6-13
            ]
            if gen_num < len(generations):
                if info_type == "HansyokuNum":
                    return f"{generations[gen_num]}の繁殖登録番号"
                if info_type == "Bamei":
                    return f"{generations[gen_num]}の馬名"

    # === 生産者 ===
    if "BreederCode" in col:
        return "生産者コード"
    if "BreederName" in col:
        return "生産者名"

    # === 産地 ===
    if "SanchiName" in col:
        return "産地名"

    # === 初胎 ===
    if col == "Syotai":
        return "初胎（初仔の場合に「初」）"

    # === 累計賞金 ===
    if col.startswith("Ruikei"):
        if "Honsyo" in col:
            if "Heiti" in col or "Heichi" in col:
                return "累計本賞金（平地、単位：千円）"
            if "Syogai" in col:
                return "累計本賞金（障害、単位：千円）"
        if "Fuka" in col:
            if "Heichi" in col or "Heiti" in col:
                return "累計付加賞金（平地、単位：千円）"
            if "Syogai" in col:
                return "累計付加賞金（障害、単位：千円）"
        if "Syutoku" in col:
            if "Heichi" in col or "Heiti" in col:
                return "累計取得賞金（平地、単位：千円）"
            if "Syogai" in col:
                return "累計取得賞金（障害、単位：千円）"

    # === 着度数（ChakuSogo, ChakuChuo, ChakuKaisu） ===
    if col.startswith("Chaku"):
        # 総合着度数
        if col.startswith("ChakuSogoChakuKaisu"):
            place = re.search(r'ChakuKaisu(\d+)', col)
            if place:
                p = int(place.group(1))
                if p == 0:
                    return "総合1着回数"
                elif p == 1:
                    return "総合2着回数"
                elif p == 2:
                    return "総合3着回数"
                elif p == 3:
                    return "総合4着回数"
                elif p == 4:
                    return "総合5着回数"
                elif p == 5:
                    return "総合着外回数"

        # 中央着度数
        if col.startswith("ChakuChuoChakuKaisu"):
            place = re.search(r'ChakuKaisu(\d+)', col)
            if place:
                p = int(place.group(1))
                if p == 0:
                    return "中央1着回数"
                elif p == 1:
                    return "中央2着回数"
                elif p == 2:
                    return "中央3着回数"
                elif p == 3:
                    return "中央4着回数"
                elif p == 4:
                    return "中央5着回数"
                elif p == 5:
                    return "中央着外回数"

        # 馬場別着度数
        if col.startswith("ChakuKaisuBa"):
            match = re.search(r'ChakuKaisuBa(\d+)ChakuKaisu(\d+)', col)
            if match:
                ba_type = int(match.group(1))
                place = int(match.group(2))
                ba_names = ["芝", "ダート", "障害芝", "障害ダート", "サマー芝", "サマーダート", "サマー障害"]
                place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
                if ba_type < len(ba_names) and place < len(place_names):
                    return f"{ba_names[ba_type]}{place_names[place]}回数"

        # 馬場状態別着度数
        if col.startswith("ChakuKaisuJyotai"):
            match = re.search(r'ChakuKaisuJyotai(\d+)ChakuKaisu(\d+)', col)
            if match:
                jyotai = int(match.group(1))
                place = int(match.group(2))
                jyotai_names = [
                    "良馬場", "稍重", "重", "不良",
                    "芝良", "芝稍重", "芝重", "芝不良",
                    "ダート良", "ダート稍重", "ダート重", "ダート不良"
                ]
                place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
                if jyotai < len(jyotai_names) and place < len(place_names):
                    return f"{jyotai_names[jyotai]}{place_names[place]}回数"

        # 距離別着度数
        if col.startswith("ChakuKaisuKyori"):
            match = re.search(r'ChakuKaisuKyori(\d+)ChakuKaisu(\d+)', col)
            if match:
                kyori = int(match.group(1))
                place = int(match.group(2))
                kyori_names = [
                    "1000m以下", "1001-1300m", "1301-1500m",
                    "1501-1700m", "1701-2000m", "2001m以上"
                ]
                place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
                if kyori < len(kyori_names) and place < len(place_names):
                    return f"{kyori_names[kyori]}{place_names[place]}回数"

    # === 客質（Kyakusitu） ===
    if col.startswith("Kyakusitu") and col[-1].isdigit():
        num = int(col[-1])
        if num == 0:
            return "客質（グレード、A=G1, B=G2等）"
        elif num == 1:
            return "客質（馬場、1=芝, 2=ダート）"
        elif num == 2:
            return "客質（距離、1=短距離, 2=マイル, 3=中距離, 4=長距離）"
        elif num == 3:
            return "客質（その他区分）"

    # === レース数 ===
    if col == "RaceCount":
        return "総レース出走回数"

    # === 削除区分 ===
    if col == "DelKubun":
        return "削除区分（1=抹消）"

    # === 日付関連 ===
    if col == "RegDate":
        return "登録年月日（YYYYMMDD形式）"
    if col == "DelDate":
        return "抹消年月日（YYYYMMDD形式）"
    if col == "BirthDate":
        return "生年月日（YYYYMMDD形式またはYYYY形式）"

    # === 在厩フラグ ===
    if col == "ZaikyuFlag":
        return "在厩フラグ（1=在厩中）"

    # === リザーブ ===
    if col.startswith("reserved") or col == "Reserved":
        return "（予約領域）"

    # === 発行日・作成時刻 ===
    if col == "IssueDate":
        return "発行年月日（YYYYMMDD形式）"
    if col == "MakeHM":
        return "作成時分（HHMM形式）"

    # === 騎手資格 ===
    if col == "SikakuCD":
        return "騎手資格コード"

    # === 調教師の最近重賞成績（SaikinJyusyo0-9） ===
    if col.startswith("SaikinJyusyo"):
        match = re.search(r'SaikinJyusyo(\d+)(\w+)', col)
        if match:
            num = int(match.group(1))
            field = match.group(2)

            # IDフィールド
            if field.startswith("SaikinJyusyoid"):
                id_field = field.replace("SaikinJyusyoid", "")
                if id_field == "Year":
                    return f"最近重賞{num+1}のレース開催年"
                elif id_field == "MonthDay":
                    return f"最近重賞{num+1}のレース開催月日"
                elif id_field == "JyoCD":
                    return f"最近重賞{num+1}のレース競馬場コード"
                elif id_field == "Kaiji":
                    return f"最近重賞{num+1}のレース回次"
                elif id_field == "Nichiji":
                    return f"最近重賞{num+1}のレース日次"
                elif id_field == "RaceNum":
                    return f"最近重賞{num+1}のレース番号"

            # その他フィールド
            if field == "Hondai":
                return f"最近重賞{num+1}のレース名"
            elif field.startswith("Ryakusyo"):
                if "10" in field:
                    return f"最近重賞{num+1}のレース略称（10文字）"
                elif "6" in field:
                    return f"最近重賞{num+1}のレース略称（6文字）"
                elif "3" in field:
                    return f"最近重賞{num+1}のレース略称（3文字）"
            elif field == "GradeCD":
                return f"最近重賞{num+1}のグレード"
            elif field == "SyussoTosu":
                return f"最近重賞{num+1}の出走頭数"
            elif field == "KettoNum":
                return f"最近重賞{num+1}の勝ち馬血統登録番号"
            elif field == "Bamei":
                return f"最近重賞{num+1}の勝ち馬名"

    # === 騎手の初騎乗・初勝利（HatuKiJyo0-9, HatuSyori0-9） ===
    if col.startswith("HatuKiJyo") or col.startswith("HatuSyori"):
        is_first_win = col.startswith("HatuSyori")
        prefix = "HatuSyori" if is_first_win else "HatuKiJyo"
        label = "初勝利" if is_first_win else "初騎乗"

        match = re.search(rf'{prefix}(\d+)(\w+)', col)
        if match:
            num = int(match.group(1))
            field = match.group(2)

            # IDフィールド
            if field.startswith("Hatukijyoid"):
                id_field = field.replace("Hatukijyoid", "")
                if id_field == "Year":
                    return f"{label}場{num+1}のレース開催年"
                elif id_field == "MonthDay":
                    return f"{label}場{num+1}のレース開催月日"
                elif id_field == "JyoCD":
                    return f"{label}場{num+1}の競馬場コード"
                elif id_field == "Kaiji":
                    return f"{label}場{num+1}のレース回次"
                elif id_field == "Nichiji":
                    return f"{label}場{num+1}のレース日次"
                elif id_field == "RaceNum":
                    return f"{label}場{num+1}のレース番号"

            # その他フィールド
            if field == "SyussoTosu":
                return f"{label}場{num+1}の出走頭数"
            elif field == "KettoNum":
                return f"{label}場{num+1}の騎乗馬血統登録番号"
            elif field == "Bamei":
                return f"{label}場{num+1}の騎乗馬名"
            elif field == "KakuteiJyuni":
                return f"{label}場{num+1}の着順"
            elif field == "IJyoCD":
                return f"{label}場{num+1}の異常区分"

    # === 払戻情報（FuseirituFlag, TokubaraiFlag, HenkanFlag, HenkanUma, HenkanWaku, HenkanDoWaku） ===
    if col.startswith("FuseirituFlag"):
        num = re.search(r'FuseirituFlag(\d+)', col)
        if num:
            n = int(num.group(1))
            ticket_types = ["単勝", "複勝", "枠連", "馬連", "ワイド", "馬単", "3連複", "3連単", "WIN5"]
            if n < len(ticket_types):
                return f"{ticket_types[n]}不成立フラグ（0=成立, 1=不成立）"

    if col.startswith("TokubaraiFlag"):
        num = re.search(r'TokubaraiFlag(\d+)', col)
        if num:
            n = int(num.group(1))
            ticket_types = ["単勝", "複勝", "枠連", "馬連", "ワイド", "馬単", "3連複", "3連単", "WIN5"]
            if n < len(ticket_types):
                return f"{ticket_types[n]}特払フラグ（0=通常, 1=特払）"

    if col.startswith("HenkanFlag"):
        num = re.search(r'HenkanFlag(\d+)', col)
        if num:
            n = int(num.group(1))
            ticket_types = ["単勝", "複勝", "枠連", "馬連", "ワイド", "馬単", "3連複", "3連単", "WIN5"]
            if n < len(ticket_types):
                return f"{ticket_types[n]}返還フラグ（0=返還なし, 1=返還あり）"

    if col.startswith("HenkanUma"):
        num = re.search(r'HenkanUma(\d+)', col)
        if num:
            return f"返還馬番{num.group(1)}"

    if col.startswith("HenkanWaku"):
        num = re.search(r'HenkanWaku(\d+)', col)
        if num:
            return f"返還枠番{num.group(1)}"

    if col.startswith("HenkanDoWaku"):
        num = re.search(r'HenkanDoWaku(\d+)', col)
        if num:
            return f"返還同枠番{num.group(1)}"

    # === デジタルメモ配列（DMInfo0-17） ===
    if col.startswith("DMInfo"):
        match = re.search(r'DMInfo(\d+)(\w+)', col)
        if match:
            num = int(match.group(1))
            field = match.group(2)

            if field == "Umaban":
                return f"デジタルメモ{num+1}の馬番"
            elif field == "DMTime":
                return f"デジタルメモ{num+1}のタイム"
            elif field == "DMGosaP":
                return f"デジタルメモ{num+1}の誤差（プラス）"
            elif field == "DMGosaM":
                return f"デジタルメモ{num+1}の誤差（マイナス）"

    # === 本年前年累計成績（HonZenRuikei0-9） - 調教師・騎手の詳細成績 ===
    if col.startswith("HonZenRuikei"):
        match = re.search(r'HonZenRuikei(\d+)(\w+)', col)
        if match:
            year_idx = int(match.group(1))
            field = match.group(2)

            # 年度ラベル（0=今年, 1=前年, 2-9=その他）
            year_label = "今年" if year_idx == 0 else f"{year_idx}年前"

            # 設定年
            if field == "SetYear":
                return f"{year_label}の設定年（YYYY形式）"

            # 本賞金
            if field == "HonSyokinHeichi":
                return f"{year_label}の本賞金・平地（単位：千円）"
            if field == "HonSyokinSyogai":
                return f"{year_label}の本賞金・障害（単位：千円）"

            # 付加賞金
            if field == "FukaSyokinHeichi":
                return f"{year_label}の付加賞金・平地（単位：千円）"
            if field == "FukaSyokinSyogai":
                return f"{year_label}の付加賞金・障害（単位：千円）"

            # 着度数（平地・障害）
            chaku_match = re.search(r'ChakuKaisu(Heichi|Syogai)ChakuKaisu(\d+)', field)
            if chaku_match:
                ba_type = "平地" if chaku_match.group(1) == "Heichi" else "障害"
                place = int(chaku_match.group(2))
                place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
                if place < len(place_names):
                    return f"{year_label}の{ba_type}{place_names[place]}回数"

            # 着度数（競馬場別）
            jyo_match = re.search(r'ChakuKaisuJyo(\d+)ChakuKaisu(\d+)', field)
            if jyo_match:
                jyo_idx = int(jyo_match.group(1))
                place = int(jyo_match.group(2))
                jyo_names = [
                    "札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉",
                    "門別", "北見", "岩見沢", "帯広", "旭川"  # 地方競馬場など
                ]
                place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
                if jyo_idx < len(jyo_names) and place < len(place_names):
                    return f"{year_label}の{jyo_names[jyo_idx]}{place_names[place]}回数"
                elif place < len(place_names):
                    # 競馬場名が不明でも説明を生成
                    return f"{year_label}の競馬場{jyo_idx}{place_names[place]}回数"

            # 着度数（距離別）
            kyori_match = re.search(r'ChakuKaisuKyori(\d+)ChakuKaisu(\d+)', field)
            if kyori_match:
                kyori_idx = int(kyori_match.group(1))
                place = int(kyori_match.group(2))
                kyori_names = [
                    "1000m以下", "1001-1300m", "1301-1500m",
                    "1501-1700m", "1701-2000m", "2001m以上"
                ]
                place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
                if kyori_idx < len(kyori_names) and place < len(place_names):
                    return f"{year_label}の{kyori_names[kyori_idx]}{place_names[place]}回数"
                elif place < len(place_names):
                    return f"{year_label}の距離区分{kyori_idx}{place_names[place]}回数"

    # === 払戻金詳細（PayTansyo, PayFukusyo, PayWakuren, PayUmaren, PayWide, PayUmatan, Pay3fukutan, Pay3tan, PayWin5, PayReserved） ===
    pay_patterns = [
        ("PayTansyo", "単勝"),
        ("PayFukusyo", "複勝"),
        ("PayWakuren", "枠連"),
        ("PayUmaren", "馬連"),
        ("PayWide", "ワイド"),
        ("PayUmatan", "馬単"),
        ("Pay3fukutan", "3連複"),
        ("Pay3tan", "3連単"),
        ("PayWin5", "WIN5"),
        ("PayReserved", "予約枠")
    ]

    for prefix, ticket_name in pay_patterns:
        if col.startswith(prefix):
            match = re.search(rf'{prefix}(\d+)(\w+)', col)
            if match:
                num = int(match.group(1))
                field = match.group(2)

                if field == "Umaban":
                    return f"{ticket_name}払戻{num+1}の馬番"
                elif field == "Kumi":
                    return f"{ticket_name}払戻{num+1}の組番"
                elif field == "Pay":
                    return f"{ticket_name}払戻{num+1}の払戻金（円）"
                elif field == "Ninki":
                    return f"{ticket_name}払戻{num+1}の人気順"

    # === デフォルト：カラム名をそのまま返す ===
    return f"（説明未登録: {col}）"


# 一括説明生成関数
def get_all_column_descriptions(table_name: str, column_names: list) -> dict:
    """全カラムの説明を一括生成

    Args:
        table_name: テーブル名
        column_names: カラム名のリスト

    Returns:
        {column_name: description}の辞書
    """
    descriptions = {}
    for col_name in column_names:
        descriptions[col_name] = generate_column_description(table_name, col_name)
    return descriptions
