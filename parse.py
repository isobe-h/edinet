"""
 csvフォルダ下のcsvファイルを読み込み、下記の値を計算する。
 1. 正味運転資本(売上債権+棚卸資産-仕入債務)の前年との差額(BSより取得)
		以下の計算式で求める。しかし、文言が異なる
 売上債権(+)
		売掛金
	電子記録債権
	支払い手形
	契約資産
	その他
棚卸資産(+)
		商品および製品
	仕掛品
	原材料及び貯蔵品
	その他
仕入れ債務(-)
		電子記録債務
	支払い手形および買掛金

	未払い費用
	未払金
	電子記録債務
	契約負債
	預かり金
	その他
2. 有利子負債
短期借入金
短期社債
コマーシャルペーパー（CP）
リース債務（流動負債）
1年未満返済の長期借入金
1年未満償還の長期社債
1年未満償還の転換社債
1年未満償還の新株予約権付社債
長期借入金
社債
転換社債
新株予約権付転換社債
新株予約権付社債
リース債務（固定負債）
3. 現金及び預金(BSより取得)
4. 株式数（自社株を除く）
5. 売上高および営業利益
6. 来年度の売上高および営業利益予測
7. 有価証券(BSより取得)
8. 遊休資産
9. 設備投資
10. 減価償却(キャッシュフロー計算書より取得)

なお、同じ項目が複数回記載されている場合は、合計値を表す最後の行を取得する。
 """

import os
import re

import pandas as pd

# 現在のディレクトリ
current_dir = os.getcwd()

# csvフォルダのパス
csv_folder = os.path.join(current_dir, "csv")


def remove_unnecessary_columns(df):
    # dfから要素ID、コンテキストID,ユニットID列を削除
    # 相対年度の列が、'当期'　以外の行は削除
    df = df.drop(
        columns=["要素ID", "コンテキストID", "ユニットID", "単位", "期間・時点"]
    ).dropna(subset=["項目名"])
    # 相対年度の列が、terms_regexに一致する行のみを抽出
    df = df[df["相対年度"].str.contains(term_regex)]
    df = df[df["連結・個別"] != "個別"]
    df = df.drop(columns=["連結・個別"])
    # 項目名の列内の"、経営指標等"のを削除
    # 総資産額、経営指標等　→　総資産額
    df["項目名"] = df["項目名"].str.replace("、経営指標等", "")
    # # '項目名'が'所有株式数'から始まる行から、最初の'現金及び預金'の前の行までを削除
    # # 例：所有株式数（単元）－政府及び地方公共団体
    # start_index = df[df["項目名"].str.startswith("所有株式数", na=False)].index[0]
    # end_index = df[df["項目名"] == "現金及び預金"].index[0] - 1
    # df = df.drop(df.index[start_index:end_index])
    return df


term_regex = r"当期末?|前期末?"


def get_rows_by_item_name(df, item_name):
    item = df.loc[df["項目名"] == item_name, "値"]
    if len(item) > 1:
        return item.tolist()
    else:
        print(item_name + "が見つかりませんでした。")
        return [0, 0]


# 有利子負債合計を計算
# 長期借入金、短期借入金、社債、コマーシャルペーパー、リース債務、その他の有利子負債を合計する


def calc_interest_bearing_debt(df):
    long_term_loans = get_rows_by_item_name(df, "長期借入金")
    short_term_loans = get_rows_by_item_name(df, "短期借入金")
    corporate_bonds = get_rows_by_item_name(df, "社債")
    commercial_papers = get_rows_by_item_name(df, "コマーシャルペーパー")
    lease_obligations = get_rows_by_item_name(df, "リース債務")

    return (
        int(long_term_loans[1])
        + int(short_term_loans[1])
        + int(corporate_bonds[1])
        + int(commercial_papers[1])
        + int(lease_obligations[1])
    )


def get_net_working_capital(df):
    sales_receivables = get_rows_by_item_name(df, "売掛金")
    electronic_records_receivables = get_rows_by_item_name(df, "電子記録債権、流動資産")
    receivable_notes = get_rows_by_item_name(df, "受取手形")
    contract_assets = get_rows_by_item_name(df, "契約資産")
    other_current_assets = get_rows_by_item_name(df, "その他、流動資産")

    inventories = get_rows_by_item_name(df, "商品及び製品")
    work_in_process = get_rows_by_item_name(df, "仕掛品")
    raw_materials = get_rows_by_item_name(df, "原材料及び貯蔵品")
    other_current_liabilities = get_rows_by_item_name(df, "その他、流動負債")

    trade_payables = get_rows_by_item_name(df, "支払手形及び買掛金")
    unpaid_expenses = get_rows_by_item_name(df, "未払費用")
    unpaid_money = get_rows_by_item_name(df, "未払金")
    electronic_records_debt = get_rows_by_item_name(df, "電子記録債務、流動負債")
    contract_liabilities = get_rows_by_item_name(df, "契約負債")

    return [
        {
            "売掛金": sales_receivables[0],
            "電子記録債権": electronic_records_receivables[0],
            "受取手形": receivable_notes[0],
            "契約資産": contract_assets[0],
            "その他、流動資産": other_current_assets[0],
            "商品及び製品": inventories[0],
            "仕掛品": work_in_process[0],
            "原材料及び貯蔵品": raw_materials[0],
            "支払手形及び買掛金": trade_payables[0],
            "未払い費用": unpaid_expenses[0],
            "未払金": unpaid_money[0],
            "電子記録債務": electronic_records_debt[0],
            "契約負債": contract_liabilities[0],
            "その他、流動負債": other_current_liabilities[0],
        },
        {
            "売掛金": sales_receivables[1],
            "電子記録債権": electronic_records_receivables[1],
            "支払手形": receivable_notes[1],
            "契約資産": contract_assets[1],
            "その他、流動資産": other_current_assets[1],
            "商品及び製品": inventories[1],
            "仕掛品": work_in_process[1],
            "原材料及び貯蔵品": raw_materials[1],
            "支払手形及び買掛金": trade_payables[1],
            "未払い費用": unpaid_expenses[1],
            "未払金": unpaid_money[1],
            "電子記録債務": electronic_records_debt[1],
            "契約負債": contract_liabilities[1],
            "その他、流動負債": other_current_liabilities[1],
        },
    ]


def extract_values(df):
    bs = df.loc[df["項目名"] == "連結貸借対照表 [テキストブロック]", "値"].iloc[0]

    # 現金及び預金の取得
    cash_and_deposits = df.loc[df["項目名"] == "現金及び預金", "値"].iloc[-1]
    # 発行済み株式数（自社株を除く）の取得
    shares_outstanding = int(
        df.loc[df["項目名"] == "発行済株式総数（普通株式）", "値"].iloc[-1]
    ) - int(df.loc[df["項目名"] == "自己株式", "値"].iloc[-1])

    # 売上高および営業利益の取得
    # 相対年度の列が、'当期'、'前期'の売り上げと営業利益を抽出
    previous_revenue = df.loc[
        (df["項目名"] == "売上高") & (df["相対年度"] == "前期"), "値"
    ].iloc[-1]
    previous_operating_profit = df.loc[
        (df["項目名"] == "営業利益又は営業損失（△）") & (df["相対年度"] == "前期"),
        "値",
    ].iloc[-1]
    revenue = df.loc[
        (df["項目名"] == "売上高") & (df["相対年度"] == "当期"), "値"
    ].iloc[-1]
    operating_profit = df.loc[
        (df["項目名"] == "営業利益又は営業損失（△）") & (df["相対年度"] == "当期"),
        "値",
    ].iloc[-1]

    # 変数bsの中に'投資有価証券'があれば、続く数字部分のみを取得
    # 連結貸借対照表 [テキストブロック],当期,"①【連結貸借対照表】  (単位：百万円) 前連結会計年度(2022年３月31日)当連結会計年度(2023年３月31日)資産の部  流動資産  現金及び預金21,16522,458受取手形1,4181,664売掛金7,6389,514電子記録債権3,9535,812商品及び製品912943仕掛品1,6982,008原材料及び貯蔵品9181,771その他347435貸倒引当金△2△3流動資産合計38,05044,605固定資産  有形固定資産  建物及び構築物（純額）※１ 12,452※１ 11,416機械装置及び運搬具（純額）※１ 2,258※１ 2,343土地4,7734,614建設仮勘定5031,867その他（純額）※１ 285※１ 883有形固定資産合計20,27221,124無形固定資産  ソフトウエア203216電話加入権1312その他612無形固定資産合計222242投資その他の資産  投資有価証券※２ 5,490※２ 5,693退職給付に係る資産369433繰延税金資産129122その他※２ 476289貸倒引当金△18△18投資その他の資産合計6,4466,520固定資産合計26,94127,886資産合計64,99172,492    (単位：百万円) 前連結会計年度(2022年３月31日)当連結会計年度(2023年３月31日)負債の部  流動負債  支払手形及び買掛金3,4343,189電子記録債務293278短期借入金2501,250未払金1,1091,442未払法人税等2,9742,321賞与引当金856958資産除去債務117－その他1,0781,052流動負債合計10,11310,492固定負債  長期借入金100100繰延税金負債135158退職給付に係る負債1,5961,556資産除去債務158164その他228652固定負債合計2,2192,631負債合計12,33313,124純資産の部  株主資本  資本金4,9664,966資本剰余金5,2085,222利益剰余金41,13748,300自己株式△1,572△2,562株主資本合計49,73955,927その他の包括利益累計額  その他有価証券評価差額金2,3812,317為替換算調整勘定4681,020退職給付に係る調整累計額68102その他の包括利益累計額合計2,9193,441純資産合計52,65859,368負債純資産合計64,99172,492"
    # の場合、5,693を取得する。
    securities = "0"
    match = re.search(r"投資有価証券※２\s*\d+,\d+※２\s*(\d+,\d+)", bs)
    if match:
        securities = match.group(1).replace(",", "")  # カンマを削除

    # 項目名の中に、(単位：百万円）があれば、100万、(単位：千円）があれば、1000万とする
    money_unit = 1000000 if "(単位：百万円）" in bs else 1000

    # # 遊休資産の取得（ない場合は0）
    # idle_assets = (
    #     df.loc[df["項目名"] == "遊休資産", "値"].iloc[-1]
    #     if len(df.loc[df["項目名"] == "遊休資産", "値"]) > 0
    #     else 0
    # )

    # 設備投資があれば、その値を取得、なければ0
    capital_expenditure = df.loc[df["項目名"] == "設備投資額、設備投資等の概要", "値"]
    if len(capital_expenditure) > 0:
        capital_expenditure = capital_expenditure.iloc[-1]
    else:
        capital_expenditure = "0"
        print("設備投資が見つかりませんでした。")

    # 減価償却の取得
    depreciation = df.loc[df["項目名"] == "減価償却費、セグメント情報", "値"]
    if len(depreciation) > 0:
        depreciation = depreciation.iloc[-1]
    else:
        depreciation = "0"
        print("減価償却費が見つかりませんでした。")

    net_working_capital = get_net_working_capital(df)
    print(net_working_capital[0])
    print(net_working_capital[1])

    interest_bearing_debt = calc_interest_bearing_debt(df)
    print("有利子負債:", interest_bearing_debt, "円")
    # 全ての値をprint()で表示
    print("売上高:", revenue + "円")
    print("営業利益:", operating_profit + "円")
    print("前年の売上高:", previous_revenue + "円")
    print("前年の営業利益:", previous_operating_profit + "円")
    print("現金及び預金:", cash_and_deposits + "円")
    print("発行済み株式数（自社株を除く）:", str(shares_outstanding) + "株")
    print("投資有価証券:", str(int(securities) * money_unit) + "円")
    print("設備投資:", capital_expenditure + "円")
    print("減価償却費:", depreciation + "円")
    # print("正味運転資本の前年との差額:", str(result["正味運転資本"]) + "円")


# 計算結果を表示
# print(f"正味運転資本の前年との差額: {calc_net_working_capital(df):.2f}{money_unit}")
# print(f"有利子負債: {calc_interest_bearing_debt(df):.2f}{money_unit}")
# print(f"現金及び預金: {cash_and_deposits:.2f}{money_unit}")
# print(f"発行済み株式数（自社株を除く）: {shares_outstanding:.2f}株")
# print(f"売上高: {revenue:.2f}{money_unit}")
# print(f"営業利益: {operating_profit:.2f}{money_unit}")
# print(f"有価証券: {securities:.2f}{money_unit}")
# print(f"設備投資: {capital_expenditure:.2f}{money_unit}")
# print(f"減価償却: {depreciation:.2f}{money_unit}")
df = None
if __name__ == "__main__":
    df = pd.read_csv(
        os.path.join(csv_folder, "S100R0HJ_日本ピラー工業株式会社.csv"),
        encoding="utf-8",
    )
    df = remove_unnecessary_columns(df)
    df.to_csv(
        os.path.join(csv_folder, "S100R0HJ_日本ピラー工業株式会社_整形済み.csv"),
        index=False,
    )

    # csvファイルを読み込む
    df = pd.read_csv(
        os.path.join(csv_folder, "S100R0HJ_日本ピラー工業株式会社_整形済み.csv"),
        encoding="utf-8",
    )

    extract_values(df)

# 流動資産・流動負債を売上債権・棚卸資産・仕入債務に分類する関数
# データ例)"①【連結貸借対照表】  (単位：百万円) 前連結会計年度(2022年３月31日)当連結会計年度(2023年３月31日)資産の部  流動資産  現金及び預金21,16522,458受取手形1,4181,664売掛金7,6389,514電子記録債権3,9535,812商品及び製品912943仕掛品1,6982,008原材料及び貯蔵品9181,771その他347435貸倒引当金△2△3流動資産合計38,05044,605固定資産  有形固定資産  建物及び構築物（純額）※１ 12,452※１ 11,416機械装置及び運搬具（純額）※１ 2,258※１ 2,343土地4,7734,614建設仮勘定5031,867その他（純額）※１ 285※１ 883有形固定資産合計20,27221,124無形固定資産  ソフトウエア203216電話加入権1312その他612無形固定資産合計222242投資その他の資産  投資有価証券※２ 5,490※２ 5,693退職給付に係る資産369433繰延税金資産129122その他※２ 476289貸倒引当金△18△18投資その他の資産合計6,4466,520固定資産合計26,94127,886資産合計64,99172,492    (単位：百万円) 前連結会計年度(2022年３月31日)当連結会計年度(2023年３月31日)負債の部  流動負債  支払手形及び買掛金3,4343,189電子記録債務293278短期借入金2501,250未払金1,1091,442未払法人税等2,9742,321賞与引当金856958資産除去債務117－その他1,0781,052流動負債合計10,11310,492固定負債  長期借入金100100繰延税金負債135158退職給付に係る負債1,5961,556資産除去債務158164その他228652固定負債合計2,2192,631負債合計12,33313,124純資産の部  株主資本  資本金4,9664,966資本剰余金5,2085,222利益剰余金41,13748,300自己株式△1,572△2,562株主資本合計49,73955,927その他の包括利益累計額  その他有価証券評価差額金2,3812,317為替換算調整勘定4681,020退職給付に係る調整累計額68102その他の包括利益累計額合計2,9193,441純資産合計52,65859,368負債純資産合計64,99172,492"
