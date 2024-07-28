import datetime
import os
import re
import time

import pandas as pd
import requests

from type import ReportProperties

API_KEY = os.getenv("KEY")
BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents"
DOC_LIST_URL = BASE_URL + ".json"


def fetch_annual_report_by_docid(doc_id: str):
    doc_parameter = {"type": 5, "Subscription-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/{doc_id}", params=doc_parameter)
    if response.status_code != 200:
        print(f"docID: {doc_id} のファイルのダウンロードに失敗しました。")
        return None
    return response.content


def fetch_doc_list(date: str):
    # 2023-11-30 00:00:00
    # dateをYYYY-MM- DD形式に変換
    doc_list_parameter = {
        "date": date.split(" ")[0],
        "type": 2,  # 提出書類を取得します。
        "Subscription-Key": API_KEY,
    }
    result = requests.get(DOC_LIST_URL, doc_list_parameter).json()
    return result


def get_annual_reports_by_date_and_word(
    start_date, search_word: str
) -> list[ReportProperties]:
    annual_securities_reports: list[ReportProperties] = []
    result = fetch_doc_list(start_date)

    if "results" not in result:
        return annual_securities_reports
    print(result["results"])

    df = pd.DataFrame(result["results"])
    pattern = r"^有価証券報告書"
    for _, row in df.iterrows():
        description = row.get("docDescription")  # 書類の説明
        docId = row.get("docID")  # 書類管理番号
        secCode = row.get("secCode")  # 提出者証券コード
        filerName = row.get("filerName")  # 提出者名
        if (
            description is None
            or docId is None
            or secCode is None
            or re.search(pattern, description) is None
        ):
            continue
        report_info = {
            "docID": docId,
            "secCode": secCode,
            "docDescription": description,
            "filerName": filerName,
        }
        if search_word == "" or (search_word in filerName):
            annual_securities_reports.append(report_info)

    print("wait for 2 seconds")
    time.sleep(2)

    return annual_securities_reports


def get_annual_report_by_date_and_word(
    start_date, search_word: str
) -> ReportProperties or None:
    report = None
    if search_word == "":
        return report
    result = fetch_doc_list(start_date.strftime(start_date))

    if "results" not in result:
        return report

    df = pd.DataFrame(result["results"])
    pattern = r"^有価証券報告書"
    for _, row in df.iterrows():
        description = row.get("docDescription")  # 書類の説明
        (docId,) = row.get("docID")  # 書類管理番号
        secCode = row.get("secCode")  # 提出者証券コード
        filerName = row.get("filerName")  # 提出者名
        if (
            description is None
            or docId is None
            or secCode is None
            or re.search(pattern, description) is None
            or search_word not in filerName
        ):

            continue
        report = {
            "docID": docId,
            "secCode": secCode,
            "docDescription": description,
            "filerName": filerName,
        }
        break
    time.sleep(2)
    print("wait for 2 seconds")
    return report
