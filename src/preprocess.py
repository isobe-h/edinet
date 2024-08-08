import os

import pandas as pd

from file_utils import PREPROCESSED_CSV_DIR_NAME, ROW_CSV_DIR_NAME

term_regex = r"当期末?|前期末?"


def remove_unnecessary_columns(df) -> pd.DataFrame:
    # dfから要素ID、コンテキストID,ユニットID列を削除
    # 相対年度の列が、'当期'　以外の行は削除
    df = df.drop(
        columns=["要素ID", "コンテキストID", "ユニットID", "単位", "期間・時点"]
    ).dropna(subset=["項目名"])
    # 相対年度の列が、terms_regexに一致する行のみを抽出
    df = df[df["相対年度"].str.contains(term_regex)]
    # 項目名の列内の"、経営指標等"のを削除
    # 総資産額、経営指標等　→　総資産額
    df["項目名"] = df["項目名"].str.replace("、経営指標等", "")
    #
    # # '項目名'が'所有株式数'から始まる行から、最初の'現金及び預金'の前の行までを削除
    # # 例：所有株式数（単元）－政府及び地方公共団体
    # start_index = df[df["項目名"].str.startswith("所有株式数", na=False)].index[0]
    # end_index = df[df["項目名"] == "現金及び預金"].index[0] - 1
    # df = df.drop(df.index[start_index:end_index])
    return df


def preprocess_csv(saved_path: str):
    # saved_path: 前処理前のcsvファイルのパス
    # 	例：	/Users/alucard/edinetapi/EDINET/row_csv/62550/株式会社エヌ・ピー・シー_有価証券報告書－第31期20220901－20230831.csv
    df = pd.read_csv(saved_path)
    df = remove_unnecessary_columns(df)
    # 保存するpathはrow_csvフォルダのパスからprocessed_csvフォルダのパスに変更
    preprocessed_path = saved_path.replace(ROW_CSV_DIR_NAME, PREPROCESSED_CSV_DIR_NAME)
    # パスがなければ作成
    if not os.path.exists(os.path.dirname(preprocessed_path)):
        os.makedirs(os.path.dirname(preprocessed_path))
    # 前処理済みのcsvファイルを保存
    df.to_csv(
        preprocessed_path,
        index=False,
        encoding="utf-8",
    )
    return preprocessed_path
