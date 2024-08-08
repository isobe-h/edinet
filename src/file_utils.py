import glob
import io
import os
import zipfile

import pandas as pd

save_path = "./EDINET/"
ROW_BASE_PATH = save_path + "row_csv/"
DOC_BASE_PATH = save_path + "row_csv/*/XBRL_TO_CSV/"
PROCESSED_BASE_PATH = save_path + "processed_csv/"
RESULT_BASE_PATH = save_path + "result_csv/"
if not os.path.exists(save_path):
    os.makedirs(ROW_BASE_PATH)
    os.makedirs(PROCESSED_BASE_PATH)
    os.makedirs(RESULT_BASE_PATH)


def extract_zip(zip_data, directory: str):
    """ZIPファイルを指定されたディレクトリに解凍する
    Copy codeArgs:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    zip_data (bytes): ZIPファイルのバイナリデータ
    """
    path = os.path.join(ROW_BASE_PATH, directory)
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
        zip_ref.extractall(path)


def csv_to_df(save_dir):
    pattern = ROW_BASE_PATH + "/" + save_dir + "/" + "XBRL_TO_CSV/jpcrp*.csv"
    print(pattern)
    file_path = glob.glob(pattern)  # 最初のファイルのみを取得
    assert len(file_path) == 1
    df = pd.read_csv(file_path, encoding="utf-16", sep=None, engine="python")
    return df


def clean_up_directory(save_dir):
    pattern = ROW_BASE_PATH + "/" + save_dir + "/" + "XBRL_TO_CSV/"
    files = glob.glob(pattern + "*")
    for f in files:
        os.remove(f)
    os.rmdir(pattern)


def save_doc_from_zip(zip_file: bytes, save_dir: str, title: str):
    extract_zip(zip_file, save_dir)
    # 選択したdocIDのファイルのdocDescriptionを取得
    df = csv_to_df(save_dir)
    df.to_csv(
        os.path.join(ROW_BASE_PATH, save_dir, title),
        index=False,
        encoding="utf-8",
    )
    clean_up_directory(save_dir)
    return save_path
