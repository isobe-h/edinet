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
TAX_RATE = 0.3
TAX_COEFFICIENT = 1 - TAX_RATE


def get_last_value(df, item_name, term=None) -> int:
    """
    指定された項目名から最後の値を取得します。
    """
    value = 0
    if item_name not in df["項目名"].values:
        return value
    if term:
        value = df.loc[
            (df["項目名"] == item_name) & (df["相対年度"].str.contains(term)),
            "値",
        ].iloc[-1]
    else:
        value = df.loc[df["項目名"] == item_name, "値"].iloc[-1]
    return int(value)


def calc_interest_bearing_debt(df, term=None) -> InterestBearingDebt:
    long_term_debt = get_last_value(df, "長期借入金", "当期末")
    short_term_debt = get_last_value(df, "短期借入金", "当期末")
    long_term_debt_within_1year = get_last_value(
        df, "１年内返済予定の長期借入金", "当期末"
    )
    corporate_bonds = get_last_value(df, "社債", "当期末")
    commercial_papers = get_last_value(df, "コマーシャルペーパー", "当期末")
    lease_obligations = get_last_value(df, "リース債務", "当期末")
    sum_current_period = sum(
        [
            long_term_debt,
            short_term_debt,
            corporate_bonds,
            commercial_papers,
            lease_obligations,
            long_term_debt_within_1year,
        ]
    )

    long_term_debt_last_period = get_last_value(df, "長期借入金", "前期末")
    short_term_debt_last_period = get_last_value(df, "短期借入金", "前期末")
    long_term_debt_within_1year_last_period = get_last_value(
        df, "１年内返済予定の長期借入金", "前期末"
    )
    corporate_bonds_last_period = get_last_value(df, "社債", "前期末")
    commercial_papers_last_period = get_last_value(df, "コマーシャルペーパー", "前期末")
    lease_obligations_last_period = get_last_value(df, "リース債務", "前期末")
    sum_last_period = sum(
        [
            long_term_debt_last_period,
            short_term_debt_last_period,
            corporate_bonds_last_period,
            commercial_papers_last_period,
            lease_obligations_last_period,
            long_term_debt_within_1year_last_period,
        ]
    )

    interest_bearing_debt: InterestBearingDebt = {
        "short_term_debt": [
            short_term_debt_last_period + long_term_debt_within_1year_last_period,
            short_term_debt + long_term_debt_within_1year,
        ],
        "long_term_debt": [long_term_debt_last_period, long_term_debt],
        "corporate_bonds": [corporate_bonds_last_period, corporate_bonds],
        "commercial_papers": [commercial_papers_last_period, commercial_papers],
        "lease_obligations": [lease_obligations_last_period, lease_obligations],
        "interest_bearing_debt_sum": [sum_last_period, sum_current_period],
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
        **sales_receivables,
        **inventories,
        **purchase_debt,
        "sum_of_net_operating_capitals": [
            sum([value[0] for value in sales_receivables.values()])
            + sum([value[0] for value in inventories.values()])
            - sum([value[0] for value in purchase_debt.values()]),
            sum([value[1] for value in sales_receivables.values()])
            + sum([value[1] for value in inventories.values()])
            - sum([value[1] for value in purchase_debt.values()]),
        ],
    }
    return net_working_capital


def get_idle_assets(df):

    return {
        "投資有価証券": [
            get_last_value(df, "投資有価証券", "前期"),
            get_last_value(df, "投資有価証券", "当期"),
        ],
        "現金及び預金": [
            get_last_value(df, "現金及び預金", "前期"),
            get_last_value(df, "現金及び預金", "当期"),
        ],
    }


def get_money_unit(bs: str) -> int:
    if " (単位：千円) " in bs:
        return 1000
    elif " (単位：百万円) " in bs:
        return 1000000
    else:
        raise Exception("単位が取得できませんでした")


# 実効税率を取得
def calculate_effective_tax_rate(
    tax: int, net_income_before_tax_current_period: int
) -> float:
    # 実効税率
    return round((tax / net_income_before_tax_current_period), 2)


def get_financial_summary(df) -> FinancialSumary:
    revenues = [
        get_last_value(df, "売上高", "前期"),
        get_last_value(df, "売上高", "当期"),
    ]
    operating_profits = [
        get_last_value(df, "営業利益又は営業損失（△）", "前期"),
        get_last_value(df, "営業利益又は営業損失（△）", "当期"),
    ]
    nopat = [
        float(operating_profits[0]) * TAX_COEFFICIENT,
        float(operating_profits[1]) * TAX_COEFFICIENT,
    ]
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


def calculate_roic(
    effective_tax_rates: tuple[float, float],
    operating_incomes: tuple[int, int],
    interest_bearing_debts: tuple[int, int],
):
    shareholders_equity = (
        get_last_value(df, "株主資本", "前期"),
        get_last_value(df, "株主資本", "当期"),
    )
    # 投下資本
    invested_capital = (
        shareholders_equity[0] + interest_bearing_debts[0],
        shareholders_equity[1] + interest_bearing_debts[1],
    )
    noplats = (
        float(operating_incomes[0]) * (1 - effective_tax_rates[0]),
        float(operating_incomes[1]) * (1 - effective_tax_rates[1]),
    )
    print(noplats[0] / invested_capital[0], noplats[1] / invested_capital[1])
    return [
        round(noplats[0] / invested_capital[0], 4) * 100,
        round(noplats[1] / invested_capital[1], 4) * 100,
    ]


def extract_and_process_data(df):
    bs: str = df.loc[df["項目名"] == "連結貸借対照表 [テキストブロック]", "値"].iloc[0]
    financial_summary = get_financial_summary(df)
    interest_bearing_debt = calc_interest_bearing_debt(df)
    net_working_capital = get_net_working_capital(df)
    money_unit = get_money_unit(bs)
    idle_assets = get_idle_assets(df)
    number_of_stock = get_last_value(df, "発行済株式総数（普通株式）") - get_last_value(
        df, "自己名義所有株式数（株）、自己株式等"
    )

    fcf = (
        financial_summary["nopat"][0]
        - financial_summary["capital_expenditure"][0]
        + financial_summary["deprecations"][0]
    )
    effective_tax_rates: tuple[float, float] = (
        calculate_effective_tax_rate(
            get_last_value(df, "法人税等", "前期"),
            get_last_value(df, "税引前当期純利益又は税引前当期純損失（△）", "前期"),
        ),
        calculate_effective_tax_rate(
            get_last_value(df, "法人税等", "当期"),
            get_last_value(df, "税引前当期純利益又は税引前当期純損失（△）", "当期"),
        ),
    )
    return {
        # "単位": str(money_unit),
        "期": ["前期", "当期"],
        **financial_summary,
        "営業利益成長率": [
            calculate_growth_rate(financial_summary["operating_profits"])
        ],
        "FCF": [fcf],
        "ROIC": calculate_roic(
            effective_tax_rates,
            financial_summary["operating_profits"],
            interest_bearing_debt["interest_bearing_debt_sum"],
        ),
        "": "",
        "正味運転資本": "",
        **net_working_capital,
        "正味運転資本の増減": net_working_capital["sum_of_net_operating_capitals"][1]
        - net_working_capital["sum_of_net_operating_capitals"][0],
        " ": "",
        "株式数(自社株控除後)": number_of_stock,
        **idle_assets,
        "有利子負債": "",
        **interest_bearing_debt,
        "純有利子負債": [
            idle_assets["現金及び預金"][0]
            - interest_bearing_debt["interest_bearing_debt_sum"][0],
            idle_assets["現金及び預金"][1]
            - interest_bearing_debt["interest_bearing_debt_sum"][1],
        ],
    }


def calculate_growth_rate(values) -> float:
    """Calculate growth rate between two periods"""
    if values[1] and values[0]:
        return round(((values[1] - values[0]) / values[0]) * 100, 2)
    return 0


def export_to_csv(data, path):
    # utf-8-sigにすることで、Excelで開いた際に文字化けを防ぐ
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
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
        return ", ".join(data)


if __name__ == "__main__":
    path = "/Users/alucard/edinetapi/processed_csv/ｓａｎｔｅｃ　Ｈｏｌｄｉｎｇｓ株式会社_S100TOES_有価証券報告書－第45期20230401－20240331.csv"
    df = pd.read_csv(path)
    result = extract_and_process_data(df)
    export_to_csv(result, "results.csv")


def parse_csv(path, filename):
    df = pd.read_csv(path, encoding="utf-8")
    result = extract_and_process_data(df)
    export_to_csv(result, filename)
