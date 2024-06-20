import sqlite3
import pandas as pd

database_path = "/financial_data.db"


# Define the table schema
table_schema = """
CREATE TABLE IF NOT EXISTS financial_reports (
    element_id TEXT,
    item_name TEXT,
    context_id TEXT,
    relative_fiscal_year TEXT,
    consolidated TEXT,
    period_or_point TEXT,
    unit_id TEXT,
    unit TEXT,
    value TEXT
);
"""
# def test():
#     conn = sqlite3.connect(database_path)
#     table_schema = """
#     CREATE TABLE IF NOT EXISTS financial_reports (
#         要素ID TEXT,
#         項目名 TEXT,
#         コンテキストID TEXT,
#         相対年度 TEXT,
#         連結・個別 TEXT,
#         期間・時点 TEXT,
#         ユニットID TEXT,
#         単位 TEXT,
#         値 TEXT
#     );
#         """

#     # Create the new table in the SQLite database
#     with conn:
#         conn.execute(table_schema)

#     # Verify the first few rows to ensure data is inserted correctly
#     query = "SELECT 項目名,相対年度,単位,値 FROM financial_reports LIMIT 10;"
#     result = pd.read_sql_query(query, conn)

#     # Close the connection to the database
#     conn.close()

#     print(result)
# test()


def connect_db(df):
    conn = sqlite3.connect(database_path)
    conn.execute("DROP TABLE IF EXISTS financial_reports")
    table_schema = """
    CREATE TABLE IF NOT EXISTS financial_reports (
        要素ID TEXT,
        項目名 TEXT,
        コンテキストID TEXT,
        相対年度 TEXT,
        連結・個別 TEXT,
        期間・時点 TEXT,
        ユニットID TEXT,
        単位 TEXT,
        値 TEXT
    );
        """

    # Create the new table in the SQLite database
    with conn:
        conn.execute(table_schema)

    # Write the data from the DataFrame to the SQLite table
    df.to_sql("financial_reports", conn, if_exists="append", index=False)

    # Verify the first few rows to ensure data is inserted correctly
    query = "SELECT * FROM financial_reports LIMIT 5;"
    result = pd.read_sql_query(query, conn)

    # Close the connection to the database
    conn.close()

    print(result)
