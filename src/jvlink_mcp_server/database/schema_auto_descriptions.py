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
    if col == "RecordSpec" or col == "headRecordSpec":
        return "レコード種別ID（例：RA, SE, HR等）"
    if col == "DataKubun" or col == "headDataKubun":
        return "データ区分（1=通常, 2=削除, 9=WIN5等）"
    if col == "MakeDate" or col == "headMakeDate":
        return "データ作成年月日（YYYYMMDD形式）"
    if col == "RecordDelimiter":
        return "レコード区切り（改行コード）"

    # === 識別子（id*または直接名） ===
    if col == "Year" or col == "idYear":
        return "開催年（YYYY形式）"
    if col == "MonthDay" or col == "idMonthDay":
        return "開催月日（MMDD形式）"
    if col == "JyoCD" or col == "idJyoCD":
        return "競馬場コード（01=札幌, 02=函館, 03=福島, 04=新潟, 05=東京, 06=中山, 07=中京, 08=京都, 09=阪神, 10=小倉）"
    if col == "Kaiji" or col == "idKaiji":
        return "開催回次（第何回開催か）"
    if col == "Nichiji" or col == "idNichiji":
        return "開催日次（何日目か）"
    if col == "RaceNum" or col == "idRaceNum":
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

    # === 票数テーブル（H1-H6）用カラム ===
    # 発売フラグ
    if col == "HatubaiFlag":
        return "発売フラグ（0=発売なし, 1=発売あり）"

    # 単勝票数 (H1)
    if col == "TansyoUmaban":
        return "単勝馬番"
    if col == "TansyoHyo":
        return "単勝票数"
    if col == "TansyoNinki":
        return "単勝人気順"
    if col == "TansyoHyoTotal":
        return "単勝票数合計"
    if col == "TansyoHenkanHyoTotal":
        return "単勝返還票数合計"

    # 複勝票数 (H1)
    if col == "FukusyoUmaban":
        return "複勝馬番"
    if col == "FukusyoHyo":
        return "複勝票数"
    if col == "FukusyoNinki":
        return "複勝人気順"
    if col == "FukusyoHyoTotal":
        return "複勝票数合計"
    if col == "FukusyoHenkanHyoTotal":
        return "複勝返還票数合計"

    # 馬連票数 (H2)
    if col == "UmarenKumi":
        return "馬連組番（4桁：上位2桁=1頭目馬番、下位2桁=2頭目馬番）"
    if col == "UmarenHyo":
        return "馬連票数"
    if col == "UmarenNinki":
        return "馬連人気順"
    if col == "UmarenHyoTotal":
        return "馬連票数合計"
    if col == "UmarenHenkanHyoTotal":
        return "馬連返還票数合計"

    # ワイド票数 (H3)
    if col == "WideKumi":
        return "ワイド組番（4桁：上位2桁=1頭目馬番、下位2桁=2頭目馬番）"
    if col == "WideHyo":
        return "ワイド票数"
    if col == "WideNinki":
        return "ワイド人気順"
    if col == "WideHyoTotal":
        return "ワイド票数合計"
    if col == "WideHenkanHyoTotal":
        return "ワイド返還票数合計"

    # 馬単票数 (H4)
    if col == "UmatanKumi":
        return "馬単組番（4桁：上位2桁=1着馬番、下位2桁=2着馬番）"
    if col == "UmatanHyo":
        return "馬単票数"
    if col == "UmatanNinki":
        return "馬単人気順"
    if col == "UmatanHyoTotal":
        return "馬単票数合計"
    if col == "UmatanHenkanHyoTotal":
        return "馬単返還票数合計"

    # 3連複票数 (H5)
    if col == "SanrenfukuKumi":
        return "3連複組番（6桁：各2桁で3頭の馬番）"
    if col == "SanrenfukuHyo":
        return "3連複票数"
    if col == "SanrenfukuNinki":
        return "3連複人気順"
    if col == "SanrenfukuHyoTotal":
        return "3連複票数合計"
    if col == "SanrenfukuHenkanHyoTotal":
        return "3連複返還票数合計"

    # 3連単票数 (H6)
    if col == "SanrentanKumi":
        return "3連単組番（6桁：各2桁で1着・2着・3着の馬番）"
    if col == "SanrentanHyo":
        return "3連単票数"
    if col == "SanrentanNinki":
        return "3連単人気順"
    if col == "SanrentanHyoTotal":
        return "3連単票数合計"
    if col == "SanrentanHenkanHyoTotal":
        return "3連単返還票数合計"

    # === オッズテーブル用フラグ ===
    if col == "TanFlag":
        return "単勝発売フラグ（0=発売なし, 1=発売あり）"
    if col == "FukuFlag":
        return "複勝発売フラグ（0=発売なし, 1=発売あり）"
    if col == "WakuFlag":
        return "枠連発売フラグ（0=発売なし, 1=発売あり）"
    if col == "UmarenFlag":
        return "馬連発売フラグ（0=発売なし, 1=発売あり）"
    if col == "WideFlag":
        return "ワイド発売フラグ（0=発売なし, 1=発売あり）"
    if col == "UmatanFlag":
        return "馬単発売フラグ（0=発売なし, 1=発売あり）"
    if col == "SanrenpukuFlag":
        return "3連複発売フラグ（0=発売なし, 1=発売あり）"
    if col == "SanrentanFlag":
        return "3連単発売フラグ（0=発売なし, 1=発売あり）"

    # オッズ値
    if col == "TanOdds":
        return "単勝オッズ"
    if col == "FukuOddsMin":
        return "複勝オッズ（最小値）"
    if col == "FukuOddsMax":
        return "複勝オッズ（最大値）"
    if col == "WakuOdds":
        return "枠連オッズ"
    if col == "UmarenOdds":
        return "馬連オッズ"
    if col == "WideOddsMin":
        return "ワイドオッズ（最小値）"
    if col == "WideOddsMax":
        return "ワイドオッズ（最大値）"
    if col == "UmatanOdds":
        return "馬単オッズ"
    if col == "SanrenpukuOdds":
        return "3連複オッズ"
    if col == "SanrentanOdds":
        return "3連単オッズ"

    # === 発売フラグ（番号付き） ===
    if col.startswith("HatubaiFlag") and col[-1].isdigit():
        num = col.replace("HatubaiFlag", "")
        flag_types = {"1": "単勝", "2": "複勝", "3": "枠連", "4": "馬連", "5": "ワイド", "6": "馬単", "7": "3連複", "8": "3連単", "9": "WIN5"}
        return f"{flag_types.get(num, num)}発売フラグ（0=発売なし, 1=発売あり）"

    # === 予約領域 ===
    if col.startswith("Reserved") or col.startswith("reserved"):
        return "予約領域（未使用）"

    # === その他の共通カラム ===
    if col == "HappyoTime":
        return "発表時刻（HHmm形式）"
    if col == "HenkoID":
        return "変更ID"
    if col == "SetYear":
        return "設定年（YYYY形式）"
    if col == "HonSyokinTotal":
        return "本賞金合計（単位：万円）"
    if col == "FukaSyokin":
        return "付加賞金（単位：万円）"
    if col == "ChakuKaisu":
        return "着回数"
    if col == "YoubiCD":
        return "曜日コード（0=日, 1=月, 2=火, 3=水, 4=木, 5=金, 6=土）"
    if col == "TokuNum":
        return "特別競走番号"
    if col == "HondaiEng":
        return "レース名（英語）"
    if col == "FukudaiEng":
        return "副題（英語）"
    if col == "KakkoEng":
        return "カッコ内表記（英語）"
    if col.startswith("Ryakusyo"):
        if "10" in col:
            return "略称（10文字）"
        if "6" in col:
            return "略称（6文字）"
        if "3" in col:
            return "略称（3文字）"
        return "略称"
    if col == "Hondai":
        return "レース名（正式名称）"
    if col == "Fukudai":
        return "副題"
    if col == "Kakko":
        return "カッコ内表記"

    # === 繁殖・血統関連 ===
    if col == "HansyokuNum":
        return "繁殖登録番号"
    if col == "FHansyokuNum":
        return "父の繁殖登録番号"
    if col == "MHansyokuNum":
        return "母の繁殖登録番号"
    if col == "KeitoId":
        return "系統ID"
    if col == "KeitoName":
        return "系統名"
    if col == "KeitoEx":
        return "系統説明"
    if col == "MochiKubun":
        return "持込区分"
    if col == "ImportYear":
        return "輸入年"
    if col == "SankuMochiKubun":
        return "産駒持込区分"
    if col == "FNum":
        return "父番号"
    if col == "BirthYear":
        return "生年"
    if col.startswith("Ketto3InfoHansyokuNum"):
        match = re.search(r'Ketto3InfoHansyokuNum(\d+)', col)
        if match:
            gen_num = int(match.group(1))
            generations = ["父", "母", "父父", "父母", "母父", "母母", "父父父", "父父母", "父母父", "父母母", "母父父", "母父母", "母母父", "母母母"]
            if gen_num <= len(generations):
                return f"{generations[gen_num-1]}の繁殖登録番号"

    # === コース・馬場情報 ===
    if col == "Course":
        return "コース"
    if col == "CourseEx":
        return "コース説明"
    if col == "KaishuDate":
        return "開催日"
    if col == "TresenKubun":
        return "トレセン区分（1=美浦, 2=栗東）"
    if col == "ChokyoDate":
        return "調教日"
    if col == "ChokyoTime":
        return "調教時刻"
    if col == "BabaMawari":
        return "馬場回り"
    if col == "HaronTime10Total":
        return "10ハロンタイム合計"
    if col.startswith("LapTime_"):
        return f"ラップタイム（{col.replace('LapTime_', '')}）"

    # === 売上・販売情報 ===
    if col == "SaleHostName":
        return "販売元名"
    if col == "SaleName":
        return "販売名"
    if col == "SaleCode":
        return "販売コード"
    if col == "Price":
        return "価格"
    if col == "FromDate":
        return "開始日"
    if col == "ToDate":
        return "終了日"
    if col == "Address":
        return "住所"
    if col == "Num":
        return "番号"

    # === タイムマスタ ===
    if col == "TMScore":
        return "タイムスコア"

    # === 重賞成績関連（番号なし直接参照） ===
    if col.startswith("SaikinJyusyo") and "_id" in col:
        return "最近重賞のレースID"
    if col.startswith("HatuKiJyo") and "id" in col:
        return "初騎乗のレースID"
    if col.startswith("HatuSyori") and "id" in col:
        return "初勝利のレースID"

    # === 変更理由 ===
    if col == "HenkouJiyuCD":
        return "変更事由コード"
    if col == "RecInfoKubun":
        return "レコード情報区分"

    # === 賞金詳細 ===
    if col == "HeichiHonsyokinTotal":
        return "平地本賞金合計（単位：万円）"
    if col == "SyogaiHonsyokinTotal":
        return "障害本賞金合計（単位：万円）"
    if col == "HonSyokinHeichi":
        return "本賞金・平地（単位：万円）"
    if col == "HonSyokinSyogai":
        return "本賞金・障害（単位：万円）"
    if col == "FukaSyokinHeichi":
        return "付加賞金・平地（単位：万円）"
    if col == "FukaSyokinSyogai":
        return "付加賞金・障害（単位：万円）"

    # === 開催スケジュール ===
    if col.startswith("Jyusyo") and "TokuNum" in col:
        return "重賞特別競走番号"

    # === Yobi（予備）フィールド ===
    if col.startswith("Yobi"):
        return "予備フィールド"
    if col.startswith("Field"):
        return "予備フィールド"

    # === オッズテーブル共通 ===
    if col == "Kumi":
        return "組番（馬番の組み合わせ）"
    if col == "Vote":
        return "票数"
    if col == "OddsLow":
        return "オッズ（下限）"
    if col == "OddsHigh":
        return "オッズ（上限）"
    if col == "WakurenFlag":
        return "枠連発売フラグ（0=発売なし, 1=発売あり）"
    if col == "FukuChakubaraiKey" or col == "FukuChakuBaraiKey":
        return "複勝着払いキー"
    if col == "TanNinki":
        return "単勝人気順"
    if col == "TanUma":
        return "単勝馬番"
    if col == "TanHyo":
        return "単勝票数"
    if col == "FukuUma":
        return "複勝馬番"
    if col == "FukuHyo":
        return "複勝票数"
    if col == "crlf":
        return "改行コード"

    # === コース変更情報 ===
    if col == "AtoKyori":
        return "変更後距離（メートル）"
    if col == "AtoTruckCD" or col == "AtoTrackCD":
        return "変更後トラックコード"
    if col == "MaeKyori":
        return "変更前距離（メートル）"
    if col == "MaeTruckCD" or col == "MaeTrackCD":
        return "変更前トラックコード"
    if col == "JiyuCD":
        return "事由コード"
    if col == "AtoFutan":
        return "変更後斤量"
    if col == "MaeFutan":
        return "変更前斤量"
    if col == "AtoJi":
        return "変更後時"
    if col == "AtoFun":
        return "変更後分"
    if col == "MaeJi":
        return "変更前時"
    if col == "MaeFun":
        return "変更前分"

    # === 競走条件 ===
    if col == "Kubun":
        return "区分"
    if col == "Nkai":
        return "第N回"
    if col.startswith("JyokenCD"):
        return "競走条件コード"
    if col == "SyubetuCD":
        return "競走種別コード（11=芝, 21=ダート, 23=障害芝, 24=障害ダート）"
    if col == "SyubetuCD_TrackCD":
        return "競走種別・トラックコード"
    if col == "RecKubun":
        return "レコード区分"
    if col == "RecTime":
        return "レコードタイム"

    # === 天候・馬場状態 ===
    if col == "TenkoState":
        return "天候状態"
    if col == "SibaBabaState":
        return "芝馬場状態"
    if col == "DirtBabaState":
        return "ダート馬場状態"

    # === 出走関連 ===
    if col == "SyussoKubun":
        return "出走区分"
    if col == "JyogaiStateKubun":
        return "除外状態区分"

    # === 繁殖関連 ===
    if col == "HansyokuFNum":
        return "父の繁殖番号"
    if col == "HansyokuMNum":
        return "母の繁殖番号"

    # === 着払い情報 ===
    if col == "HenkanUma":
        return "返還馬番情報"

    # === 9番目のフラグ（WIN5用） ===
    if col == "FuseirituFlag9":
        return "WIN5不成立フラグ（0=成立, 1=不成立）"
    if col == "TokubaraiFlag9":
        return "WIN5特払フラグ（0=通常, 1=特払）"
    if col == "HenkanFlag9":
        return "WIN5返還フラグ（0=返還なし, 1=返還あり）"

    # === 血統情報（拡張） ===
    for i in range(7, 15):
        if col == f"Ketto3InfoBamei{i}":
            generations = ["父", "母", "父父", "父母", "母父", "母母", "父父父", "父父母", "父母父", "父母母", "母父父", "母父母", "母母父", "母母母"]
            if i <= len(generations):
                return f"{generations[i-1]}の馬名"

    # === 賞金詳細（拡張） ===
    if col == "HeichiFukasyokinTotal":
        return "平地付加賞金合計（単位：万円）"
    if col == "SyogaiFukasyokinTotal":
        return "障害付加賞金合計（単位：万円）"
    if col == "HeichiSyutokuTotal":
        return "平地取得賞金合計（単位：万円）"
    if col == "SyogaiSyutokuTotal":
        return "障害取得賞金合計（単位：万円）"

    # === 重賞成績詳細 ===
    if col.startswith("SaikinJyusyo") and "_" in col:
        parts = col.split("_")
        if len(parts) >= 2:
            field = parts[1]
            if field == "Hondai":
                return "最近重賞のレース名"
            if "Ryakusyo" in field:
                return "最近重賞のレース略称"
            if field == "GradeCD":
                return "最近重賞のグレード"
            if field == "SyussoTosu":
                return "最近重賞の出走頭数"
            if field == "KettoNum":
                return "最近重賞の勝ち馬血統番号"
            if field == "Bamei":
                return "最近重賞の勝ち馬名"
            if field == "id":
                return "最近重賞のレースID"

    # === 開催スケジュール詳細 ===
    if col.startswith("Jyusyo") and not "TokuNum" in col:
        if "Hondai" in col:
            return "重賞レース名"
        if "Ryakusyo" in col:
            return "重賞略称"

    # === レース情報（番号付き） ===
    if col.startswith("RaceInfo") and col[-1].isdigit():
        return "レース情報"

    # === レース略称 ===
    if col.startswith("RaceRyakusyo"):
        if "10" in col:
            return "レース略称（10文字）"
        if "6" in col:
            return "レース略称（6文字）"
        if "3" in col:
            return "レース略称（3文字）"
        return "レース略称"

    # === ハロンタイム詳細 ===
    if col.startswith("HaronTime") and "Total" in col:
        match = re.search(r'HaronTime(\d+)Total', col)
        if match:
            return f"{match.group(1)}ハロンタイム合計"

    # === 出馬表の対戦情報 ===
    if col == "KettoNum1":
        return "対戦相手の血統登録番号（1着馬は2着馬、2着以下は1着馬）"
    if col == "Bamei1":
        return "対戦相手の馬名（1着馬は2着馬、2着以下は1着馬）"

    # === NL_CH/NL_KS: 最近重賞成績配列（番号付き直接パターン） ===
    # SaikinJyusyo0Hondai, SaikinJyusyo1GradeCD など
    saikin_match = re.match(r'SaikinJyusyo(\d+)(.+)', col)
    if saikin_match:
        num = int(saikin_match.group(1)) + 1
        field = saikin_match.group(2)

        # IDフィールド（SaikinJyusyoidYear等）
        if field.startswith("SaikinJyusyoid"):
            id_part = field.replace("SaikinJyusyoid", "")
            id_map = {
                "Year": "開催年",
                "MonthDay": "開催月日",
                "JyoCD": "競馬場コード",
                "Kaiji": "回次",
                "Nichiji": "日次",
                "RaceNum": "レース番号"
            }
            if id_part in id_map:
                return f"最近重賞{num}の{id_map[id_part]}"

        # 他のフィールド
        field_map = {
            "Hondai": "レース名",
            "Ryakusyo10": "レース略称（10文字）",
            "Ryakusyo6": "レース略称（6文字）",
            "Ryakusyo3": "レース略称（3文字）",
            "GradeCD": "グレードコード",
            "SyussoTosu": "出走頭数",
            "KettoNum": "勝ち馬血統登録番号",
            "Bamei": "勝ち馬名"
        }
        if field in field_map:
            return f"最近重賞{num}の{field_map[field]}"

        # Ryakusyoのバリエーション
        if "Ryakusyo" in field:
            return f"最近重賞{num}のレース略称"

    # === NL_CK: 競馬場別着度数（ChakuKaisuJyo0~9） ===
    jyo_chaku_match = re.match(r'ChakuKaisuJyo(\d+)ChakuKaisu(\d+)', col)
    if jyo_chaku_match:
        jyo_idx = int(jyo_chaku_match.group(1))
        place_idx = int(jyo_chaku_match.group(2))
        jyo_names = ["札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]
        place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
        jyo_name = jyo_names[jyo_idx] if jyo_idx < len(jyo_names) else f"競馬場{jyo_idx}"
        place_name = place_names[place_idx] if place_idx < len(place_names) else f"{place_idx}着"
        return f"{jyo_name}{place_name}回数"

    # === NL_CK: 距離別着度数（ChakuKaisuKyori0~5） ===
    kyori_chaku_match = re.match(r'ChakuKaisuKyori(\d+)ChakuKaisu(\d+)', col)
    if kyori_chaku_match:
        kyori_idx = int(kyori_chaku_match.group(1))
        place_idx = int(kyori_chaku_match.group(2))
        kyori_names = ["〜1000m", "1001〜1300m", "1301〜1600m", "1601〜1900m", "1901〜2200m", "2201m〜"]
        place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
        kyori_name = kyori_names[kyori_idx] if kyori_idx < len(kyori_names) else f"距離{kyori_idx}"
        place_name = place_names[place_idx] if place_idx < len(place_names) else f"{place_idx}着"
        return f"{kyori_name}{place_name}回数"

    # === NL_O1: 単勝・複勝オッズ配列（TanOddsUmaban0~17, FukuOdds0~17） ===
    tan_odds_match = re.match(r'TanOddsUmaban(\d+)', col)
    if tan_odds_match:
        num = int(tan_odds_match.group(1)) + 1
        return f"単勝オッズ{num}番馬番"

    tan_odds_val = re.match(r'TanOdds(\d+)$', col)
    if tan_odds_val:
        num = int(tan_odds_val.group(1)) + 1
        return f"単勝オッズ{num}番馬"

    fuku_odds_val = re.match(r'FukuOdds(\d+)$', col)
    if fuku_odds_val:
        num = int(fuku_odds_val.group(1)) + 1
        return f"複勝オッズ{num}番馬"

    fuku_odds_min = re.match(r'FukuOddsMin(\d+)', col)
    if fuku_odds_min:
        num = int(fuku_odds_min.group(1)) + 1
        return f"複勝オッズ{num}番馬（下限）"

    fuku_odds_max = re.match(r'FukuOddsMax(\d+)', col)
    if fuku_odds_max:
        num = int(fuku_odds_max.group(1)) + 1
        return f"複勝オッズ{num}番馬（上限）"

    # === NL_O1: 枠連オッズ（WakurenOdds0~35） ===
    waku_odds = re.match(r'WakurenOdds(\d+)', col)
    if waku_odds:
        num = int(waku_odds.group(1)) + 1
        return f"枠連オッズ{num}番組"

    # === NL_O2: 馬連オッズ（UmarenOdds0~152） ===
    umaren_odds = re.match(r'UmarenOdds(\d+)$', col)
    if umaren_odds:
        num = int(umaren_odds.group(1)) + 1
        return f"馬連オッズ{num}番組"

    umaren_kumi = re.match(r'UmarenKumi(\d+)', col)
    if umaren_kumi:
        num = int(umaren_kumi.group(1)) + 1
        return f"馬連{num}番組の組番"

    umaren_ninki = re.match(r'UmarenNinki(\d+)', col)
    if umaren_ninki:
        num = int(umaren_ninki.group(1)) + 1
        return f"馬連{num}番組の人気順"

    # === NL_O3: ワイドオッズ（WideOddsMin0~152, WideOddsMax0~152） ===
    wide_min = re.match(r'WideOddsMin(\d+)', col)
    if wide_min:
        num = int(wide_min.group(1)) + 1
        return f"ワイドオッズ{num}番組（下限）"

    wide_max = re.match(r'WideOddsMax(\d+)', col)
    if wide_max:
        num = int(wide_max.group(1)) + 1
        return f"ワイドオッズ{num}番組（上限）"

    wide_kumi = re.match(r'WideKumi(\d+)', col)
    if wide_kumi:
        num = int(wide_kumi.group(1)) + 1
        return f"ワイド{num}番組の組番"

    wide_ninki = re.match(r'WideNinki(\d+)', col)
    if wide_ninki:
        num = int(wide_ninki.group(1)) + 1
        return f"ワイド{num}番組の人気順"

    # === NL_O4: 馬単オッズ（UmatanOdds0~305） ===
    umatan_odds = re.match(r'UmatanOdds(\d+)$', col)
    if umatan_odds:
        num = int(umatan_odds.group(1)) + 1
        return f"馬単オッズ{num}番組"

    umatan_kumi = re.match(r'UmatanKumi(\d+)', col)
    if umatan_kumi:
        num = int(umatan_kumi.group(1)) + 1
        return f"馬単{num}番組の組番"

    umatan_ninki = re.match(r'UmatanNinki(\d+)', col)
    if umatan_ninki:
        num = int(umatan_ninki.group(1)) + 1
        return f"馬単{num}番組の人気順"

    # === NL_O5: 3連複オッズ（SanrenpukuOdds0~815） ===
    sanrenp_odds = re.match(r'SanrenpukuOdds(\d+)$', col)
    if sanrenp_odds:
        num = int(sanrenp_odds.group(1)) + 1
        return f"3連複オッズ{num}番組"

    sanrenp_kumi = re.match(r'SanrenpukuKumi(\d+)', col)
    if sanrenp_kumi:
        num = int(sanrenp_kumi.group(1)) + 1
        return f"3連複{num}番組の組番"

    sanrenp_ninki = re.match(r'SanrenpukuNinki(\d+)', col)
    if sanrenp_ninki:
        num = int(sanrenp_ninki.group(1)) + 1
        return f"3連複{num}番組の人気順"

    # === NL_O6: 3連単オッズ（SanrentanOdds0~4895） ===
    sanrent_odds = re.match(r'SanrentanOdds(\d+)$', col)
    if sanrent_odds:
        num = int(sanrent_odds.group(1)) + 1
        return f"3連単オッズ{num}番組"

    sanrent_kumi = re.match(r'SanrentanKumi(\d+)', col)
    if sanrent_kumi:
        num = int(sanrent_kumi.group(1)) + 1
        return f"3連単{num}番組の組番"

    sanrent_ninki = re.match(r'SanrentanNinki(\d+)', col)
    if sanrent_ninki:
        num = int(sanrent_ninki.group(1)) + 1
        return f"3連単{num}番組の人気順"

    # === NL_RA: レース条件コード（JyokenCD1~5） ===
    jyoken_match = re.match(r'JyokenCD(\d+)', col)
    if jyoken_match:
        num = int(jyoken_match.group(1))
        return f"競走条件コード{num}（出走条件の詳細）"

    # === NL_RA: 競走記号コード ===
    if col == "KigoCD":
        return "競走記号コード（000=一般, 001=指定, 002=見習騎手, 010=馬齢戦など）"

    # === NL_RA: 重量種別コード ===
    if col == "JyuryoCD":
        return "重量種別コード（1=ハンデ, 2=別定, 3=馬齢, 4=定量）"

    # === NL_RA: グレードコード ===
    if col == "GradeCD":
        return "グレードコード（A=G1, B=G2, C=G3, D=リステッド, E=オープン, F=3勝クラス等）"

    # === NL_RA: コーナー情報配列（CornerInfo0~3） ===
    corner_match = re.match(r'CornerInfo(\d+)(.+)', col)
    if corner_match:
        corner_num = int(corner_match.group(1)) + 1
        field = corner_match.group(2)
        field_map = {
            "Corner": "位置",
            "Syukaisu": "周回数",
            "Jyuni": "通過順位"
        }
        if field in field_map:
            return f"{corner_num}コーナー{field_map[field]}"
        return f"{corner_num}コーナー情報"

    # === 血統情報配列（Ketto3Info0~13） ===
    ketto_match = re.match(r'Ketto3Info(\d+)(.+)', col)
    if ketto_match:
        gen_num = int(ketto_match.group(1))
        field = ketto_match.group(2)
        generations = ["父", "母", "父父", "父母", "母父", "母母",
                      "父父父", "父父母", "父母父", "父母母",
                      "母父父", "母父母", "母母父", "母母母"]
        gen_name = generations[gen_num] if gen_num < len(generations) else f"祖先{gen_num}"

        if field == "HansyokuNum":
            return f"{gen_name}の繁殖登録番号"
        if field == "Bamei":
            return f"{gen_name}の馬名"
        return f"{gen_name}の情報"

    # === 本年前年累計詳細（HonZenRuikei配列） ===
    honzen_match = re.match(r'HonZenRuikei(\d+)(.+)', col)
    if honzen_match:
        year_idx = int(honzen_match.group(1))
        field = honzen_match.group(2)
        year_label = "今年" if year_idx == 0 else f"{year_idx}年前"

        # 競馬場別着度数
        jyo_match2 = re.match(r'ChakuKaisuJyo(\d+)ChakuKaisu(\d+)', field)
        if jyo_match2:
            jyo_idx = int(jyo_match2.group(1))
            place_idx = int(jyo_match2.group(2))
            jyo_names = ["札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]
            place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
            jyo_name = jyo_names[jyo_idx] if jyo_idx < len(jyo_names) else f"競馬場{jyo_idx}"
            place_name = place_names[place_idx] if place_idx < len(place_names) else f"{place_idx}着"
            return f"{year_label}の{jyo_name}{place_name}回数"

        # その他のフィールド
        field_map = {
            "SetYear": "設定年",
            "HonSyokinHeichi": "本賞金・平地",
            "HonSyokinSyogai": "本賞金・障害",
            "FukaSyokinHeichi": "付加賞金・平地",
            "FukaSyokinSyogai": "付加賞金・障害"
        }
        if field in field_map:
            return f"{year_label}の{field_map[field]}"

    # === 初騎乗・初勝利詳細（HatuKiJyo, HatuSyori配列） ===
    hatuki_match = re.match(r'HatuKiJyo(\d+)(.+)', col)
    if hatuki_match:
        num = int(hatuki_match.group(1)) + 1
        field = hatuki_match.group(2)

        if field.startswith("Hatukijyoid"):
            id_part = field.replace("Hatukijyoid", "")
            id_map = {"Year": "開催年", "MonthDay": "開催月日", "JyoCD": "競馬場コード",
                      "Kaiji": "回次", "Nichiji": "日次", "RaceNum": "レース番号"}
            if id_part in id_map:
                return f"初騎乗{num}の{id_map[id_part]}"

        field_map = {"SyussoTosu": "出走頭数", "KettoNum": "騎乗馬血統番号",
                     "Bamei": "騎乗馬名", "KakuteiJyuni": "着順", "IJyoCD": "異常区分"}
        if field in field_map:
            return f"初騎乗{num}の{field_map[field]}"

    hatusyori_match = re.match(r'HatuSyori(\d+)(.+)', col)
    if hatusyori_match:
        num = int(hatusyori_match.group(1)) + 1
        field = hatusyori_match.group(2)

        if field.startswith("Hatukijyoid"):
            id_part = field.replace("Hatukijyoid", "")
            id_map = {"Year": "開催年", "MonthDay": "開催月日", "JyoCD": "競馬場コード",
                      "Kaiji": "回次", "Nichiji": "日次", "RaceNum": "レース番号"}
            if id_part in id_map:
                return f"初勝利{num}の{id_map[id_part]}"

        field_map = {"SyussoTosu": "出走頭数", "KettoNum": "騎乗馬血統番号",
                     "Bamei": "騎乗馬名", "KakuteiJyuni": "着順", "IJyoCD": "異常区分"}
        if field in field_map:
            return f"初勝利{num}の{field_map[field]}"

    # === 払戻配列（PayTansyo, PayFukusyo等） ===
    pay_match = re.match(r'Pay(Tansyo|Fukusyo|Wakuren|Umaren|Wide|Umatan|3fukutan|3tan|Win5|Reserved)(\d+)(.+)', col)
    if pay_match:
        pay_type = pay_match.group(1)
        num = int(pay_match.group(2)) + 1
        field = pay_match.group(3)

        pay_names = {
            "Tansyo": "単勝", "Fukusyo": "複勝", "Wakuren": "枠連",
            "Umaren": "馬連", "Wide": "ワイド", "Umatan": "馬単",
            "3fukutan": "3連複", "3tan": "3連単", "Win5": "WIN5", "Reserved": "予約"
        }
        pay_name = pay_names.get(pay_type, pay_type)

        field_map = {"Umaban": "馬番", "Kumi": "組番", "Pay": "払戻金", "Ninki": "人気順"}
        if field in field_map:
            return f"{pay_name}払戻{num}の{field_map[field]}"

    # === デジタルメモ配列（DMInfo0~17） ===
    dm_match = re.match(r'DMInfo(\d+)(.+)', col)
    if dm_match:
        num = int(dm_match.group(1)) + 1
        field = dm_match.group(2)
        field_map = {"Umaban": "馬番", "DMTime": "タイム", "DMGosaP": "誤差（+）", "DMGosaM": "誤差（-）"}
        if field in field_map:
            return f"デジタルメモ{num}の{field_map[field]}"

    # === 着馬情報配列（ChakuUmaInfo0~4） ===
    chaku_uma_match = re.match(r'ChakuUmaInfo(\d+)(.+)', col)
    if chaku_uma_match:
        place = int(chaku_uma_match.group(1)) + 1
        field = chaku_uma_match.group(2)
        if field == "KettoNum":
            return f"{place}着馬の血統登録番号"
        if field == "Bamei":
            return f"{place}着馬の馬名"

    # === 票数配列 ===
    # TansyoInfo, FukusyoInfo等
    hyo_patterns = [
        (r'TansyoInfo(\d+)(.+)', "単勝"),
        (r'FukusyoInfo(\d+)(.+)', "複勝"),
        (r'UmarenInfo(\d+)(.+)', "馬連"),
        (r'WideInfo(\d+)(.+)', "ワイド"),
        (r'UmatanInfo(\d+)(.+)', "馬単"),
        (r'SanrenfukuInfo(\d+)(.+)', "3連複"),
        (r'SanrentanInfo(\d+)(.+)', "3連単"),
    ]
    for pattern, hyo_name in hyo_patterns:
        hyo_match = re.match(pattern, col)
        if hyo_match:
            num = int(hyo_match.group(1)) + 1
            field = hyo_match.group(2)
            field_map = {"Umaban": "馬番", "Kumi": "組番", "Hyo": "票数", "Ninki": "人気順"}
            if field in field_map:
                return f"{hyo_name}{num}の{field_map[field]}"

    # === 枠連組番・票数 ===
    wakuren_match = re.match(r'WakurenKumi(\d+)', col)
    if wakuren_match:
        num = int(wakuren_match.group(1)) + 1
        return f"枠連{num}番組の組番"

    wakuren_hyo = re.match(r'WakurenHyo(\d+)', col)
    if wakuren_hyo:
        num = int(wakuren_hyo.group(1)) + 1
        return f"枠連{num}番組の票数"

    wakuren_ninki = re.match(r'WakurenNinki(\d+)', col)
    if wakuren_ninki:
        num = int(wakuren_ninki.group(1)) + 1
        return f"枠連{num}番組の人気順"

    # === 総合・中央着度数 ===
    sogo_match = re.match(r'ChakuSogo(.+)', col)
    if sogo_match:
        field = sogo_match.group(1)
        chaku_match = re.match(r'ChakuKaisu(\d+)', field)
        if chaku_match:
            place_idx = int(chaku_match.group(1))
            place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
            place = place_names[place_idx] if place_idx < len(place_names) else f"{place_idx}着"
            return f"総合{place}回数"

    chuo_match = re.match(r'ChakuChuo(.+)', col)
    if chuo_match:
        field = chuo_match.group(1)
        chaku_match = re.match(r'ChakuKaisu(\d+)', field)
        if chaku_match:
            place_idx = int(chaku_match.group(1))
            place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
            place = place_names[place_idx] if place_idx < len(place_names) else f"{place_idx}着"
            return f"中央{place}回数"

    # === 馬場別着度数（直接パターン） ===
    baba_match = re.match(r'ChakuKaisuBa(\d+)ChakuKaisu(\d+)', col)
    if baba_match:
        ba_idx = int(baba_match.group(1))
        place_idx = int(baba_match.group(2))
        ba_names = ["芝", "ダート", "障害芝", "障害ダート"]
        place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
        ba = ba_names[ba_idx] if ba_idx < len(ba_names) else f"馬場{ba_idx}"
        place = place_names[place_idx] if place_idx < len(place_names) else f"{place_idx}着"
        return f"{ba}{place}回数"

    # === 馬場状態別着度数 ===
    jyotai_match = re.match(r'ChakuKaisuJyotai(\d+)ChakuKaisu(\d+)', col)
    if jyotai_match:
        jyotai_idx = int(jyotai_match.group(1))
        place_idx = int(jyotai_match.group(2))
        jyotai_names = ["良", "稍重", "重", "不良"]
        place_names = ["1着", "2着", "3着", "4着", "5着", "着外"]
        jyotai = jyotai_names[jyotai_idx] if jyotai_idx < len(jyotai_names) else f"状態{jyotai_idx}"
        place = place_names[place_idx] if place_idx < len(place_names) else f"{place_idx}着"
        return f"馬場{jyotai}{place}回数"

    # === 開催スケジュール配列（JyusyoInfo0~9） ===
    jyusyo_info = re.match(r'JyusyoInfo(\d+)(.+)', col)
    if jyusyo_info:
        num = int(jyusyo_info.group(1)) + 1
        field = jyusyo_info.group(2)
        if "Hondai" in field:
            return f"重賞{num}のレース名"
        if "Ryakusyo" in field:
            return f"重賞{num}の略称"
        if "GradeCD" in field:
            return f"重賞{num}のグレード"
        if "TokuNum" in field:
            return f"重賞{num}の特別競走番号"
        return f"重賞{num}の情報"

    # === WIN5情報 ===
    if col.startswith("Win5") or col.startswith("WIN5"):
        return "WIN5関連情報"

    # === NL_CK: 着度数詳細（芝・ダート・障害・回り・馬場状態別） ===
    if col == "TotalChakuCount":
        return "総合着回数"
    if col == "ChuoChakuCount":
        return "中央着回数"

    # 芝・ダート・障害の直進/右回り/左回り
    track_patterns = [
        ("SibaChoChaku", "芝直線コース着回数"),
        ("SibaMigiChaku", "芝右回り着回数"),
        ("SibaHidariChaku", "芝左回り着回数"),
        ("DirtChoChaku", "ダート直線コース着回数"),
        ("DirtMigiChaku", "ダート右回り着回数"),
        ("DirtHidariChaku", "ダート左回り着回数"),
        ("SyogaiChaku", "障害着回数"),
    ]
    for pattern, desc in track_patterns:
        if col == pattern:
            return desc

    # 馬場状態別着回数（芝・ダート・障害）
    baba_patterns = [
        ("SibaRyoChaku", "芝良馬場着回数"),
        ("SibaYayaChaku", "芝稍重着回数"),
        ("SibaOmoChaku", "芝重馬場着回数"),
        ("SibaFuryoChaku", "芝不良馬場着回数"),
        ("SibaFuChaku", "芝不良馬場着回数"),
        ("DirtRyoChaku", "ダート良馬場着回数"),
        ("DirtYayaChaku", "ダート稍重着回数"),
        ("DirtOmoChaku", "ダート重馬場着回数"),
        ("DirtFuryoChaku", "ダート不良馬場着回数"),
        ("DirtFuChaku", "ダート不良馬場着回数"),
        ("SyogaiRyoChaku", "障害良馬場着回数"),
        ("SyogaiYayaChaku", "障害稍重着回数"),
        ("SyogaiOmoChaku", "障害重馬場着回数"),
        ("SyogaiFuryoChaku", "障害不良馬場着回数"),
        ("SyogaiFuChaku", "障害不良馬場着回数"),
    ]
    for pattern, desc in baba_patterns:
        if col == pattern:
            return desc

    # 季節別着回数
    season_patterns = [
        ("SpringChaku", "春季着回数"),
        ("SummerChaku", "夏季着回数"),
        ("AutumnChaku", "秋季着回数"),
        ("WinterChaku", "冬季着回数"),
    ]
    for pattern, desc in season_patterns:
        if col == pattern:
            return desc

    # 距離別着回数（詳細）
    dist_patterns = [
        ("Dist1000Chaku", "1000m以下着回数"),
        ("Dist1200Chaku", "1200m着回数"),
        ("Dist1400Chaku", "1400m着回数"),
        ("Dist1600Chaku", "1600m着回数"),
        ("Dist1800Chaku", "1800m着回数"),
        ("Dist2000Chaku", "2000m着回数"),
        ("Dist2200Chaku", "2200m着回数"),
        ("Dist2400Chaku", "2400m着回数"),
        ("Dist2500Chaku", "2500m以上着回数"),
    ]
    for pattern, desc in dist_patterns:
        if col == pattern:
            return desc

    # === NL_CK: 距離別着回数（詳細パターン） ===
    # 芝の距離別：Siba1200IkaChaku, Siba1201_1400Chaku, Siba2801OverChaku等
    siba_dist = re.match(r'Siba(\d+)(Ika|Over|_\d+)?Chaku', col)
    if siba_dist:
        dist = siba_dist.group(1)
        suffix = siba_dist.group(2) or ""
        if suffix == "Ika":
            return f"芝{dist}m以下着回数"
        if suffix == "Over":
            return f"芝{dist}m以上着回数"
        if suffix.startswith("_"):
            return f"芝{dist}〜{suffix[1:]}m着回数"
        return f"芝{dist}m着回数"

    # ダートの距離別：Dirt1000IkaChaku, Dirt1001_1300Chaku, Dirt2801OverChaku等
    dirt_dist = re.match(r'Dirt(\d+)(Ika|Over|_\d+)?Chaku', col)
    if dirt_dist:
        dist = dirt_dist.group(1)
        suffix = dirt_dist.group(2) or ""
        if suffix == "Ika":
            return f"ダート{dist}m以下着回数"
        if suffix == "Over":
            return f"ダート{dist}m以上着回数"
        if suffix.startswith("_"):
            return f"ダート{dist}〜{suffix[1:]}m着回数"
        return f"ダート{dist}m着回数"

    # 障害の距離別
    syogai_dist = re.match(r'Syogai(\d+)(Ika|Over|_\d+)?Chaku', col)
    if syogai_dist:
        dist = syogai_dist.group(1)
        suffix = syogai_dist.group(2) or ""
        if suffix == "Ika":
            return f"障害{dist}m以下着回数"
        if suffix == "Over":
            return f"障害{dist}m以上着回数"
        if suffix.startswith("_"):
            return f"障害{dist}〜{suffix[1:]}m着回数"
        return f"障害{dist}m着回数"

    # === NL_CK: 競馬場別着回数（SapporoSibaChaku等） ===
    jyo_track_patterns = [
        (r'Sapporo(Siba|Dirt|Syogai)Chaku', "札幌"),
        (r'Hakodate(Siba|Dirt|Syogai)Chaku', "函館"),
        (r'Fukushima(Siba|Dirt|Syogai)Chaku', "福島"),
        (r'Niigata(Siba|Dirt|Syogai)Chaku', "新潟"),
        (r'Tokyo(Siba|Dirt|Syogai)Chaku', "東京"),
        (r'Nakayama(Siba|Dirt|Syogai)Chaku', "中山"),
        (r'Chukyo(Siba|Dirt|Syogai)Chaku', "中京"),
        (r'Kyoto(Siba|Dirt|Syogai)Chaku', "京都"),
        (r'Hanshin(Siba|Dirt|Syogai)Chaku', "阪神"),
        (r'Kokura(Siba|Dirt|Syogai)Chaku', "小倉"),
    ]
    for pattern, jyo_name in jyo_track_patterns:
        match = re.match(pattern, col)
        if match:
            track = match.group(1)
            track_map = {"Siba": "芝", "Dirt": "ダート", "Syogai": "障害"}
            return f"{jyo_name}{track_map.get(track, track)}着回数"

    # === NL_CH: 賞金・着度数詳細（H=平地, S=障害） ===
    ch_patterns = [
        ("HonSyokinH", "本賞金・平地（単位：千円）"),
        ("HonSyokinS", "本賞金・障害（単位：千円）"),
        ("FukaSyokinH", "付加賞金・平地（単位：千円）"),
        ("FukaSyokinS", "付加賞金・障害（単位：千円）"),
        ("ChakuKaisuH", "着回数・平地"),
        ("ChakuKaisuS", "着回数・障害"),
    ]
    for pattern, desc in ch_patterns:
        if col == pattern:
            return desc

    # ChakuKaisu01H〜ChakuKaisu06H（1着〜着外）
    chaku_h_match = re.match(r'ChakuKaisu0?(\d+)([HS])', col)
    if chaku_h_match:
        place = int(chaku_h_match.group(1))
        track_type = "平地" if chaku_h_match.group(2) == "H" else "障害"
        place_names = {1: "1着", 2: "2着", 3: "3着", 4: "4着", 5: "5着", 6: "着外"}
        place_name = place_names.get(place, f"{place}着")
        return f"{track_type}{place_name}回数"

    # ChakuKaisuSiba1〜3, ChakuKaisuDirt1〜3（芝・ダート着順別）
    chaku_siba = re.match(r'ChakuKaisuSiba(\d+)', col)
    if chaku_siba:
        place = int(chaku_siba.group(1))
        place_names = {1: "1着", 2: "2着", 3: "3着"}
        place_name = place_names.get(place, f"{place}着")
        return f"芝{place_name}回数"

    chaku_dirt = re.match(r'ChakuKaisuDirt(\d+)', col)
    if chaku_dirt:
        place = int(chaku_dirt.group(1))
        place_names = {1: "1着", 2: "2着", 3: "3着"}
        place_name = place_names.get(place, f"{place}着")
        return f"ダート{place_name}回数"

    # === NL_HR/RT_HR: 払戻詳細（単体カラム） ===
    hr_patterns = [
        ("TanUmaban", "単勝馬番"),
        ("TanPay", "単勝払戻金（円）"),
        ("TanNinki", "単勝人気順"),
        ("FukuUmaban", "複勝馬番"),
        ("FukuPay", "複勝払戻金（円）"),
        ("FukuNinki", "複勝人気順"),
        ("WakuKumi", "枠連組番"),
        ("WakuPay", "枠連払戻金（円）"),
        ("WakuNinki", "枠連人気順"),
        ("UmarenPay", "馬連払戻金（円）"),
        ("WidePay", "ワイド払戻金（円）"),
        ("UmatanPay", "馬単払戻金（円）"),
        ("SanrenfukuPay", "3連複払戻金（円）"),
        ("SanrentanPay", "3連単払戻金（円）"),
        ("Yobi1", "予備1"),
        ("Yobi2", "予備2"),
        ("Yobi3", "予備3"),
    ]
    for pattern, desc in hr_patterns:
        if col == pattern:
            return desc

    # === NL_H1: 票数詳細（単体カラム） ===
    h1_patterns = [
        ("TanUmaban", "単勝馬番"),
        ("TanHyo", "単勝票数"),
        ("TanNinki", "単勝人気順"),
        ("FukuUmaban", "複勝馬番"),
        ("FukuHyo", "複勝票数"),
        ("FukuNinki", "複勝人気順"),
        ("WakuKumi", "枠連組番"),
        ("WakuHyo", "枠連票数"),
        ("WakuNinki", "枠連人気順"),
        ("TanHyoTotal", "単勝票数合計"),
        ("FukuHyoTotal", "複勝票数合計"),
        ("WakuHyoTotal", "枠連票数合計"),
        ("TanHenkanHyoTotal", "単勝返還票数合計"),
        ("FukuHenkanHyoTotal", "複勝返還票数合計"),
        ("WakuHenkanHyoTotal", "枠連返還票数合計"),
    ]
    for pattern, desc in h1_patterns:
        if col == pattern:
            return desc

    # === NL_O1: オッズ詳細（単体カラム） ===
    o1_patterns = [
        ("TanUmaban", "単勝馬番"),
        ("TanOdds", "単勝オッズ"),
        ("TanNinki", "単勝人気順"),
        ("FukuUmaban", "複勝馬番"),
        ("FukuOddsLow", "複勝オッズ（下限）"),
        ("FukuOddsHigh", "複勝オッズ（上限）"),
        ("FukuNinki", "複勝人気順"),
        ("WakurenOdds", "枠連オッズ"),
        ("WakurenNinki", "枠連人気順"),
        ("TanVote", "単勝票数"),
        ("FukuVote", "複勝票数"),
        ("WakurenVote", "枠連票数"),
    ]
    for pattern, desc in o1_patterns:
        if col == pattern:
            return desc

    # === NL_RA: ラップ・コーナー情報（単体カラム） ===
    ra_patterns = [
        ("LapTime", "ラップタイム"),
        ("Haron3F", "前半3ハロンタイム"),
        ("Haron4F", "前半4ハロンタイム"),
        ("Haron3L", "上がり3ハロンタイム"),
        ("Haron4L", "上がり4ハロンタイム"),
        ("Corner", "コーナー位置"),
        ("Syukaisu", "周回数"),
        ("TsukaJyuni", "通過順位"),
        ("Crlf", "改行コード"),
    ]
    for pattern, desc in ra_patterns:
        if col == pattern:
            return desc

    # === NL_TK: 特別レース情報 ===
    tk_patterns = [
        ("RaceMeiKubun", "レース名区分"),
        ("JyusyoKaiji", "重賞回次"),
        ("CourseKubun", "コース区分"),
        ("HandeHappyoDate", "ハンデ発表日"),
        ("RenbanNum", "連番番号"),
        ("Koryu", "交流区分"),
        ("RecordBreak", "レコード更新フラグ"),
    ]
    for pattern, desc in tk_patterns:
        if col == pattern:
            return desc

    # === NL_YS: 開催スケジュール重賞情報 ===
    ys_jyusyo = re.match(r'Jyusyo(\d+)(.+)', col)
    if ys_jyusyo:
        num = int(ys_jyusyo.group(1))
        field = ys_jyusyo.group(2)
        field_map = {
            "Nkai": "回次",
            "GradeCD": "グレードコード",
            "SyubetuCD": "競走種別コード",
            "KigoCD": "競走記号コード",
            "JyuryoCD": "重量種別コード",
            "Kyori": "距離",
            "TrackCD": "トラックコード",
            "TokuNum": "特別競走番号",
            "Hondai": "レース名",
        }
        if field in field_map:
            return f"重賞{num}の{field_map[field]}"

    # === NL_RC: レコード馬情報 ===
    rec_uma = re.match(r'RecUma(.+?)(\d+)', col)
    if rec_uma:
        field = rec_uma.group(1)
        num = int(rec_uma.group(2))
        field_map = {
            "KettoNum": "血統登録番号",
            "Bamei": "馬名",
            "SexCD": "性別コード",
            "Futan": "斤量",
        }
        if field in field_map:
            return f"レコード馬{num}の{field_map[field]}"

    # === NL_UM: 血統情報（Bameiのみ） ===
    ketto_bamei = re.match(r'Ketto3InfoBamei(\d+)', col)
    if ketto_bamei:
        gen_num = int(ketto_bamei.group(1))
        generations = ["父", "母", "父父", "父母", "母父", "母母",
                      "父父父", "父父母", "父母父", "父母母",
                      "母父父", "母父母", "母母父", "母母母"]
        gen_name = generations[gen_num - 1] if gen_num <= len(generations) else f"祖先{gen_num}"
        return f"{gen_name}の馬名"

    # === NL_KS: 最近重賞ID ===
    saikin_id = re.match(r'SaikinJyusyo(\d+)SaikinJyusyoid$', col)
    if saikin_id:
        num = int(saikin_id.group(1))
        return f"最近重賞{num}のレースID"

    # === NL_WE: 天候・馬場状態（2回目発表） ===
    we_patterns = [
        ("TenkoState2", "天候状態（2回目発表）"),
        ("SibaBabaState2", "芝馬場状態（2回目発表）"),
        ("DirtBabaState2", "ダート馬場状態（2回目発表）"),
    ]
    for pattern, desc in we_patterns:
        if col == pattern:
            return desc

    # === NL_WF: WIN5情報 ===
    wf_patterns = [
        ("HatubaiHyosu", "発売票数"),
        ("YukoHyosu", "有効票数"),
        ("HenkanFlag", "返還フラグ"),
        ("FuseirituFlag", "不成立フラグ"),
        ("TekichuNasiFlag", "的中なしフラグ"),
        ("CarryOverStart", "キャリーオーバー開始額"),
        ("CarryOverBalance", "キャリーオーバー残高"),
        ("PayJyushosiki", "払戻重勝式"),
        ("TekichuHyosu", "的中票数"),
    ]
    for pattern, desc in wf_patterns:
        if col == pattern:
            return desc

    # === NL_CK: その他詳細情報 ===
    ck_extra = [
        ("KyakusituKeiko", "客質傾向（脚質傾向）"),
        ("RegisteredRaceCount", "登録レース数"),
        ("KisyuResultsInfo", "騎手成績情報"),
        ("ChokyosiResultsInfo", "調教師成績情報"),
        ("BanusiResultsInfo", "馬主成績情報"),
        ("BreederResultsInfo", "生産者成績情報"),
    ]
    for pattern, desc in ck_extra:
        if col == pattern:
            return desc

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
