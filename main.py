import glob
import io
import os
import shutil
import time
import zipfile
from datetime import datetime, timedelta

import pandas as pd
import requests

API_KEY = os.getenv("KEY")
BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents"
DOC_LIST_URL = BASE_URL + ".json"
DOC_PATH = "csv"


def fetch_annual_report(doc_id):
    """書類取得APIを使って書類をダウンロードする
        docID (str): 書類管理番号
        type (str): 1:提出本文書及び監査報告書、2:PDF、3:代替書面・添付文書、
                    4:英文ファイル、5:CSV

    Returns:
        bytes: ダウンロードしたファイルのバイナリデータ
    """
    doc_parameter = {'type': 5, 'Subscription-Key': API_KEY }
    response = requests.get(f"{BASE_URL}/{doc_id}", params=doc_parameter)
    if response.status_code != 200:
        print(f"docID: {doc_id} のファイルのダウンロードに失敗しました。")
        return None
    return response.content


def extract_zip(zip_data):
    """ZIPファイルを指定されたディレクトリに解凍する
    Copy codeArgs:
        zip_data (bytes): ZIPファイルのバイナリデータ
    """
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
        zip_ref.extractall(DOC_PATH)


def process_csv_files():
    pattern = "csv/XBRL_TO_CSV/jpcrp*.csv"
    dataframes = []
    for file_path in glob.glob(pattern):
        df = pd.read_csv(file_path, encoding="utf-16", sep=None, engine="python")
        dataframes.append(df)
    return dataframes


def clean_up_directory():
    # jpcrp*.csvファイルを削除
    for file_path in glob.glob("csv/XBRL_TO_CSV/jpaud*.csv"):
        os.remove(file_path)


def fetch_annual_securities_reports(start_date, end_date):
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

        if "results" in result:
            df = pd.DataFrame(result["results"])
            for _, row in df.iterrows():
                description = row.get("docDescription")     # 書類の説明
                docId = row.get("docID")    # 書類管理番号
                secCode = row.get("secCode")    # 提出者証券コード
                filerName = row.get("filerName")    # 提出者名
                if description is None or docId is None or secCode is None:
                    continue
                if "訂正有価証券報告書" in description or "受益証券" in description:
                    continue
                if "有価証券報告書" in description:
                    report_info = {
                        "docID": docId,
                        "secCode": secCode,
                        "docDescription": description,
                        "filerName": filerName,
                    }
                    annual_securities_reports.append(report_info)

        print("wait for 2 seconds")
        time.sleep(2)
        current_date += timedelta(days=1)

    return annual_securities_reports


def main(secCode):
    start_date = datetime.strptime("2023-06-22", "%Y-%m-%d")
    end_date = datetime.strptime("2023-06-22", "%Y-%m-%d")

    annual_securities_reports = fetch_annual_securities_reports(start_date, end_date)

    if not annual_securities_reports:
        print(start_date.strftime("%Y-%m-%d"), "から", end_date.strftime("%Y-%m-%d"), "の間に有価証券報告書はありません。")
        return
    # secCodeに一致する有価証券報告書のみを抽出
    annual_securities_reports = [report for report in annual_securities_reports if report["secCode"] == secCode]
    if not annual_securities_reports:
        print(f"{secCode} に一致する有価証券報告書はありません。")
        return
    print(f"{len(annual_securities_reports)} 件の有価証券報告書があります。")

    report_df = pd.DataFrame(annual_securities_reports)
    print(report_df[["docID", "docDescription", "filerName"]])

    if input("ダウンロードしますか?(y/n)") == "n":
        exit(0)
    doc_id = annual_securities_reports[0]["docID"]
    zip_file = fetch_annual_report(doc_id)
    if zip_file is not None:
        try:
            extract_zip(zip_file)
            df = process_csv_files()[0]
            # dfから要素ID、コンテキストID,ユニットID列を削除
            # 相対年度の列が、'当期'　以外の行は削除
            df = df.drop(
                columns=["要素ID", "コンテキストID", "ユニットID", "単位", "期間・時点"]
            )
            # 相対年度の列が、
            df = df[df["相対年度"] == "当期"]
            # df = df.drop(columns=["相対年度"])
            df = df[df["連結・個別"] != "個別"]
            df = df.drop(columns=["連結・個別"])
            df.to_csv(f"csv/{doc_id}.csv", index=False)
            clean_up_directory()
            print(f"docID: {doc_id} のファイルが正常にダウンロードされました。")
            print("wait 2 seconds")
            time.sleep(2)
        except zipfile.BadZipFile:
            print(f"docID: {doc_id} のファイルはZIPファイルではありません。")
    else:
        print(f"docID: {doc_id} のファイルのダウンロードに失敗しました。")


if __name__ == "__main__":
    if API_KEY is None:
        print("APIキーが設定されていません。")
        exit(1)
    # while True:
    #     secCode = input("4桁の証券コードを入力してください(終了する場合はqを入力): ")
    #     if len(secCode) == 4 and secCode.isdigit():
    #         break
    #     if secCode == "q":
    #         exit(0)
    #     else:
    #         print("入力が不正です。4桁の数字を入力してください。")
    main('6490'+'0')
