import os
import re
import time
import zipfile
from datetime import datetime

import pandas as pd

from fetch import fetch_annual_report, search_annual_reports_by_term
from file_utils import clean_up_directory, csv_to_df, extract_zip

save_dir = os.path.join(os.getcwd(), "csv")
print(save_dir)


def main(date: str):
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
        print(title)
        df.to_csv(
            os.path.join(save_dir, title),
            index=False,
            encoding="utf-8",
        )
        clean_up_directory()
        print(f"docID: {selected_doc_id} のファイルが正常にダウンロードされました。")
        print("wait 2 seconds")
        time.sleep(2)
    except zipfile.BadZipFile:
        print(f"docID: {selected_doc_id} のファイルはZIPファイルではありません。")


def sanitize_filename(name):
    # OSで禁止されている文字とパス区切り文字をアンダースコアに置き換える
    return re.sub(r'[\/:*?"<>|\(\)]+', "", name)


if __name__ == "__main__":
    if os.getenv("KEY") is None:
        print("APIキーが設定されていません。")
        exit(1)
    while True:
        # date = input("検索する日付を入力してください(yyyymmdd): ")
        date = "20240620"
        if date == "q":
            break
        # yyyymmddかどうか
        if date.isdigit() and len(date) == 8:
            main(date)
            exit(0)
        else:
            print("入力が不正です。4桁の数字を入力してください。")
