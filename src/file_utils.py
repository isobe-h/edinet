import glob
import io
import os
import zipfile

import pandas as pd

DOC_PATH = "csv"


def extract_zip(zip_data):
    """ZIPファイルを指定されたディレクトリに解凍する
    Copy codeArgs:
        zip_data (bytes): ZIPファイルのバイナリデータ
    """
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
        zip_ref.extractall(DOC_PATH)


def csv_to_df():
    pattern = "csv/XBRL_TO_CSV/jpcrp*.csv"
    dataframes = []
    for file_path in glob.glob(pattern):
        df = pd.read_csv(file_path, encoding="utf-16", sep=None, engine="python")
        dataframes.append(df)
    return dataframes


def clean_up_directory():
    # csv/XBRL_TO_CSVディレクトリを削除
    files = glob.glob("csv/XBRL_TO_CSV/*")
    for f in files:
        os.remove(f)
    os.rmdir("csv/XBRL_TO_CSV")
