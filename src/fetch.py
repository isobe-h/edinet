import os
import time
from datetime import timedelta

import pandas as pd
import requests

from type import ReportProperties

API_KEY = os.getenv("KEY")
BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents"
DOC_LIST_URL = BASE_URL + ".json"


def fetch_annual_report(doc_id: str):
    """書類取得APIを使って書類をダウンロードする
                                                                    docID (str): 書類管理番号
                                                                    type (str): 1:提出本文書及び監査報告書、2:PDF、3:代替書面・添付文書、
                                                                                                                                                                                                                                                                    4:英文ファイル、5:CSV

    Returns:
                                                                    bytes: ダウンロードしたファイルのバイナリデータ
    """
    doc_parameter = {"type": 5, "Subscription-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/{doc_id}", params=doc_parameter)
    if response.status_code != 200:
        print(f"docID: {doc_id} のファイルのダウンロードに失敗しました。")
        return None
    return response.content


def search_annual_reports_by_term_and_word(
    start_date, end_date, search_word: str
) -> list[ReportProperties]:
    current_date = start_date
    annual_securities_reports = []

    while current_date <= end_date:
        print(f"Fetching data for {current_date.strftime('%Y-%m-%d')}...")
        doc_list_parameter = {
            "date": current_date.strftime("%Y-%m-%d"),
            "type": 2,  # 提出書類を取得します。
            "Subscription-Key": API_KEY,
        }
        result = requests.get(DOC_LIST_URL, doc_list_parameter).json()

        if "results" not in result:
            continue

        df = pd.DataFrame(result["results"])
        for _, row in df.iterrows():
            description = row.get("docDescription")  # 書類の説明
            docId = row.get("docID")  # 書類管理番号
            secCode = row.get("secCode")  # 提出者証券コード
            filerName = row.get("filerName")  # 提出者名
            if description is None or docId is None or secCode is None:
                continue
            if "訂正有価証券報告書" in str(description) or "受益証券" in str(
                description
            ):
                continue
            if "有価証券報告書" in str(description):
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
        current_date += timedelta(days=1)

    return annual_securities_reports
