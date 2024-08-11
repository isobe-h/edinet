import csv
import glob
import io
import os
import zipfile

import pandas as pd

from type import japanese_dict
from utils import convert_to_thousand_separated

BASE_PATH = "./EDINET/"
ROW_CSV_HEADER = "row_"
PREPROCESSED_CSV_HEADER = "preprocessed_"
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)


def extract_zip(zip_data, directory: str):
    """ZIPファイルを指定されたディレクトリに解凍する
    Copy codeArgs:zip_data (bytes): ZIPファイルのバイナリデータ
    """
    path = os.path.join(BASE_PATH, directory)
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
        zip_ref.extractall(path)


def csv_to_df(save_dir):
    pattern = BASE_PATH + save_dir + "/" + "XBRL_TO_CSV/jpcrp*.csv"
    print(pattern)
    file_path = glob.glob(pattern)  # 最初のファイルのみを取得
    print(file_path)
    assert len(file_path) == 1
    df = pd.read_csv(file_path[0], encoding="utf-16", sep=None, engine="python")
    return df


def clean_up_directory(save_dir):
    pattern = BASE_PATH + save_dir + "/" + "XBRL_TO_CSV/"
    files = glob.glob(pattern + "*")
    for f in files:
        os.remove(f)
    os.rmdir(pattern)


def save_doc_from_zip(zip_file: bytes, save_dir: str, title: str):
    extract_zip(zip_file, save_dir)
    # 選択したdocIDのファイルのdocDescriptionを取得
    df = csv_to_df(save_dir)
    save_path = os.path.join(BASE_PATH, save_dir, ROW_CSV_HEADER + title)
    df.to_csv(
        save_path,
        index=False,
        encoding="utf-8",
    )
    clean_up_directory(save_dir)
    return save_path


def export_df_to_csv(data, save_path):
    # utf-8-sigにすることで、Excelで開いた際に文字化けを防ぐ
    with open(save_path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)

        for key, values in data.items():
            # 日本語ラベルに変換、見つからない場合は元のキーを使用
            japanese_label = japanese_dict.get(key, key)

            if isinstance(values, dict):
                # 辞書型の場合、各サブキーに対して新たな行を作成
                for subkey, subvalues in values.items():
                    sub_japanese_label = japanese_dict.get(subkey, subkey)
                    # 値がリストであることを確認し、それぞれの要素を列として追加
                    if isinstance(subvalues, list):
                        writer.writerow(
                            [japanese_label, sub_japanese_label] + subvalues
                        )
                    else:
                        writer.writerow([japanese_label, sub_japanese_label, subvalues])
            else:
                # リストや単一の値の場合、通常通りに処理
                if isinstance(values, list) or isinstance(values, tuple):
                    writer.writerow(
                        [japanese_label]
                        + list(map(convert_to_thousand_separated, values))
                    )
                else:
                    writer.writerow(
                        [japanese_label, convert_to_thousand_separated(values)]
                    )
