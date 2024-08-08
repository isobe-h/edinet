import os

import requests

API_KEY = os.getenv("KEY")
BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents"
DOC_LIST_URL = BASE_URL + ".json"
DOC_TYPE = 5  # CSV


def fetch_annual_report_by_docid(doc_id: str):
    doc_parameter = {"type": DOC_TYPE, "Subscription-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/{doc_id}", params=doc_parameter)
    assert response.status_code == 200
    return response.content


def fetch_doc_list(date: str):
    # 2023-11-30 00:00:00
    # dateをYYYY-MM- DD形式に変換
    if " " in date:
        date = date.split(" ")[0]
    doc_list_parameter = {
        "date": date,
        "type": 2,  # 提出書類を取得します。
        "Subscription-Key": API_KEY,
    }
    result = requests.get(DOC_LIST_URL, doc_list_parameter)
    return result.json()
