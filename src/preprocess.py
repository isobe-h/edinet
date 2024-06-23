import os

import pandas as pd

# 現在のディレクトリの上の階層
parent_dir = os.getcwd()
print(parent_dir)
# 前処理前のcsvフォルダのパス
csv_folder = os.path.join(parent_dir, "csv")
# 前処理済みのcsvフォルダのパス
processed_csv_folder = os.path.join(parent_dir, "processed_csv")


term_regex = r"当期末?|前期末?"


def remove_unnecessary_columns(df):
    # dfから要素ID、コンテキストID,ユニットID列を削除
    # 相対年度の列が、'当期'　以外の行は削除
    df = df.drop(
        columns=["要素ID", "コンテキストID", "ユニットID", "単位", "期間・時点"]
    ).dropna(subset=["項目名"])
    # 相対年度の列が、terms_regexに一致する行のみを抽出
    df = df[df["相対年度"].str.contains(term_regex)]
    df = df[df["連結・個別"] != "個別"]
    df = df.drop(columns=["連結・個別"])
    # 項目名の列内の"、経営指標等"のを削除
    # 総資産額、経営指標等　→　総資産額
    df["項目名"] = df["項目名"].str.replace("、経営指標等", "")
    # # '項目名'が'所有株式数'から始まる行から、最初の'現金及び預金'の前の行までを削除
    # # 例：所有株式数（単元）－政府及び地方公共団体
    # start_index = df[df["項目名"].str.startswith("所有株式数", na=False)].index[0]
    # end_index = df[df["項目名"] == "現金及び預金"].index[0] - 1
    # df = df.drop(df.index[start_index:end_index])
    return df


def preprocess_csv(path: str):
    # csvファイルを読み込む
    df = pd.read_csv(path)
    # jpcrp_cor:CompanyNameCoverPage,会社名、表紙,FilingDateInstant,提出日時点,その他,時点,－,－,ｓａｎｔｅｃ　Ｈｏｌｄｉｎｇｓ株式会社
    # の行から、値の列の値を取得
    company_name = df.loc[df["項目名"] == "会社名、表紙", "値"].iloc[0]
    # 不要な列を削除
    df = remove_unnecessary_columns(df)
    # processed_csv_folderが存在しない場合は作成
    if not os.path.exists(processed_csv_folder):
        os.makedirs(processed_csv_folder)

    # 前処理済みのcsvファイルを保存
    df.to_csv(
        os.path.join(processed_csv_folder, company_name + "_" + path.split("/")[-1]),
        index=False,
        encoding="utf-8",
    )
    return df
