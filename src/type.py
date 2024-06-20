from typing import NotRequired, Optional, TypedDict


class FinancialSumary(TypedDict):
    revenue: int
    operating_profit: str
    tax_rate: int


# 売上債権
class SalesReceivables(TypedDict):
    sales_receivables: Optional[int]
    electronic_records_receivables: Optional[int]
    receivable_notes: Optional[int]
    contract_assets: Optional[int]
    other_current_assets: Optional[int]


# 棚卸資産
class Inventory(TypedDict):
    inventories: Optional[int]
    work_in_process: Optional[int]
    raw_materials: Optional[int]


# 仕入債務
class TradePayables(TypedDict):
    trade_payables: Optional[int]
    unpaid_expenses: Optional[int]
    unpaid_money: Optional[int]
    electronic_records_debt: Optional[int]
    contract_liabilities: Optional[int]
    other_current_liabilities: Optional[int]


# 正味運転資本
class NetOperatingCapital(TypedDict):
    sales_receivables: SalesReceivables
    inventories: Inventory
    trade_payables: TradePayables


# 有利子負債
class InterestBearingDebt(TypedDict):
    short_term_debt: Optional[int]
    long_term_debt: Optional[int]
    corporate_bonds: Optional[int]
    commercial_papers: Optional[int]
    lease_obligations: Optional[int]
    others: Optional[int]


class ReportProperties(TypedDict):
    docID: str
    secCode: str
    docDescription: str
    filerName: str
