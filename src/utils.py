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
