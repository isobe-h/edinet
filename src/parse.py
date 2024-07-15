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
import re

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
# 売上債権
sales_receivables_items = [
    "売掛金",
    "電子記録債権",
    "受取手形",
    "契約資産",
    "その他、流動資産",
    "前渡金",
]
# 棚卸資産
inventories_items = ["商品及び製品", "仕掛品", "原材料及び貯蔵品"]
# 仕入債務
purchase_debt_items = [
    "支払手形",
    "買掛金",
    "未払費用",
    "未払金",
    "電子記録債務",
    "契約負債",
    "前受金",
    "その他、流動負債",
]
# 有利子負債
interest_bearing_debt_items = [
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
]


def get_item_name(df, item_name, term=None) -> str:
    """
    指定された項目名を含む項目の名前を取得します。
    完全合致する項目が複数ある場合は、最初の項目を返します。
    ないばあいは、部分一致する項目の最初の項目を返します。
    """
    if term:
        values = df.loc[
            (df["項目名"] == item_name) & (df["相対年度"].str.contains(term)),
            "項目名",
        ].values
        if len(values) > 0:
            return values[0]
    else:
        values = df.loc[df["項目名"] == item_name, "項目名"].values[0]
        if len(values) > 0:
            return values[0]
    return ""


def get_last_value(df, item_name, term=None) -> int:
    """
    指定された項目名から最後の値を取得します。
    """
    value = 0
    if item_name not in df["項目名"].values:
        return value
    if term:
        value = df.loc[
            (df["項目名"] == item_name) & (df["相対年度"].str.contains(term)), "値"
        ].iloc[-1]
    else:
        value = df.loc[df["項目名"] == item_name, "値"].iloc[-1]
    return int(value)


def calc_interest_bearing_debt(df) -> InterestBearingDebt:
    interest_bearing_debt_item_names = set(
        [
            get_item_name(df, x, "当期末")
            for x in interest_bearing_debt_items
            if get_item_name(df, x, "当期") != ""
        ]
    )
    interest_bearing_debt = {
        item_name: [
            get_last_value(df, item_name, "前期末"),
            get_last_value(df, item_name, "当期末"),
        ]
        for item_name in interest_bearing_debt_item_names
    }

    interest_bearing_debt["sum"] = [
        sum([value[0] for value in interest_bearing_debt.values()]),
        sum([value[1] for value in interest_bearing_debt.values()]),
    ]

    return interest_bearing_debt


def get_net_working_capital(df) -> NetOperatingCapital:
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
    print(sales_receivables_item_names)
    print(inventories_item_names)
    print(purchase_debt_item_names)
    sales_receivables = {
        item_name: [
            get_last_value(df, item_name, "前期"),
            get_last_value(df, item_name, "当期"),
        ]
        for item_name in sales_receivables_item_names
    }
    inventories = {
        item_name: [
            get_last_value(df, item_name, "前期"),
            get_last_value(df, item_name, "当期"),
        ]
        for item_name in inventories_item_names
    }
    purchase_debt = {
        item_name: [
            get_last_value(df, item_name, "前期"),
            get_last_value(df, item_name, "当期"),
        ]
        for item_name in purchase_debt_item_names
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
    operating_profits = [
        get_last_value(df, "営業利益又は営業損失（△）", "前期"),
        get_last_value(df, "営業利益又は営業損失（△）", "当期"),
    ]
    nopat = [
        float(operating_profits[0]) * TAX_COEFFICIENT,
        float(operating_profits[1]) * TAX_COEFFICIENT,
    ]
    return {
        "revenues": [
            get_last_value(df, "売上高", "前期"),
            get_last_value(df, "売上高", "当期"),
        ],
        "operating_profits": operating_profits,
        "nopat": nopat,
        "deprecations": [
            get_last_value(df, "減価償却費、セグメント情報", "前期"),
            get_last_value(df, "減価償却費、セグメント情報", "当期"),
        ],
        "capital_expenditure": [
            "-",
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


# 借入利率を取得
def calculate_weighted_average_interest_rate(text_data):
    # 更新された正規表現パターン
    items = (
        "短期借入金",
        "長期借入金",
        "１年以内に返済予定の長期借入金",
        "１年以内返済予定のリース債務",
        "リース債務",
    )
    rate_pattern = r"(\d\.\d)"
    rate = 0.0
    divided = re.split(r"－", text_data)  # 項目ごとに分割
    # lengthが0の項目を削除
    divided = [x for x in divided if len(x) > 0]
    for item in items:
        # 項目名を含む行を取得
        for line in divided:
            if item in line:
                # rateにマッチする部分を取得して切り取る
                match = re.search(rate_pattern, line)
                if match:
                    rate = float(match.group(1))
                    break
    return rate


def extract_and_process_data(df):
    bs: str = df.loc[df["項目名"] == "連結貸借対照表 [テキストブロック]", "値"].iloc[0]
    # 借入金明細
    debt_detail = str(
        df.loc[
            df["項目名"] == "借入金等明細表、連結財務諸表 [テキストブロック]", "値"
        ].iloc[-1]
    )
    debt_rate = calculate_weighted_average_interest_rate(debt_detail)

    financial_summary = get_financial_summary(df)
    interest_bearing_debt = calc_interest_bearing_debt(df)
    net_working_capital = get_net_working_capital(df)
    money_unit = get_money_unit(bs)
    idle_assets = get_idle_assets(df)
    number_of_stock = get_last_value(df, "発行済株式総数（普通株式）")
    number_of_company_stock = get_last_value(df, "自己名義所有株式数（株）、自己株式等")

    fcf = (
        financial_summary["nopat"][1]
        - financial_summary["capital_expenditure"][1]
        + financial_summary["deprecations"][1]
        - net_working_capital["sum_of_net_operating_capitals"][1]
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
    bps = round(get_last_value(df, "純資産額", "当期末") / number_of_stock, 2)
    return {
        # "単位": str(money_unit),
        "期": ["前期", "当期"],
        **financial_summary,
        "営業利益成長率": [
            "-",
            calculate_growth_rate(financial_summary["operating_profits"]),
        ],
        "FCF": ["-", fcf],
        "ROIC(NOPLAT/投下資本)": calculate_roic(
            effective_tax_rates,
            financial_summary["operating_profits"],
            interest_bearing_debt["sum"],
        ),
        "BPS": [
            "-",
            bps,
        ],
        "正味運転資本": "",
        **net_working_capital,
        "正味運転資本の増減": [
            "-",
            net_working_capital["sum_of_net_operating_capitals"][1]
            - net_working_capital["sum_of_net_operating_capitals"][0],
        ],
        " ": "",
        "株式数(自社株控除後)": ["-", number_of_stock - number_of_company_stock],
        **idle_assets,
        "有利子負債": "",
        **interest_bearing_debt,
        "純有利子負債": [
            idle_assets["現金及び預金"][0] - interest_bearing_debt["sum"][0],
            idle_assets["現金及び預金"][1] - interest_bearing_debt["sum"][1],
        ],
        "債権者コスト（要修正）": ["-", debt_rate],
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
