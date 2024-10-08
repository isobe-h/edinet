import os
import re
import zipfile
from datetime import datetime

import pandas as pd
import questionary

from fetch import fetch_annual_report_by_docid, fetch_doc_list
from file_utils import PREPROCESSED_CSV_HEADER, export_df_to_csv, save_doc_from_zip
from financial_data import FinancialDataProcessor
from preprocess import preprocess_csv
from type import ReportType
from utils import input_date, input_sec_code, sanitize_filename


def search_annual_report_by_date_and_seccode(
    start_date: str, report_type: ReportType, secCode: str
) -> pd.DataFrame:
    result = fetch_doc_list(start_date)
    assert "results" in result
    df = pd.DataFrame(result["results"])
    df_filtered = df[df["secCode"].notna()]
    report_type = str(ReportType.ANNUAL_SECURITIES_REPORT.value)
    # print(df_filtered["secCode"].unique())
    df_filtered = df_filtered.query(
        "docTypeCode == @report_type and secCode == @secCode",
    )
    assert len(df_filtered) == 1
    return df_filtered


def fetch_and_save_annual_report(df: pd.DataFrame) -> str:
    filerName = sanitize_filename(df["filerName"].values[0])
    docDescription = sanitize_filename(df["docDescription"].values[0])
    sec_code = df["secCode"].values[0]
    selected_doc_id = df["docID"].values[0]
    dates = re.findall(r"\d{8}", docDescription)
    end_year = dates[1][:4]
    title = f"{filerName}_{docDescription}.csv"
    zip_file = fetch_annual_report_by_docid(selected_doc_id)
    if zip_file is None:
        print(f"docID: {selected_doc_id} のファイルのダウンロードに失敗しました。")
        exit(1)
    try:
        return save_doc_from_zip(zip_file, os.path.join(sec_code, end_year), title)
    except zipfile.BadZipFile:
        print(f"docID: {selected_doc_id} のファイルはZIPファイルではありません。")
        exit(1)


# 1. 日付と証券コードから、企業の業績データを取得する
def generate_report_from_single_report(date: str, sec_code: str):
    start_date = str(datetime.strptime(date, "%Y%m%d"))
    df = search_annual_report_by_date_and_seccode(start_date, 120, sec_code)
    df.head()
    saved_path = fetch_and_save_annual_report(df)
    preprocessed_path = preprocess_csv(saved_path)
    preprocess_df = pd.read_csv(preprocessed_path, encoding="utf-8")
    year = start_date[:4]
    result = FinancialDataProcessor(preprocess_df, year).get_report()
    save_path = preprocessed_path.replace(PREPROCESSED_CSV_HEADER, "")
    export_df_to_csv(result, save_path)


# 過去10年分のデータを取得する(今日から数えて)
# 日付は多少前後するので、指定した日付で見つからない場合は、±1の日付で検索し続ける
# 全部取得したら、それぞれのデータを結合して、csvに保存する。


if __name__ == "__main__":
    assert os.getenv("KEY")
    # which_input = questionary.select(
    #     "どのように検索しますか？",
    #     choices=["日付と証券コード"],
    # ).ask()
    # if which_input == "日付と証券コード":
    #     date = input_date()
    #     sec_code = input_sec_code()
    #     generate_report_from_single_report(date, sec_code)
    generate_report_from_single_report("20231130", "62550")
