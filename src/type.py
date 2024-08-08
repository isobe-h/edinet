from enum import Enum
from typing import TypedDict


class FinancialSumary(TypedDict):
    revenues: tuple[int]
    operating_profits: tuple[int]
    nopat: tuple[int]
    deprecations: tuple[int]
    capital_expenditure: tuple[int]


# 売上債権
class SalesReceivables(TypedDict):
    accounts_receivables: tuple[int]
    electronic_records_receivables: tuple[int]
    receivable_notes: tuple[int]
    contract_assets: tuple[int]
    other_current_assets: tuple[int]


# 棚卸資産
class Inventory(TypedDict):
    merchandise_or_products: tuple[int]
    work_in_process: tuple[int]
    raw_materials: tuple[int]


# 仕入債務
class PurchaseDebt(TypedDict):
    trade_payables: tuple[int]
    unpaid_expenses: tuple[int]
    unpaid_money: tuple[int]
    electronic_records_debt: tuple[int]
    contract_liabilities: tuple[int]
    other_current_liabilities: tuple[int]


# 正味運転資本
class NetOperatingCapital(TypedDict):
    sales_receivables: SalesReceivables
    inventories: Inventory
    purchase_debt: PurchaseDebt
    sum: tuple[int]


# 有利子負債
class InterestBearingDebt(TypedDict):
    short_term_debt: int
    long_term_debt_within_1year: int
    long_term_debt: int
    corporate_bonds: int
    commercial_papers: int
    lease_obligations: int
    others: int
    sum: int


class ReportProperties(TypedDict):
    docID: str
    secCode: str
    docDescription: str
    filerName: str


# 120	有価証券報告書
# 130	訂正有価証券報告書
# 140	四半期報告書
# 150	訂正四半期報告書
# 160	半期報告書
# 170	訂正半期報告書
# 350	大量保有報告書
# 360	訂正大量保有報告書
class ReportType(Enum):
    ANNUAL_SECURITIES_REPORT = 120
    AMENDED_ANNUAL_SECURITIES_REPORT = 130
    QUARTERLY_REPORT = 140
    AMENDED_QUARTERLY_REPORT = 150
    SEMI_ANNUAL_REPORT = 160
    AMENDED_SEMI_ANNUAL_REPORT = 170
    LARGE_HOLDING_REPORT = 350
    AMENDED_LARGE_HOLDING_REPORT = 360


japanese_dict = {
    "revenues": "売上高",
    "operating_profits": "営業利益",
    "nopat": "NOPAT（税率30%）",
    "noplat": "NOPLAT(実行税引後営業利益)",
    "deprecations": "減価償却費",
    "capital_expenditure": "設備投資額",
    "accounts_receivables": "|-売掛金",
    "electronic_records_receivables": "|-電子記録債権",
    "receivable_notes": "|-受取手形",
    "contract_assets": "|-契約資産",
    "other_current_assets": "|-その他の流動資産",
    "merchandise_or_products": "|-商品及び製品",
    "work_in_process": "|-仕掛品",
    "raw_materials": "|-原材料",
    "trade_payables": "|-支払手形及び買掛金",
    "unpaid_expenses": "|-未払費用",
    "unpaid_money": "|-未払金",
    "electronic_records_debt": "|-電子記録債務",
    "contract_liabilities": "|-契約負債",
    "other_current_liabilities": "|-その他の流動負債",
    "sales_receivables": "|-売上債権",
    "inventories": "|-棚卸資産",
    "purchase_debt": "|-仕入債務",
    "sum_of_inventories": "棚卸資産",
    "sum_of_sales_receivables": "売上債権",
    "sum_of_purchase_debt": "仕入債務",
    # "１年内返済予定の長期借入金",
    "long_term_debt_within_1year": "１年内返済予定の長期借入金",
    "short_term_debt": "短期借入金",
    "long_term_debt": "長期借入金",
    "corporate_bonds": "社債",
    "commercial_papers": "コマーシャルペーパー",
    "lease_obligations": "リース債務",
    "others": "その他の有利子負債",
    "sum_of_net_operating_capitals": "正味運転資本合計",
    "fluctuation_of_net_operating_capitals": "正味運転資本の増減",
    "sum_of_interest_bearing_debt": "有利子負債合計",
    "operating_profit_margin": "営業利益率",
    "operating_profit_growth_rate": "営業利益成長率",
    "revenue_growth_rate": "売上成長率",
    "selling_general_and_administrative_expenses": "販売費および一般管理費",
    "cost_of_sales": "売上原価",
    "net_income": "純利益",
    "total_assets": "総資産",
    "net_income_per_share_adjusted_for_potential_stock": "潜在株式調整後一株当たり純利益",
}
