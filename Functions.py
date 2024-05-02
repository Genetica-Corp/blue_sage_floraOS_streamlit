import pandas as pd
from snowflake.connector import connect
import streamlit as st

def run_query(query):
    conn = st.connection("snowflake")
    cur = conn.cursor()
    cur.execute(query)
    df = cur.fetch_pandas_all()
    return df


def display_popular_products_by_sales(df):
    # Sort the dataframe by total sales
    df_sorted_sales = df.sort_values(by="TOTAL_SALES", ascending=False).reset_index(drop=True)
    

    # Initialize markdown strings
    popular_sales_markdown = "### 🏆 Top 10 Products by :blue[Total Sales] 🏆\n"
    

    # Construct markdown content for each metric
    for i in range(10):
        sales_product = df_sorted_sales.iloc[i]

        # Sales-based report
        popular_sales_markdown += (
            f"{i + 1}. **{sales_product['PRODUCTNAME']}** - ${sales_product['TOTAL_SALES']:.2f} in sales\n"
        )

    return popular_sales_markdown


def display_popular_products_by_transactions(df):
    # Sort the dataframe by total transactions
    df_sorted_transactions = df.sort_values(by="TOTAL_TRANSACTIONS", ascending=False).reset_index(drop=True)
    
    popular_transactions_markdown = "### 🏆 Top 10 Products by :blue[Total Transactions] 🏆\n"

    for i in range(10):
        trans_product = df_sorted_transactions.iloc[i]

        # Transactions-based report
        popular_transactions_markdown += (
            f"{i + 1}. **{trans_product['PRODUCTNAME']}** - {trans_product['TOTAL_TRANSACTIONS']} transactions\n"
        )

    return popular_transactions_markdown

def get_Lebanon_data(query_date_filter):
    query = f"""
                SELECT
                p.productname,
                p.location,
                SUM(i.totalprice) AS total_sales,
                COUNT(DISTINCT i.transactionid) AS total_transactions
                FROM
                FLORAOS.BLUE_SAGE.flattened_itemsv_blue_sage_04_28_2024 AS i
                JOIN FLORAOS.BLUE_SAGE.dutchie_inventory AS p ON i.productid = p.productid
                JOIN FLORAOS.BLUE_SAGE.dutchie_transactions AS t ON i.transactionid = t.transactionid
                {query_date_filter}
                AND p.location = 'lebanon'
                GROUP BY
                p.productname,
                p.location
                ORDER BY
                total_sales DESC
                limit 10;
                """
    
    df_lebanon = run_query(query)
    return df_lebanon