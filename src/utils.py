import re


def sanitize_filename(name):
    print(name)
    # OSで禁止されている文字とパス区切り文字をアンダースコアに置き換える
    return re.sub(r'[\/:*?"<>|\(\)]+', "", name)


def input_date():
    while True:
        date = input("検索する日付を入力してください(yyyymmdd): ")
        if date == "q":
            return
        # yyyymmddかどうか
        if date.isdigit() and len(date) == 8:
            return date
        else:
            print("入力が不正です。4桁の数字を入力してください。")
            input_date()


def input_sec_code():
    while True:
        search_word = input("検索する証券コードを入力してください(4桁): ")
        if search_word.isdigit() and len(search_word) == 4:
            return search_word + "0"
        else:
            print("入力が不正です。4桁の数字を入力してください。")


def convert_to_thousand_separated(number: float | str) -> str:
    # 数値が文字列の場合、そのまま返す
    if isinstance(number, str):
        return number

    # 数値をフォーマットして返す
    if isinstance(number, (int, float)):
        # 小数部分が0なら整数部のみ表示
        if number == int(number):
            return f"{int(number):,}"
        else:
            # 小数部分がある場合は小数点以下2桁まで表示
            return f"{number:,.2f}"

    return "{:,.2f}".format(number)


def convert_str_to_float(value: str) -> float:
    if value == "－":
        return 0
    # △が頭についている場合、マイナスに変換
    if "△" in str(value):
        return -float(str(value).replace("△", ""))
    return float(value)
