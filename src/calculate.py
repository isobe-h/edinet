import re


# 投下資本の計算
# 期首の投下資本と期末の投下資本を２で割って平均を取る
def calculate_invested_capital(
    sum_of_shareholders_equities: list[float],
    sum_of_interest_bearing_debts: list[float],
) -> list[float]:
    return [
        (sum_of_shareholders_equities[0] + sum_of_interest_bearing_debts[0]) / 2,
        (sum_of_shareholders_equities[1] + sum_of_interest_bearing_debts[1]) / 2,
    ]


def calculate_weighted_average_cost(text_data):
    # 該当事項がない場合のチェック
    if "該当事項はありません" in text_data:
        return 0  # 借入金等の情報がないため、加重平均借入コストは0
    if text_data == "":
        return 0

    # パターンを使用して借入金の詳細を抽出（小数点、カンマ、ダッシュに対応）
    pattern = (
        r"([\D]+?)(\d{1,3}(?:,\d{3})*|\－)\s*(\d{1,3}(?:,\d{3})*|\－)\s*(\d+\.\d+|\－)"
    )
    matches = re.findall(pattern, text_data)

    # 各借入金類の情報を処理
    total_weighted_rate = 0
    total_balance = 0

    for match in matches:
        description, start_balance, end_balance, rate = match
        if end_balance == "－" or rate == "－":
            continue  # データが存在しない場合はスキップ

        end_balance = int(end_balance.replace(",", ""))  # カンマを除去し整数に変換
        rate = float(rate)  # 文字列を浮動小数点数に変換

        total_weighted_rate += end_balance * rate
        total_balance += end_balance

    # 全体の加重平均借入コストを計算
    weighted_average_cost = total_weighted_rate / total_balance if total_balance else 0
    return weighted_average_cost


# 実効税率を取得
def calculate_effective_tax_rate(
    tax: float, net_income_before_tax_current_period: float
) -> float:
    # 実効税率

    return round((tax / net_income_before_tax_current_period), 2)


# incomesはNOPAT/NOPLAT
def calculate_roic(
    incomes: tuple[float, float],
    invested_capital: list[float],
) -> list[float]:
    return [
        round(incomes[0] / invested_capital[0], 4) * 100,
        round(incomes[1] / invested_capital[1], 4) * 100,
    ]


def calculate_growth_ratio(previous: float, current: float) -> str:
    if previous == 0 or current == 0:
        return "0%"
    result = (current - previous) / previous * 100
    return str(round(result, 2)) + "%"


def calculate_ratio(a: float, b: float) -> str:
    if a == 0 or b == 0:
        return "0%"
    result = a / b * 100
    return str(round(result, 2)) + "%"
