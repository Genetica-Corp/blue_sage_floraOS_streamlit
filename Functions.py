import pandas as pd
from snowflake.connector import connect
import streamlit as st
import plotly.express as px

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

def get_budtender_transaction_data(query_date_filter):
    query = f"""
                SELECT
                completedbyuser AS budtender,
                AVG(total) AS average_sale_amount,
                COUNT(transactionid) AS total_transactions
            FROM
                FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS
            {query_date_filter}
            AND NOT ISVOID
            GROUP BY
                completedbyuser
            ORDER BY
                total_transactions DESC
            limit 10
            """
    df_budtender = run_query(query)
    return df_budtender


def get_weekly_profitability(query_date_filter):
    query = f"""
            SELECT 
                DAYNAME(TRANSACTIONDATE) AS DAY_OF_WEEK,
                SUM(TOTAL) AS TOTAL_REVENUE,
                AVG(TOTAL) AS AVERAGE_REVENUE
            FROM FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS
            {query_date_filter}
            GROUP BY DAY_OF_WEEK
            ORDER BY 
                CASE 
                    WHEN DAY_OF_WEEK = 'Monday' THEN 1
                    WHEN DAY_OF_WEEK = 'Tuesday' THEN 2
                    WHEN DAY_OF_WEEK = 'Wednesday' THEN 3
                    WHEN DAY_OF_WEEK = 'Thursday' THEN 4
                    WHEN DAY_OF_WEEK = 'Friday' THEN 5
                    WHEN DAY_OF_WEEK = 'Saturday' THEN 6
                    WHEN DAY_OF_WEEK = 'Sunday' THEN 7
                    ELSE 8  -- Default value in case there's unexpected day names
                END
                """
    df_weekly_profitability = run_query(query)
    return df_weekly_profitability


def get_customer_sales(query_date_filter):
    
    query = f"""
            SELECT
                LATITUDE, 
                LONGITUDE
            FROM FLORAOS.BLUE_SAGE.MATCHED_CUSTOMERS_ZIPCODES          
            WHERE LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL
            """
    df_customer_sales = run_query(query)
    return df_customer_sales


def render_profitability_visualizations(df_weekly_profitability):
    # Bar chart for total revenue
    fig1 = px.bar(
        df_weekly_profitability,
        x="DAY_OF_WEEK",
        y="TOTAL_REVENUE",
        color="DAY_OF_WEEK",
        title="Total Revenue by Day of the Week",
        labels={"DAY_OF_WEEK": "Day of the Week", "TOTAL_REVENUE": "Total Revenue ($)"},
    )
    fig1.update_layout(margin=dict(l=60, r=60, t=40, b=80), showlegend=True)
    return fig1



def get_transaction_data():
    query = """
            SELECT
                CAST(TRANSACTIONDATE AS DATE) AS Transaction_Date,
                TRANSACTIONID, TOTAL
                FROM
                FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS
            WHERE
                TRANSACTIONDATE >= CURRENT_DATE - INTERVAL '1 year'
            """
    df_transaction_data = run_query(query)
    return df_transaction_data
