import logging

import pandas as pd

from calculate import (
    calculate_growth_ratio,
    calculate_invested_capital,
    calculate_ratio,
    calculate_str_ratio,
    calculate_weighted_average_cost,
)
from type import FinancialSummary, NetOperatingCapital
from utils import convert_str_to_float


class FinancialDataProcessor:
    def __init__(self, df: pd.DataFrame, year: int):
        self.df = df
        self.year = int(year)
        self.TAX_RATE = 0.3
        self.TAX_COEFFICIENT = 1 - self.TAX_RATE
        # 売上債権
        self.sales_receivables_items = (
            "売掛金",
            "契約資産",
            "前渡金",
            "電子記録債権",
            "受取手形",
            "その他、流動資産",
        )
        # 棚卸資産
        self.inventories_items = ("商品及び製品", "仕掛品", "原材料及び貯蔵品")
        # 仕入債務
        self.purchase_debt_items = (
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
        self.interest_bearing_debt_items = (
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

    def _get_item_name(self, item_name, term=None) -> str:
        if term:
            values = self.df.loc[
                (self.df["項目名"] == item_name) & (self.df["相対年度"].str.contains(term)),
                "項目名",
            ].values
            if len(values) > 0:
                return values[0]
        else:
            values = self.df.loc[self.df["項目名"] == item_name, "項目名"].values[0]
            if len(values) > 0:
                return values[0]
        return ""

    def _get_float_values_by_name(self, item_name, *terms: str) -> list[float]:
        # termsの長さのリストを作成
        result = [0.0] * len(terms)
        try:
            for index, term in enumerate(terms):
                value = self._get_first_value_by_name(item_name, term)
                if value and value.replace(".", "").replace("-", "").isnumeric():
                    result[index] = convert_str_to_float(value)
        except IndexError:
            logging.error(f"Value for {item_name} not found for term {term}")
            return result
        return result

    def _get_first_value_by_name(self, item_name, term=None) -> str:
        if item_name not in self.df["項目名"].values:
            return ""

        query_base = self.df["項目名"] == item_name
        if term:
            query_term = self.df["相対年度"].str.contains(term)
            # 連結、個別、その他の順で値を検索
            for category in ["連結", "個別"]:
                match = self.df.loc[
                    query_base & query_term & (self.df["連結・個別"].str.contains(category)),
                    "値",
                ]
                if not match.empty:
                    return match.iloc[0]
            # 連結も個別も見つからなかった場合、その他の値を検索
            other_match = self.df.loc[
                query_base & query_term & (~self.df["連結・個別"].str.contains("連結|個別", regex=True)),
                "値",
            ]
            if not other_match.empty:
                return other_match.iloc[0]
            return ""  # どのカテゴリーにも該当する値がない場合
        else:
            # termが指定されていない場合は、最初に見つかった値を返す
            return self.df.loc[query_base, "値"].iloc[0]

    def get_interest_bearing_debt(self):
        interest_bearing_debt_item_names = set(
            self._get_item_name(x, "当期末")
            for x in self.interest_bearing_debt_items
            if self._get_item_name(x, "当期") != ""
        )
        interest_bearing_debt = {
            item_name: self._get_float_values_by_name(item_name, "前期末", "当期末")
            for item_name in interest_bearing_debt_item_names
        }
        return interest_bearing_debt

    def calculate_financial_metrics(self):
        # Include methods to calculate specific financial metrics
        operating_profits = self._get_float_values_by_name("営業利益又は営業損失（△）", "前期", "当期")
        nopat = [round(x * self.TAX_COEFFICIENT, 2) for x in operating_profits]

        return {"operating_profits": operating_profits, "nopat": nopat}

    def get_report(self):
        consolidated_bs_title = "連結貸借対照表 [テキストブロック]"
        bs_title = "貸借対照表 [テキストブロック]"
        consolidated_debt_detail_title = "借入金等明細表、連結財務諸表 [テキストブロック]"
        debt_detail_title = "借入金等明細表、財務諸表 [テキストブロック]"
        # 連結貸借対照表を探して、なければ単体貸借対照表を探す
        bs = self._get_first_value_by_name(consolidated_bs_title, "当期")
        if bs == "":
            bs = self._get_first_value_by_name(bs_title, "当期")
            # 見つからない場合はエラー
            if bs == "":
                raise Exception("貸借対照表が見つかりませんでした")

        # 借入金等明細表、連結財務諸表 [テキストブロック]を探して、なければ単体財務諸表を探す

        debt_detail = self._get_first_value_by_name(consolidated_debt_detail_title, "当期")
        if debt_detail == "":
            debt_detail = self._get_first_value_by_name(debt_detail_title, "当期")
        debt_rate = calculate_weighted_average_cost(debt_detail)
        financial_summary = self.get_financial_summary()
        interest_bearing_debt = self.calc_interest_bearing_debt()
        net_working_capital = self.get_net_operating_capital()
        # money_unit = get_money_unit(bs)
        idle_assets = self.get_idle_assets()
        number_of_stock = self._get_float_values_by_name("発行済株式総数（普通株式）", "当期末")[0]
        number_of_company_stock = self._get_float_values_by_name("自己名義所有株式数（株）、自己株式等", "当期末")
        fcf = (
            financial_summary["nopat"][1]
            - financial_summary["capital_expenditure"][1]
            + financial_summary["deprecations"][1]
            - net_working_capital["fluctuation_of_net_operating_capitals"][1]
        )

        effective_tax_rates = [
            calculate_ratio(x, y)
            for x, y in zip(
                self._get_float_values_by_name("法人税等", "前期", "当期"),
                self._get_float_values_by_name("税引前当期純利益又は税引前当期純損失（△）", "前期", "当期"),
            )
        ]
        effective_tax_rates_str = [
            calculate_str_ratio(x, y)
            for x, y in zip(
                self._get_float_values_by_name("法人税等", "前期", "当期"),
                self._get_float_values_by_name("税引前当期純利益又は税引前当期純損失（△）", "前期", "当期"),
            )
        ]
        noplats = [x * (1 - float(y)) for x, y in zip(financial_summary["operating_profits"], effective_tax_rates)]

        shareholders_equity = self._get_float_values_by_name("株主資本", "前期", "当期")
        invested_capitals = calculate_invested_capital(
            shareholders_equity, interest_bearing_debt["sum_of_interest_bearing_debt"]
        )
        # bps = self._get_float_values_by_name("１株当たり純資産額", "前期", "当期末")
        tangible_fixed_assets = self._get_float_values_by_name("有形固定資産", "前期", "当期")
        # 累計減価償却額
        acculumated_depreciation = self._get_float_values_by_name(
            "減価償却累計額、その他、有形固定資産", "前期", "当期"
        )
        net_trading_fixed_assets = [x - y for x, y in zip(tangible_fixed_assets, acculumated_depreciation)]
        return {
            # "単位": str(money_unit),
            "年": [str(self.year - 1), str(self.year)],
            **financial_summary,
            "正味運転資本": "",
            **net_working_capital,
            "有利子負債": "",
            **interest_bearing_debt,
            "債権者コスト": ["-", debt_rate],
            "その他": "",
            "株主資本": shareholders_equity,
            "株式数(自社株控除後)": ["-", number_of_stock - number_of_company_stock[0]],
            **idle_assets,
            "遊休資産": "",
            "  ": "",
            "FCF(NOPAT+減価償却費-設備投資±正味運転資本増減)": ["-", fcf],
            "現在価値に割り引いたFCF": "",
            "    ": "",
            "資本効率": "",
            "投下資本(有利子負債＋株主資本)": invested_capitals,
            "税引き後営業利益率(税率３０％)": [
                calculate_str_ratio(x, y) for x, y in zip(financial_summary["nopat"], financial_summary["revenues"])
            ],
            "投下資本回転率(税率３０％)": [
                calculate_str_ratio(x, y) for x, y in zip(financial_summary["revenues"], invested_capitals)
            ],
            "ROIC(NOPAT/投下資本)": [
                calculate_str_ratio(x, y) for x, y in zip(financial_summary["nopat"], invested_capitals)
            ],
            "実効税率": effective_tax_rates_str,
            "実効税引き後営業利益率(営業利益x(1-実効税率))": [
                calculate_str_ratio(x, y) for x, y in zip(noplats, financial_summary["revenues"])
            ],
            "NOPLAT(営業利益x(1-実効税率))": noplats,
            "ROIC(NOPLAT/投下資本)": [calculate_str_ratio(x, y) for x, y in zip(noplats, invested_capitals)],
            "         ": "",
            "予測レシオ": "",
            "売上原価：売上原価/売上高": [
                calculate_str_ratio(
                    financial_summary["cost_of_sales"][1],
                    financial_summary["revenues"][1],
                ),
            ],
            "販売費及び一般管理費：販売費及び一般管理費/売上高": [
                calculate_str_ratio(
                    self._get_float_values_by_name("販売費及び一般管理費", "当期")[0],
                    financial_summary["revenues"][1],
                ),
            ],
            "減価償却費：減価償却費(t)/正味有形固定資産(t-1)": [
                calculate_str_ratio(financial_summary["deprecations"][1], net_trading_fixed_assets[0]),
            ],
            "売掛金：売掛金/売上高": [
                calculate_str_ratio(
                    net_working_capital["sum_of_sales_receivables"][1],
                    financial_summary["revenues"][1],
                ),
            ],
            "棚卸資産：棚卸資産/売上原価": [
                calculate_str_ratio(
                    net_working_capital["sum_of_inventories"][1],
                    financial_summary["cost_of_sales"][1],
                ),
            ],
            "買掛金: 買掛金/売上高": [
                calculate_str_ratio(
                    net_working_capital["sum_of_purchase_debt"][1],
                    financial_summary["revenues"][1],
                ),
            ],
            "正味有形固定資産（有形固定資産-累計減価償却費）": net_trading_fixed_assets,
            "正味有形固定資産：正味有形固定資産/売上高": [
                calculate_str_ratio(
                    net_trading_fixed_assets[1],
                    financial_summary["revenues"][1],
                ),
            ],
            # "有形固定資産回転率": [
            #     calculate_str_ratio(x, y) for x, y in zip(financial_summary["revenues"], tangible_fixed_assets)
            # ],
            # "未払費用 : 未払費用/売上高": calculate_ratio(
            #     net_working_capital["未払費用"][1], financial_summary["revenues"][1]
            # ),
            # "未払金 : 未払金/売上高": calculate_ratio(
            #     net_working_capital["未払金"][1], financial_summary["revenues"][1]
            # ),
        }

    def calc_interest_bearing_debt(self):
        interest_bearing_debt_item_names = set(
            self._get_item_name(x, "当期末")
            for x in self.interest_bearing_debt_items
            if self._get_item_name(x, "当期") != ""
        )
        interest_bearing_debt = {
            item_name: self._get_float_values_by_name(item_name, "前期末", "当期末")
            for item_name in interest_bearing_debt_item_names
        }
        interest_bearing_debt["sum_of_interest_bearing_debt"] = [
            sum(value[i] for value in interest_bearing_debt.values()) for i in range(2)
        ]
        return interest_bearing_debt

    def get_net_operating_capital(self) -> NetOperatingCapital:
        # 重複項目が発生するため、項目名からsetを取得
        sales_receivables_item_names = set(
            [
                self._get_item_name(x, "当期")
                for x in self.sales_receivables_items
                if self._get_item_name(x, "当期") != ""
            ]
        )
        inventories_item_names = set(
            [self._get_item_name(x, "当期") for x in self.inventories_items if self._get_item_name(x, "当期") != ""]
        )
        purchase_debt_item_names = set(
            [self._get_item_name(x, "当期") for x in self.purchase_debt_items if self._get_item_name(x, "当期") != ""]
        )
        sales_receivables = {
            item_name: self._get_float_values_by_name(item_name, "前期", "当期")
            for item_name in sales_receivables_item_names
        }
        inventories = {
            item_name: self._get_float_values_by_name(item_name, "前期", "当期") for item_name in inventories_item_names
        }
        purchase_debt = {
            item_name: self._get_float_values_by_name(item_name, "前期", "当期")
            for item_name in purchase_debt_item_names
        }
        sum_of_sales_receivables = [sum(values[i] for values in sales_receivables.values()) for i in range(2)]
        sum_of_inventories = [sum(values[i] for values in inventories.values()) for i in range(2)]
        sum_of_purchase_debt = [sum(values[i] for values in purchase_debt.values()) * -1 for i in range(2)]
        sums = [x + y + z for x, y, z in zip(sum_of_inventories, sum_of_sales_receivables, sum_of_purchase_debt)]
        net_operating_capital: NetOperatingCapital = {
            "sum_of_sales_receivables": sum_of_sales_receivables,
            "sum_of_inventories": sum_of_inventories,
            "sum_of_purchase_debt": sum_of_purchase_debt,
            "sum_of_net_operating_capitals": sums,
            "fluctuation_of_net_operating_capitals": ["-", sums[1] - sums[0]],
        }
        return net_operating_capital

    def get_idle_assets(self):
        return {
            "投資有価証券": self._get_float_values_by_name("投資有価証券", "前期", "当期"),
            "現金及び預金": self._get_float_values_by_name("現金及び預金", "前期", "当期"),
        }

    def get_financial_summary(self) -> FinancialSummary:
        operating_profits = self._get_float_values_by_name("営業利益又は営業損失（△）", "前期", "当期")
        nopat = [round(float(x)) * self.TAX_COEFFICIENT for x in operating_profits]
        revenues = self._get_float_values_by_name("売上高", "前期", "当期")
        # "売上原価
        cost_of_sales = self._get_float_values_by_name("売上原価", "前期", "当期")
        # 一般管理費及び販売費
        selling_general_and_administrative_expenses = self._get_float_values_by_name(
            "販売費及び一般管理費", "前期", "当期"
        )
        # 純利益
        # net_income = self._get_float_values_by_name("当期純利益又は当期純損失（△）", "前期", "当期")
        # # 潜在株式調整後１株当たり当期純利益
        # net_income_per_share_adjusted_for_potential_stock: list[float] = self._get_float_values_by_name(
        #     "潜在株式調整後1株当たり当期純利益", "前期", "当期"
        # )
        # # 潜在株式がない場合
        # if len(net_income_per_share_adjusted_for_potential_stock) == 0:
        #     net_income_per_share_adjusted_for_potential_stock = self._get_float_values_by_name(
        #         "１株当たり当期純利益又は当期純損失（△）", "前期", "当期"
        #     )
        # # 総資産
        # total_assets = self._get_float_values_by_name("総資産額", "前期", "当期")
        # 売上総利益を定義
        gross_profit = [x - y for x, y in zip(revenues, cost_of_sales)]

        return {
            "revenues": revenues,
            "revenue_growth_rate": [
                "-",
                calculate_growth_ratio(revenues[0], revenues[1]),
            ],
            "cost_of_sales": cost_of_sales,
            "売上総利益": gross_profit,
            "売上総利益率": [calculate_str_ratio(x, y) for x, y in zip(gross_profit, revenues)],
            "selling_general_and_administrative_expenses": selling_general_and_administrative_expenses,
            "operating_profits": operating_profits,
            "営業利益率": [calculate_str_ratio(x, y) for x, y in zip(operating_profits, revenues)],
            "operating_profit_growth_rate": [
                "-",
                calculate_growth_ratio(
                    operating_profits[0],
                    operating_profits[1],
                ),
            ],
            "nopat": nopat,
            "deprecations": self._get_float_values_by_name(
                "減価償却費、営業活動によるキャッシュ・フロー", "前期", "当期"
            ),
            "capital_expenditure": self._get_float_values_by_name("設備投資額、設備投資等の概要", "前期", "当期"),
            # "net_income": net_income,
            # "net_income_per_share_adjusted_for_potential_stock": net_income_per_share_adjusted_for_potential_stock,
            # "total_assets": total_assets,
        }
