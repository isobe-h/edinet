import os
import re
import zipfile
from datetime import datetime

from fetch import fetch_annual_report, search_annual_reports_by_term
from file_utils import clean_up_directory, csv_to_df, extract_zip
from parse import parse_csv
from preprocess import preprocess_csv

save_dir = os.path.join(os.getcwd(), "csv")
print(save_dir)


def save_annual_report(date: str):
    start_date = datetime.strptime(date, "%Y%m%d")
    end_date = datetime.strptime(date, "%Y%m%d")

    annual_securities_reports = search_annual_reports_by_term(start_date, end_date)

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
    selected_doc_id = input("ダウンロードする番号を入力してください: ")
    selected_doc = [
        report
        for report in annual_securities_reports
        if report["docID"] == selected_doc_id
    ][0]
    if not selected_doc:
        print(f"{selected_doc_id} に一致する有価証券報告書はありません。")
        return
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


if __name__ == "__main__":
    if os.getenv("KEY") is None:
        print("APIキーが設定されていません。")
        exit(1)
    date = input_date()
    save_path = save_annual_report(date)
    preprocess_csv(save_path)
    corporate_name = save_path.split("_")[1].split(".")[0] + ".csv"
    parse_csv(save_path, corporate_name)
