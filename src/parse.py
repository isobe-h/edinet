import csv
import os
import re

import pandas as pd

from calculate import (
    calculate_effective_tax_rate,
    calculate_growth_ratio,
    calculate_invested_capital,
    calculate_ratio,
    calculate_roic,
    calculate_weighted_average_cost,
)
from type import (
    FinancialSumary,
    InterestBearingDebt,
    NetOperatingCapital,
    japanese_dict,
)
from utilities import get_first_value, get_item_name, get_item_number_value

term_regex = r"当期末?|前期末?"
TAX_RATE = 0.3
TAX_COEFFICIENT = 1 - TAX_RATE
# 売上債権
sales_receivables_items = (
    "売掛金",
    "契約資産",
    "前渡金",
    "電子記録債権",
    "受取手形",
    "その他、流動資産",
)
# 棚卸資産
inventories_items = ["商品及び製品", "仕掛品", "原材料及び貯蔵品"]
# 仕入債務
purchase_debt_items = (
    "買掛金",
    "支払手形",
    "電子記録債務",
    "未払費用",
    "未払金",
    "契約負債",
    "前受金",
    "その他、流動負債",
)
# 有利子負債
interest_bearing_debt_items = (
    "短期借入金",
    "短期社債",
    "コマーシャルペーパー",
    "リース債務（流動負債）",
    "１年内返済予定の長期借入金",
    "長期借入金",
    "社債",
    "転換社債",
    "新株予約権付転換社債",
    "新株予約権付社債",
    "リース債務（固定負債）",
)


def calc_interest_bearing_debt(df) -> InterestBearingDebt:
    interest_bearing_debt_item_names = set(
        [
            get_item_name(df, x, "当期末")
            for x in interest_bearing_debt_items
            if get_item_name(df, x, "当期") != ""
        ]
    )
    print(interest_bearing_debt_item_names)
    interest_bearing_debt = {
        item_name: [
            get_item_number_value(df, item_name, "前期末"),
            get_item_number_value(df, item_name, "当期末"),
        ]
        for item_name in interest_bearing_debt_item_names
    }
    print(interest_bearing_debt)
    interest_bearing_debt["sum_of_interest_bearing_debt"] = [
        sum([value[0] for value in interest_bearing_debt.values()]),
        sum([value[1] for value in interest_bearing_debt.values()]),
    ]

    return interest_bearing_debt


def get_net_operating_capital(df) -> NetOperatingCapital:
    # 重複項目が発生するため、項目名からsetを取得
    sales_receivables_item_names = set(
        [
            get_item_name(df, x, "当期")
            for x in sales_receivables_items
            if get_item_name(df, x, "当期") != ""
        ]
    )
    inventories_item_names = set(
        [
            get_item_name(df, x, "当期")
            for x in inventories_items
            if get_item_name(df, x, "当期") != ""
        ]
    )
    purchase_debt_item_names = set(
        [
            get_item_name(df, x, "当期")
            for x in purchase_debt_items
            if get_item_name(df, x, "当期") != ""
        ]
    )
    sales_receivables = {
        item_name: [
            get_item_number_value(df, item_name, "前期"),
            get_item_number_value(df, item_name, "当期"),
        ]
        for item_name in sales_receivables_item_names
    }
    inventories = {
        item_name: [
            get_item_number_value(df, item_name, "前期"),
            get_item_number_value(df, item_name, "当期"),
        ]
        for item_name in inventories_item_names
    }
    purchase_debt = {
        item_name: [
            get_item_number_value(df, item_name, "前期"),
            get_item_number_value(df, item_name, "当期"),
        ]
        for item_name in purchase_debt_item_names
    }
    sum_of_sales_receivables = [
        sum([value[0] for value in sales_receivables.values()]),
        sum([value[1] for value in sales_receivables.values()]),
    ]
    sum_of_inventories = [
        sum([value[0] for value in inventories.values()]),
        sum([value[1] for value in inventories.values()]),
    ]
    sum_of_purchase_debt = [
        sum([value[0] for value in purchase_debt.values()]),
        sum([value[1] for value in purchase_debt.values()]),
    ]
    sums = [
        sum_of_inventories[0] + sum_of_sales_receivables[0] - sum_of_purchase_debt[0],
        sum_of_inventories[1] + sum_of_sales_receivables[1] - sum_of_purchase_debt[1],
    ]

    net_operating_capital: NetOperatingCapital = {
        # **sales_receivables,
        "sum_of_sales_receivables": sum_of_sales_receivables,
        # **inventories,
        "sum_of_inventories": sum_of_inventories,
        # **purchase_debt,
        "sum_of_purchase_debt": sum_of_purchase_debt,
        "sum_of_net_operating_capitals": sums,
        "fluctuation_of_net_operating_capitals": ["-", sums[1] - sums[0]],
    }
    return net_operating_capital


def get_idle_assets(df):

    return {
        "投資有価証券": [
            get_item_number_value(df, "投資有価証券", "前期"),
            get_item_number_value(df, "投資有価証券", "当期"),
        ],
        "現金及び預金": [
            get_item_number_value(df, "現金及び預金", "前期"),
            get_item_number_value(df, "現金及び預金", "当期"),
        ],
    }


def get_money_unit(bs: str) -> int:
    if "単位：千円" in bs:
        return 1000
    elif "単位：百万円 " in bs:
        return 1000000
    else:
        raise Exception("単位が取得できませんでした")


def get_financial_summary(df) -> FinancialSumary:
    operating_profits = [
        get_item_number_value(df, "営業利益又は営業損失（△）", "前期"),
        get_item_number_value(df, "営業利益又は営業損失（△）", "当期"),
    ]
    nopat = [
        round(float(operating_profits[0]) * TAX_COEFFICIENT, 2),
        round(float(operating_profits[1]) * TAX_COEFFICIENT, 2),
    ]
    revenues = [
        get_item_number_value(df, "売上高", "前期"),
        get_item_number_value(df, "売上高", "当期"),
    ]
    # "売上原価
    cost_of_sales = [
        revenues[0]
        - get_item_number_value(df, "売上総利益又は売上総損失（△）", "前期"),
        revenues[1]
        - get_item_number_value(df, "売上総利益又は売上総損失（△）", "当期"),
    ]
    # 一般管理費及び販売費
    selling_general_and_administrative_expenses = [
        get_item_number_value(df, "販売費及び一般管理費", "前期"),
        get_item_number_value(df, "販売費及び一般管理費", "当期"),
    ]
    # 純利益
    net_income = [
        get_item_number_value(df, "当期純利益又は当期純損失（△）", "前期"),
        get_item_number_value(df, "当期純利益又は当期純損失（△）", "当期"),
    ]
    # 潜在株式調整後１株当たり当期純利益
    net_income_per_share_adjusted_for_potential_stock = [
        get_item_number_value(df, "潜在株式調整後1株当たり当期純利益", "前期"),
        get_item_number_value(df, "潜在株式調整後1株当たり当期純利益", "当期"),
    ]
    # 潜在株式がない場合
    if net_income_per_share_adjusted_for_potential_stock[0] == 0:
        net_income_per_share_adjusted_for_potential_stock = [
            get_item_number_value(
                df, "１株当たり当期純利益又は当期純損失（△）", "前期"
            ),
            get_item_number_value(
                df, "１株当たり当期純利益又は当期純損失（△）", "当期"
            ),
        ]
    # 総資産
    total_assets = [
        get_item_number_value(df, "総資産額", "前期"),
        get_item_number_value(df, "総資産額", "当期"),
    ]
    return {
        "revenues": revenues,
        "revenue_growth_rate": [
            "-",
            calculate_growth_ratio(revenues[0], revenues[1]),
        ],
        "cost_of_sales": cost_of_sales,
        "selling_general_and_administrative_expenses": selling_general_and_administrative_expenses,
        "operating_profits": operating_profits,
        "operating_profit_growth_rate": [
            "-",
            calculate_growth_ratio(
                operating_profits[0],
                operating_profits[1],
            ),
        ],
        "nopat": nopat,
        "deprecations": [
            get_item_number_value(
                df, "減価償却費、営業活動によるキャッシュ・フロー", "前期"
            ),
            get_item_number_value(
                df, "減価償却費、営業活動によるキャッシュ・フロー", "当期"
            ),
        ],
        "capital_expenditure": [
            "-",
            get_item_number_value(df, "設備投資額、設備投資等の概要", "当期"),
        ],
        "net_income": net_income,
        "net_income_per_share_adjusted_for_potential_stock": net_income_per_share_adjusted_for_potential_stock,
        "total_assets": total_assets,
    }


def extract_and_process_data(df, start_year, end_year):
    consolidated_bs_title = "連結貸借対照表 [テキストブロック]"
    bs_title = "貸借対照表 [テキストブロック]"
    consolidated_debt_detail_title = "借入金等明細表、連結財務諸表 [テキストブロック]"
    debt_detail_title = "借入金等明細表、財務諸表 [テキストブロック]"
    # 連結貸借対照表を探して、なければ単体貸借対照表を探す
    bs = get_first_value(df, consolidated_bs_title, "当期")
    if bs == "":
        bs = get_first_value(df, bs_title, "当期")
        # 見つからない場合はエラー
        if bs == "":
            raise Exception("貸借対照表が見つかりませんでした")

    # 借入金等明細表、連結財務諸表 [テキストブロック]を探して、なければ単体財務諸表を探す

    debt_detail = get_first_value(df, consolidated_debt_detail_title, "当期")
    if debt_detail == "":
        debt_detail = get_first_value(df, debt_detail_title, "当期")
    debt_rate = calculate_weighted_average_cost(debt_detail)
    financial_summary = get_financial_summary(df)
    interest_bearing_debt = calc_interest_bearing_debt(df)
    net_working_capital = get_net_operating_capital(df)
    # money_unit = get_money_unit(bs)
    idle_assets = get_idle_assets(df)
    number_of_stock = get_item_number_value(df, "発行済株式総数（普通株式）", "当期末")
    number_of_company_stock = get_item_number_value(
        df, "自己名義所有株式数（株）、自己株式等", "当期末"
    )

    fcf = (
        financial_summary["nopat"][1]
        - financial_summary["capital_expenditure"][1]
        + financial_summary["deprecations"][1]
        - net_working_capital["fluctuation_of_net_operating_capitals"][1]
    )

    effective_tax_rates = [
        calculate_effective_tax_rate(
            get_item_number_value(df, "法人税等", "前期"),
            get_item_number_value(
                df, "税引前当期純利益又は税引前当期純損失（△）", "前期"
            ),
        ),
        calculate_effective_tax_rate(
            get_item_number_value(df, "法人税等", "当期"),
            get_item_number_value(
                df, "税引前当期純利益又は税引前当期純損失（△）", "当期"
            ),
        ),
    ]
    noplats = (
        float(financial_summary["operating_incomes"][0]) * (1 - effective_tax_rates[0]),
        float(financial_summary["operating_incomes"][1]) * (1 - effective_tax_rates[1]),
    )
    shareholders_equity = [
        get_item_number_value(df, "株主資本", "前期"),
        get_item_number_value(df, "株主資本", "当期"),
    ]
    invested_capitals = calculate_invested_capital(
        shareholders_equity, interest_bearing_debt["sum_of_interest_bearing_debt"]
    )
    bps = [
        get_item_number_value(df, "１株当たり純資産額", "前期"),
        get_item_number_value(df, "１株当たり純資産額", "当期末"),
    ]
    tangible_fixed_assets = [
        get_item_number_value(df, "有形固定資産", "前期"),
        get_item_number_value(df, "有形固定資産", "当期"),
    ]
    net_trading_fixed_assets = [
        tangible_fixed_assets[0]
        - get_item_number_value(df, "減価償却累計額、その他、有形固定資産", "前期"),
        tangible_fixed_assets[1]
        - get_item_number_value(df, "減価償却累計額、その他、有形固定資産", "当期"),
    ]
    print(get_item_number_value(df, "有形固定資産", "前期"))
    print(get_item_number_value(df, "減価償却累計額、その他、有形固定資産", "前期"))
    print(get_item_number_value(df, "有形固定資産", "当期"))
    print(get_item_number_value(df, "減価償却累計額、その他、有形固定資産", "当期"))
    return {
        # "単位": str(money_unit),
        "年": [start_year, end_year],
        "実効税率": effective_tax_rates,
        **financial_summary,
        "FCF": ["-", fcf],
        "割引率": "",
        "正味運転資本": "",
        **net_working_capital,
        "有利子負債": "",
        **interest_bearing_debt,
        "純有利子負債": [
            idle_assets["現金及び預金"][0]
            - interest_bearing_debt["sum_of_interest_bearing_debt"][0],
            idle_assets["現金及び預金"][1]
            - interest_bearing_debt["sum_of_interest_bearing_debt"][1],
        ],
        "債権者コスト": ["-", debt_rate],
        "その他": "",
        "正味有形固定資産": net_trading_fixed_assets,
        "株主資本": shareholders_equity,
        "株式数(自社株控除後)": ["-", number_of_stock - number_of_company_stock],
        **idle_assets,
        "BPS": bps,
        "": "",
        "予測レシオ": "",
        "売上原価：売上原価/売上高": [
            "-",
            calculate_ratio(
                financial_summary["cost_of_sales"][1],
                financial_summary["revenues"][1],
            ),
        ],
        "販売費及び一般管理費：販売費及び一般管理費/売上高": [
            "-",
            calculate_ratio(
                get_item_number_value(df, "販売費及び一般管理費", "当期"),
                financial_summary["revenues"][1],
            ),
        ],
        "減価償却費：減価償却費(t)/正味有形固定資産(t-1)": [
            "-",
            calculate_ratio(
                financial_summary["deprecations"][1], net_trading_fixed_assets[0]
            ),
        ],
        "売掛金：売掛金/売上高": [
            "-",
            calculate_ratio(
                net_working_capital["sum_of_sales_receivables"][1],
                financial_summary["revenues"][1],
            ),
        ],
        "棚卸資産：棚卸資産/売上原価": [
            "-",
            calculate_ratio(
                net_working_capital["sum_of_inventories"][1],
                financial_summary["cost_of_sales"][1],
            ),
        ],
        "買掛金: 買掛金/売上高": [
            "-",
            calculate_ratio(
                net_working_capital["sum_of_purchase_debt"][1],
                financial_summary["revenues"][1],
            ),
        ],
        "正味有形固定資産：正味有形固定資産/売上高": [
            "-",
            calculate_ratio(
                net_trading_fixed_assets[1],
                financial_summary["revenues"][1],
            ),
        ],
        "投下資本(有利子負債＋株主資本)": [
            shareholders_equity[1]
            + interest_bearing_debt["sum_of_interest_bearing_debt"][1],
            shareholders_equity[0]
            + interest_bearing_debt["sum_of_interest_bearing_debt"][0],
        ],
        "営業利益率": [
            calculate_ratio(
                financial_summary["operating_profits"][0],
                financial_summary["revenues"][0],
            ),
            calculate_ratio(
                financial_summary["operating_profits"][1],
                financial_summary["revenues"][1],
            ),
        ],
        "投下資本回転率": [
            calculate_ratio(
                financial_summary["revenues"][0],
                shareholders_equity[0]
                + interest_bearing_debt["sum_of_interest_bearing_debt"][0],
            ),
            calculate_ratio(
                financial_summary["revenues"][1],
                shareholders_equity[1]
                + interest_bearing_debt["sum_of_interest_bearing_debt"][1],
            ),
        ],
        "NOPLAT": noplats,
        "ROIC(NOPLAT/投下資本)": calculate_roic(noplats, invested_capitals),
        "ROIC(NOPAT/投下資本)": calculate_roic(
            financial_summary["nopat"], invested_capitals
        ),
        "有形固定資産回転率": [
            calculate_ratio(
                financial_summary["revenues"][0],
                tangible_fixed_assets[0],
            ),
            calculate_ratio(
                financial_summary["revenues"][1],
                tangible_fixed_assets[1],
            ),
        ],
        # "未払費用 : 未払費用/売上高": calculate_ratio(
        #     net_working_capital["未払費用"][1], financial_summary["revenues"][1]
        # ),
        # "未払金 : 未払金/売上高": calculate_ratio(
        #     net_working_capital["未払金"][1], financial_summary["revenues"][1]
        # ),
    }


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
                    writer.writerow([japanese_label] + list(map(format_number, values)))
                elif isinstance(values, tuple):
                    writer.writerow([japanese_label] + list(map(format_number, values)))
                else:
                    writer.writerow([japanese_label, format_number(values)])


# ３桁区切りの文字列に変換
def format_number(number: float | str) -> str:
    if isinstance(number, str):
        return number
    elif isinstance(number, int):
        return "{:,}".format(number)
    return "{:,.2f}".format(number)


def format_dict_values(data):
    if isinstance(data, dict):
        # 辞書のキーと値をカンマ区切りで整形
        return ", ".join([f"{key}: {value}" for key, value in data.items()])
    elif isinstance(data, list):
        # リストの要素をカンマ区切りで整形
        return ", ".join(data)


if __name__ == "__main__":
    # processed_csvフォルダ下のcsvファイルを読み込み、データを処理する
    directory = os.path.join(os.getcwd(), "processed_csv")
    files = os.listdir(directory)
    for i, file in enumerate(files):
        print(f"{i}: {file}")
    file_number = int(input("処理したいファイルを選択してください: "))
    path = os.path.join(directory, files[file_number])
    # 株式会社エヌ・ピー・シー_S100SDQ5_有価証券報告書－第31期20220901－20230831.csv
    # から数字が8桁の文字列を取得し、その中から2022と2023を取得する
    result = re.findall(r"\d{8}", path)
    start_year = result[0][:4]
    end_year = result[1][:4]
    df = pd.read_csv(path)
    result = extract_and_process_data(df, start_year, end_year)
    export_to_csv(result, files[file_number])


def parse_csv(path, filename):
    result = re.findall(r"\d{8}", path)
    start_year = result[0][:4]
    end_year = result[1][:4]
    df = pd.read_csv(path, encoding="utf-8")
    result = extract_and_process_data(df, start_year, end_year)
    export_to_csv(result, filename)
