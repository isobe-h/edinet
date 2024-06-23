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

import re

import pandas as pd

term_regex = r"当期末?|前期末?"


def get_last_value(df, item_name, term=None):
    """
    指定された項目名から最後の値を取得します。
    """
    if item_name in df["項目名"].values:
        if term:
            return df.loc[
                (df["項目名"] == item_name) & (df["相対年度"].str.contains(term)),
                "値",
            ].iloc[-1]
        else:
            return df.loc[df["項目名"] == item_name, "値"].iloc[-1]
    else:
        return 0


def calc_interest_bearing_debt(df, term=None):
    long_term_loans = get_last_value(df, "長期借入金", "当期末")
    short_term_loans = get_last_value(df, "短期借入金", "当期末")
    corporate_bonds = get_last_value(df, "社債", "当期末")
    commercial_papers = get_last_value(df, "コマーシャルペーパー", "当期末")
    lease_obligations = get_last_value(df, "リース債務", "当期末")
    sum = (
        int(long_term_loans)
        + int(short_term_loans)
        + int(corporate_bonds)
        + int(commercial_papers)
        + int(lease_obligations)
    )

    return {
        "長期借入金": long_term_loans,
        "短期借入金": short_term_loans,
        "社債": corporate_bonds,
        "コマーシャルペーパー": commercial_papers,
        "リース債務": lease_obligations,
        "合計": sum,
    }


def get_net_working_capital(df):
    sales_receivables = get_last_value(df, "売掛金", "当期")
    electronic_records_receivables = get_last_value(
        df, "電子記録債権、流動資産", "当期"
    )
    receivable_notes = get_last_value(df, "受取手形", "当期")
    contract_assets = get_last_value(df, "契約資産", "当期")
    other_current_assets = get_last_value(df, "その他、流動資産", "当期")

    inventories = get_last_value(df, "商品及び製品", "当期")
    work_in_process = get_last_value(df, "仕掛品", "当期")
    raw_materials = get_last_value(df, "原材料及び貯蔵品", "当期")
    other_current_liabilities = get_last_value(df, "その他、流動負債", "当期")

    trade_payables = get_last_value(df, "支払手形及び買掛金", "当期")
    unpaid_expenses = get_last_value(df, "未払費用", "当期")
    unpaid_money = get_last_value(df, "未払金", "当期")
    electronic_records_debt = get_last_value(df, "電子記録債務、流動負債", "当期")
    contract_liabilities = get_last_value(df, "契約負債", "当期")

    sales_receivables_last_year = get_last_value(df, "売掛金", "前期")
    electronic_records_receivables_last_year = get_last_value(
        df, "電子記録債権、流動資産", "前期"
    )
    receivable_notes_last_year = get_last_value(df, "受取手形", "前期")
    contract_assets_last_year = get_last_value(df, "契約資産", "前期")
    other_current_assets_last_year = get_last_value(df, "その他、流動資産", "前期")

    inventories_last_year = get_last_value(df, "商品及び製品", "前期")
    work_in_process_last_year = get_last_value(df, "仕掛品", "前期")
    raw_materials_last_year = get_last_value(df, "原材料及び貯蔵品", "前期")
    other_current_liabilities_last_year = get_last_value(df, "その他、流動負債", "前期")

    trade_payables_last_year = get_last_value(df, "支払手形及び買掛金", "前期")
    unpaid_expenses_last_year = get_last_value(df, "未払費用", "前期")
    unpaid_money_last_year = get_last_value(df, "未払金", "前期")
    electronic_records_debt_last_year = get_last_value(
        df, "電子記録債務、流動負債", "前期"
    )
    contract_liabilities_last_year = get_last_value(df, "契約負債", "前期")

    return [
        {
            "売掛金": sales_receivables,
            "電子記録債権": electronic_records_receivables,
            "受取手形": receivable_notes,
            "契約資産": contract_assets,
            "その他、流動資産": other_current_assets,
            "商品及び製品": inventories,
            "仕掛品": work_in_process,
            "原材料及び貯蔵品": raw_materials,
            "支払手形及び買掛金": trade_payables,
            "未払い費用": unpaid_expenses,
            "未払金": unpaid_money,
            "電子記録債務": electronic_records_debt,
            "契約負債": contract_liabilities,
            "その他、流動負債": other_current_liabilities,
        },
        {
            "売掛金": sales_receivables_last_year,
            "電子記録債権": electronic_records_receivables_last_year,
            "受取手形": receivable_notes_last_year,
            "契約資産": contract_assets_last_year,
            "その他、流動資産": other_current_assets_last_year,
            "商品及び製品": inventories_last_year,
            "仕掛品": work_in_process_last_year,
            "原材料及び貯蔵品": raw_materials_last_year,
            "支払手形及び買掛金": trade_payables_last_year,
            "未払い費用": unpaid_expenses_last_year,
            "未払金": unpaid_money_last_year,
            "電子記録債務": electronic_records_debt_last_year,
            "契約負債": contract_liabilities_last_year,
            "その他、流動負債": other_current_liabilities_last_year,
        },
    ]


def parse_balance_sheet_text(bs):
    """
    連結貸借対照表のテキストブロックから、投資有価証券と通貨単位を解析します。
    """
    securities = 0
    match = re.search(r"投資有価証券※２\s*\d+,\d+※２\s*(\d+,\d+)", bs)
    if match:
        securities = int(match.group(1).replace(",", ""))
    money_unit = 1000000 if "(単位：百万円）" in bs else 1000
    print(securities, money_unit)
    return {"有価証券": securities, "単位": money_unit}


def export_to_csv(data, path):
    """
    辞書形式のデータを受け取り、CSVファイルとしてエクスポートします。
    """
    df = pd.DataFrame(list(data.items()), columns=["項目", "値"])
    df.to_csv(path, index=False, encoding="shift-jis")


def extract_and_process_data(df):

    bs = df.loc[df["項目名"] == "連結貸借対照表 [テキストブロック]", "値"].iloc[0]
    revenue = get_last_value(df, "売上高", "当期")
    operating_profit = get_last_value(df, "営業利益又は営業損失（△）", "当期")
    nopat = int(operating_profit) * 0.7
    depreciation = get_last_value(df, "減価償却費、セグメント情報", "当期")
    capital_expenditure = get_last_value(df, "設備投資額、設備投資等の概要", "当期")
    fcf = nopat - int(capital_expenditure) + int(depreciation)

    revenue_last_year = get_last_value(df, "売上高", "前期")
    operating_profit_last_year = get_last_value(df, "営業利益又は営業損失（△）", "前期")
    nopat_last_year = int(operating_profit_last_year) * 0.7
    depreciation_last_year = get_last_value(df, "減価償却費、セグメント情報", "前期")

    others = {
        "現金及び預金": get_last_value(df, "現金及び預金"),
        "発行済み株式数（自社株を除く）": int(
            get_last_value(df, "発行済株式総数（普通株式）")
        )
        - int(get_last_value(df, "自己株式")),
    }
    interest_bearing_debt = calc_interest_bearing_debt(df)

    net_working_capital = get_net_working_capital(df)
    securities_and_money_unit = parse_balance_sheet_text(bs)
    results = {
        "単位": securities_and_money_unit.get("単位"),
        "項目": ["2023", "2024"],
        "売上高": [revenue_last_year, revenue],
        "営業利益": [operating_profit_last_year, operating_profit],
        "NOPAT": [nopat_last_year, nopat],
        "減価償却": [depreciation_last_year, depreciation],
        "設備投資": [capital_expenditure],
        "FCF": [fcf],
        "正味運転資本": "",
        "当期": net_working_capital[0],
        "前期": net_working_capital[1],
        "有価証券": securities_and_money_unit.get("有価証券"),
        "純有利子負債": interest_bearing_debt,
        "その他": others,
    }

    # 辞書内の値を整形
    for key, value in results.items():
        results[key] = format_dict_values(value)

    # CSVに出力
    export_to_csv(results, "financial_results.csv")


def format_dict_values(data):
    if isinstance(data, dict):
        # 辞書のキーと値をカンマ区切りで整形
        return ", ".join([f"{key}: {value}" for key, value in data.items()])
    elif isinstance(data, list):
        # リストの要素をカンマ区切りで整形
        return ", ".join(map(str, data))


def parse_csv(path: str):
    df = pd.read_csv(path)
    result = extract_and_process_data(df)
    return result


if __name__ == "__main__":
    parse_csv(
        "/Users/alucard/edinetapi/processed_csv/ｓａｎｔｅｃ　Ｈｏｌｄｉｎｇｓ株式会社_S100TOES_有価証券報告書－第45期20230401－20240331.csv"
    )
