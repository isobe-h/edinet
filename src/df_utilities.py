def get_float_value_by_name(df, item_name, term=None) -> float:
    value = get_first_value_by_name(df, item_name, term)
    if not value:
        return 0
        # valueが数値でない場合(マイナスはok)、そのまま返す
    if not value.replace(".", "").replace("-", "").isnumeric():
        return 0
    return convert_str_to_float(value)


def get_item_name(df, item_name, term=None) -> str:
    """
    指定された項目名を含む項目の名前を取得します。
    完全合致する項目が複数ある場合は、最初の項目を返します。
    ないばあいは、部分一致する項目の最初の項目を返します。
    """
    if term:
        values = df.loc[
            (df["項目名"] == item_name) & (df["相対年度"].str.contains(term)),
            "項目名",
        ].values
        if len(values) > 0:
            return values[0]
    else:
        values = df.loc[df["項目名"] == item_name, "項目名"].values[0]
        if len(values) > 0:
            return values[0]
    return ""


def convert_str_to_float(value: str) -> float:
    if value == "－":
        return 0
    # △が頭についている場合、マイナスに変換
    if "△" in str(value):
        return -float(str(value).replace("△", ""))
    return float(value)


def get_first_value_by_name(df, item_name, term=None) -> str:
    if item_name not in df["項目名"].values:
        return ""

    query_base = df["項目名"] == item_name
    if term:
        query_term = df["相対年度"].str.contains(term)
        # 連結、個別、その他の順で値を検索
        for category in ["連結", "個別"]:
            match = df.loc[
                query_base & query_term & (df["連結・個別"].str.contains(category)),
                "値",
            ]
            if not match.empty:
                return match.iloc[0]
        # 連結も個別も見つからなかった場合、その他の値を検索
        other_match = df.loc[
            query_base
            & query_term
            & (~df["連結・個別"].str.contains("連結|個別", regex=True)),
            "値",
        ]
        if not other_match.empty:
            return other_match.iloc[0]
        return ""  # どのカテゴリーにも該当する値がない場合
    else:
        # termが指定されていない場合は、最初に見つかった値を返す
        return df.loc[query_base, "値"].iloc[0]
