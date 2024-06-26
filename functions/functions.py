import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from snowflake.connector import connect, ProgrammingError, DatabaseError


def run_query(query):
    try:
        conn = st.connection("snowflake")
        cur = conn.cursor()
        cur.execute(query)
        df = cur.fetch_pandas_all()
        return df
    except (ProgrammingError, DatabaseError) as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

def display_popular_products_by_sales(df):
    try:
        # Sort the dataframe by total sales
        df_sorted_sales = df.sort_values(by="TOTAL_SALES", ascending=False).reset_index(drop=True)
        
        # Initialize markdown strings
        popular_sales_markdown = "### 🏆 Top 10 Products by :blue[Total Sales] 🏆\n"
        
        # Construct markdown content for each metric
        for i in range(min(10, len(df_sorted_sales))):  # Ensure we don't go out of index range
            sales_product = df_sorted_sales.iloc[i]

            # Sales-based report
            popular_sales_markdown += (
                f"{i + 1}. **{sales_product['PRODUCTNAME']}** - ${sales_product['TOTAL_SALES']:.2f} in sales\n"
            )

        return popular_sales_markdown
    except KeyError as e:
        st.error(f"Column not found: {e}")
        return ""

def display_popular_products_by_transactions(df):
    try:
        # Sort the dataframe by total transactions
        df_sorted_transactions = df.sort_values(by="TOTAL_TRANSACTIONS", ascending=False).reset_index(drop=True)
        
        popular_transactions_markdown = "### 🏆 Top 10 Products by :blue[Total Transactions] 🏆\n"

        # Construct markdown content for each metric
        for i in range(min(10, len(df_sorted_transactions))):  # Ensure we don't go out of index range
            trans_product = df_sorted_transactions.iloc[i]

            # Transactions-based report
            popular_transactions_markdown += (
                f"{i + 1}. **{trans_product['PRODUCTNAME']}** - {trans_product['TOTAL_TRANSACTIONS']} transactions\n"
            )

        return popular_transactions_markdown
    except KeyError as e:
        st.error(f"Column not found: {e}")
        return ""

def display_popular_products(df, by, top_n=10):
    try:
        df_sorted = df.sort_values(by=by, ascending=False).head(top_n)
        metric = "Total Sales" if by == "TOTAL_SALES" else "Total Transactions"
        popular_markdown = f"### 🏆 Top {top_n} Products by :blue[{metric}] 🏆\n"
        for i, row in df_sorted.iterrows():
            popular_markdown += (
                f"{i + 1}. **{row['PRODUCTNAME']}** - "
                f"{'$' if by == 'TOTAL_SALES' else ''}{row[by]:.2f if by == 'TOTAL_SALES' else ''}{' transactions' if by == 'TOTAL_TRANSACTIONS' else ''}\n"
            )
        return popular_markdown
    except KeyError as e:
        st.error(f"Column not found: {e}")
        return ""


def get_data(query):
    return run_query(query)


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
        LIMIT 10;
    """
    return get_data(query)


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
        LIMIT 10;
    """
    return get_data(query)


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
                ELSE 8
            END;
    """
    return get_data(query)


def get_customer_sales():
    query = """
        SELECT
            LATITUDE, 
            LONGITUDE
        FROM FLORAOS.BLUE_SAGE.MATCHED_CUSTOMERS_ZIPCODES          
        WHERE LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL;
    """
    return get_data(query)


def render_profitability_visualizations(df_weekly_profitability):
    try:
        fig = px.bar(
            df_weekly_profitability,
            x="DAY_OF_WEEK",
            y="TOTAL_REVENUE",
            color="DAY_OF_WEEK",
            title="Total Revenue by Day of the Week",
            labels={"DAY_OF_WEEK": "Day of the Week",
                    "TOTAL_REVENUE": "Total Revenue ($)"},
        )
        fig.update_layout(margin=dict(l=60, r=60, t=40, b=80), showlegend=True)
        return fig
    except ValueError as e:
        st.error(f"Error in rendering plot: {e}")
        return None


def get_transaction_data():
    query = """
        SELECT
            CAST(TRANSACTIONDATE AS DATE) AS Transaction_Date,
            TRANSACTIONID, TOTAL
        FROM FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS
        WHERE TRANSACTIONDATE >= CURRENT_DATE - INTERVAL '1 year';
    """
    return get_data(query)


def create_heatmap(dataframe):
    try:
        plt.figure(figsize=(10, 3))
        sns.heatmap(dataframe.set_index(['LOCATION', 'PRODUCT'])[
                    ['0-30', '31-60', '61-90', '91-120', '121+']], annot=True, cmap='coolwarm', fmt=".1f")
        plt.title('Inventory Age Distribution')
        plt.xlabel('Age Categories')
        plt.ylabel('Product and Location')
        return plt
    except KeyError as e:
        st.error(f"Column not found for heatmap: {e}")
        return None


def display_inventory_aging(df):
    try:
        df_filtered = df[df['121+'] > 0].reset_index(drop=True)
        inventory_markdown = "### 🌿 Products with Inventory Aged 121+ Days 🌿\n"
        for i, product in df_filtered.iterrows():
            inventory_markdown += (
                f"{i + 1}. **{product['LOCATION']} - :blue[{product['PRODUCT']}]** :orange[{product['121+']}] units aged 121+ days\n"
            )
        return inventory_markdown
    except KeyError as e:
        st.error(f"Column not found: {e}")
        return ""
