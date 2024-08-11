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
