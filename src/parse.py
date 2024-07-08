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

import csv

import pandas as pd

from type import (
    FinancialSumary,
    InterestBearingDebt,
    Inventory,
    NetOperatingCapital,
    PurchaseDebt,
    SalesReceivables,
    japanese_dict,
)

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


def calc_interest_bearing_debt(df, term=None) -> InterestBearingDebt:
    long_term_debt = get_last_value(df, "長期借入金", "当期末")
    short_term_debt = get_last_value(df, "短期借入金", "当期末")
    long_term_debt_within_1year = get_last_value(
        df, "１年内返済予定の長期借入金", "当期末"
    )
    corporate_bonds = get_last_value(df, "社債", "当期末")
    commercial_papers = get_last_value(df, "コマーシャルペーパー", "当期末")
    lease_obligations = get_last_value(df, "リース債務", "当期末")
    sum = (
        int(long_term_debt)
        + int(short_term_debt)
        + int(corporate_bonds)
        + int(commercial_papers)
        + int(lease_obligations)
        + int(long_term_debt_within_1year)
    )

    interest_bearing_debt: InterestBearingDebt = {
        "short_term_debt": int(short_term_debt) + int(long_term_debt_within_1year),
        "long_term_debt": long_term_debt,
        "corporate_bonds": corporate_bonds,
        "commercial_papers": commercial_papers,
        "lease_obligations": lease_obligations,
        "interest_bearing_debt_sum": sum,
    }
    return interest_bearing_debt


def get_net_working_capital(df) -> NetOperatingCapital:
    sales_receivables: SalesReceivables = {
        "accounts_receivables": [
            get_last_value(df, "売掛金", "前期"),
            get_last_value(df, "売掛金", "当期"),
        ],
        "electronic_records_receivables": [
            get_last_value(df, "電子記録債務", "前期"),
            get_last_value(df, "電子記録債務", "当期"),
        ],
        "receivable_notes": [
            get_last_value(df, "受取手形", "前期"),
            get_last_value(df, "受取手形", "当期"),
        ],
        "contract_assets": [
            get_last_value(df, "契約資産", "前期"),
            get_last_value(df, "契約資産", "当期"),
        ],
        "other_current_assets": [
            get_last_value(df, "その他、流動資産", "前期"),
            get_last_value(df, "その他、流動資産", "当期"),
        ],
    }
    inventories: Inventory = {
        "merchandise_or_products": [
            get_last_value(df, "商品及び製品", "前期"),
            get_last_value(df, "商品及び製品", "当期"),
        ],
        "work_in_process": [
            get_last_value(df, "仕掛品", "前期"),
            get_last_value(df, "仕掛品", "当期"),
        ],
        "raw_materials": [
            get_last_value(df, "原材料及び貯蔵品", "前期"),
            get_last_value(df, "原材料及び貯蔵品", "当期"),
        ],
    }
    purchase_debt: PurchaseDebt = {
        "trade_payables": [
            get_last_value(df, "支払手形及び買掛金", "前期"),
            get_last_value(df, "支払手形及び買掛金", "当期"),
        ],
        "unpaid_expenses": [
            get_last_value(df, "未払費用", "前期"),
            get_last_value(df, "未払費用", "当期"),
        ],
        "unpaid_money": [
            get_last_value(df, "未払金", "前期"),
            get_last_value(df, "未払金", "当期"),
        ],
        "electronic_records_debt": [
            get_last_value(df, "電子記録債務", "前期"),
            get_last_value(df, "電子記録債務", "当期"),
        ],
        "contract_liabilities": [
            get_last_value(df, "契約負債", "前期"),
            get_last_value(df, "契約負債", "当期"),
        ],
        "other_current_liabilities": [
            get_last_value(df, "その他、流動負債", "前期"),
            get_last_value(df, "その他、流動負債", "当期"),
        ],
    }

    net_working_capital: NetOperatingCapital = {
        "sales_receivables": sales_receivables,
        "inventories": inventories,
        "purchase_debt": purchase_debt,
        "sum_of_net_operating_capitals": [
            sum([int(value[0]) for value in sales_receivables.values()])
            + sum([int(value[0]) for value in inventories.values()])
            - sum([int(value[0]) for value in purchase_debt.values()]),
            sum([int(value[1]) for value in sales_receivables.values()])
            + sum([int(value[1]) for value in inventories.values()])
            - sum([int(value[1]) for value in purchase_debt.values()]),
        ],
    }
    return net_working_capital


def get_idle_assets(df):

    return {
        "投資有価証券": get_last_value(df, "投資有価証券", "当期"),
        "現金及び預金": get_last_value(df, "現金及び預金", "当期"),
    }


def get_money_unit(bs: str) -> int:
    if " (単位：千円) " in bs:
        return 1000
    elif " (単位：百万円) " in bs:
        return 1000000
    else:
        raise Exception("単位が取得できませんでした")


def get_financial_summary(df) -> FinancialSumary:
    revenues = [
        get_last_value(df, "売上高", "前期"),
        get_last_value(df, "売上高", "当期"),
    ]
    operating_profits = [
        get_last_value(df, "営業利益又は営業損失（△）", "前期"),
        get_last_value(df, "営業利益又は営業損失（△）", "当期"),
    ]
    nopat = [int(operating_profits[0]) * 0.7, int(operating_profits[1]) * 0.7]
    return {
        "revenues": revenues,
        "operating_profits": operating_profits,
        "nopat": nopat,
        "deprecations": [
            get_last_value(df, "減価償却費、セグメント情報", "前期"),
            get_last_value(df, "減価償却費、セグメント情報", "当期"),
        ],
        "capital_expenditure": [
            get_last_value(df, "設備投資額、設備投資等の概要", "当期"),
        ],
    }


def extract_and_process_data(df):
    bs: str = df.loc[df["項目名"] == "連結貸借対照表 [テキストブロック]", "値"].iloc[0]

    financial_summary = get_financial_summary(df)
    interest_bearing_debt = calc_interest_bearing_debt(df)
    net_working_capital = get_net_working_capital(df)
    money_unit = get_money_unit(bs)
    idle_assets = get_idle_assets(df)
    number_of_stock = int(get_last_value(df, "発行済株式総数（普通株式）")) - int(
        get_last_value(df, "自己名義所有株式数（株）、自己株式等")
    )
    fcf = (
        int(financial_summary["nopat"][0])
        - int(financial_summary["capital_expenditure"][0])
        + int(financial_summary["deprecations"][0])
    )
    results = {
        "単位": str(money_unit) + "円",
        **financial_summary,
        "営業利益成長率": [
            calculate_growth_rate(financial_summary["operating_profits"])
        ],
        "FCF": [fcf],
        **net_working_capital,
        "正味運転資本の増減": net_working_capital["sum_of_net_operating_capitals"][1]
        - net_working_capital["sum_of_net_operating_capitals"][0],
        "株式数": number_of_stock,
        **idle_assets,
        **interest_bearing_debt,
        "純有利子負債": int(idle_assets["現金及び預金"])
        - interest_bearing_debt["interest_bearing_debt_sum"],
    }
    export_to_csv(results, "results.csv")


def calculate_growth_rate(values):
    """Calculate growth rate between two periods"""
    if values[1] and values[0]:
        return round(((int(values[1]) - int(values[0])) / int(values[0])) * 100, 2)
    return 0


def export_to_csv(data, path):
    with open(path, "w", encoding="sjis", newline="") as file:
        writer = csv.writer(file)

        for key, values in data.items():
            # 日本語ラベルに変換、見つからない場合は元のキーを使用
            japanese_label = japanese_dict.get(key, key)

            if isinstance(values, dict):
                # 辞書型の場合、各サブキーに対して新たな行を作成
                for subkey, subvalues in values.items():
                    sub_japanese_label = japanese_dict.get(subkey, subkey)
                    # 値がリストであることを確認し、それぞれの要素を列として追加
                    if isinstance(subvalues, list):
                        writer.writerow(
                            [japanese_label, sub_japanese_label] + subvalues
                        )
                    else:
                        writer.writerow([japanese_label, sub_japanese_label, subvalues])
            else:
                # リストや単一の値の場合、通常通りに処理
                if isinstance(values, list):
                    writer.writerow([japanese_label] + list(map(str, values)))
                else:
                    writer.writerow([japanese_label, str(values)])


def format_dict_values(data):
    if isinstance(data, dict):
        # 辞書のキーと値をカンマ区切りで整形
        return ", ".join([f"{key}: {value}" for key, value in data.items()])
    elif isinstance(data, list):
        # リストの要素をカンマ区切りで整形
        return ", ".join(map(str, data))


if __name__ == "__main__":
    path = "/Users/alucard/edinetapi/processed_csv/ｓａｎｔｅｃ　Ｈｏｌｄｉｎｇｓ株式会社_S100TOES_有価証券報告書－第45期20230401－20240331.csv"
    df = pd.read_csv(path)
    result = extract_and_process_data(df)
