import pandas as pd
import streamlit as st


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