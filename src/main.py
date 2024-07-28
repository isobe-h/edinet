import os
import re
import zipfile
from datetime import datetime

import questionary

from fetch import fetch_annual_report, search_annual_reports_by_term_and_word
from file_utils import clean_up_directory, csv_to_df, extract_zip
from parse import parse_csv
from preprocess import preprocess_csv
from type import ReportProperties

save_dir = os.path.join(os.getcwd(), "csv")
print(save_dir)


def get_selected_annual_reports(date: str, word: str):
    start_date = datetime.strptime(date, "%Y%m%d")
    end_date = datetime.strptime(date, "%Y%m%d")

    annual_securities_reports = search_annual_reports_by_term_and_word(
        start_date, end_date, word
    )

    if not annual_securities_reports:
        print(
            start_date.strftime("%Y-%m-%d"),
            "から",
            end_date.strftime("%Y-%m-%d"),
            "の間に有価証券報告書はありません。",
        )
        return
    # annual_securities_reportsの中身をを表示して、ダウンロードするファイルを選択させる
    print("以下のファイルが見つかりました。")
    print("docID, docDescription, filerName")
    for i, report in enumerate(annual_securities_reports):
        print(
            f"{i}: {report['docDescription']}, {report['filerName']}: {report['docID']}"
        )
    selected_doc_id = input("ダウンロードするdoc idを入力してください: ")
    selected_doc = [
        report
        for report in annual_securities_reports
        if report["docID"] == selected_doc_id
    ][0]
    if not selected_doc:
        print(f"{selected_doc_id} に一致する有価証券報告書はありません。")
        return
    return selected_doc


def save_annual_report(selected_doc: ReportProperties):
    selected_doc_id = selected_doc["docID"]
    zip_file = fetch_annual_report(selected_doc_id)
    if zip_file is None:
        print(f"docID: {selected_doc_id} のファイルのダウンロードに失敗しました。")
        exit(1)
    try:
        extract_zip(zip_file)
        # 選択したdocIDのファイルのdocDescriptionを取得
        df = csv_to_df()[0]
        title = (
            f"{selected_doc_id}_{sanitize_filename(selected_doc['docDescription'])}.csv"
        )
        save_path = os.path.join(save_dir, title)

        df.to_csv(
            save_path,
            index=False,
            encoding="utf-8",
        )
        clean_up_directory()
        return save_path
    except zipfile.BadZipFile:
        print(f"docID: {selected_doc_id} のファイルはZIPファイルではありません。")
        exit(1)


def sanitize_filename(name):
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


def input_search_word():
    search_word = input("検索するキーワードを入力してください: ")
    return search_word


if __name__ == "__main__":
    if os.getenv("KEY") is None:
        print("APIキーが設定されていません。")
        exit(1)
    # Questionaryを使って選択肢を表示
    # 入力項目は、1.日付と検索ワード、2.日付のみ、3.Doc IDから選択
    which_input = questionary.select(
        "どのように検索しますか？",
        choices=["日付と検索ワード", "日付のみ", "Doc IDから選択"],
    ).ask()
    if which_input == "日付と検索ワード":
        date = input_date()
        search_word = input_search_word()
    elif which_input == "日付のみ":
        date = input_date()
        search_word = ""
    selected_doc = get_selected_annual_reports(date, search_word)
    if selected_doc is None:
        exit(1)
    save_path = save_annual_report(selected_doc)
    preprocess_csv(save_path)
    corporate_name = save_path.split("_")[1].split(".")[0] + ".csv"
    parse_csv(save_path, corporate_name)
