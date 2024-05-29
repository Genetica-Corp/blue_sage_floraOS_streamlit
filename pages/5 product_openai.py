import pandas as pd
import snowflake.connector
from snowflake.connector import connect, ProgrammingError, DatabaseError
import streamlit as st
import numpy as np

def get_snowflake_connection():
    return st.connection("snowflake")

def run_query(query: str):
    try:
        conn = get_snowflake_connection()
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

def get_inventory_levels(query_date_filter: str):
    query = f"""
        SELECT
            product_name,
            SUM(quantity) AS quantity
        FROM
            FLORAOS.BLUE_SAGE.DUTCHIE_INVENTORY
        {query_date_filter}
        GROUP BY
            product_name
        ORDER BY
            quantity DESC
    """
    return run_query(query)

def insert_action_item(alert_type, description, severity_level, action_plan, responsible_department, notification_method, automated_response, data_source, additional_info):
    query = f"""
        INSERT INTO FLORAOS.BLUE_SAGE.AGENTALERTS (
            ALERT_TYPE, DESCRIPTION, SEVERITY_LEVEL, ACTION_PLAN, RESPONSIBLE_DEPARTMENT,
            NOTIFICATION_METHOD, AUTOMATED_RESPONSE, DATA_SOURCE, ADDITIONAL_INFO
        ) VALUES (
            '{alert_type}', '{description}', '{severity_level}', '{action_plan}', '{responsible_department}',
            '{notification_method}', '{automated_response}', '{data_source}', '{additional_info}'
        );
    """
    run_query(query)

def detect_sales_anomalies(df: pd.DataFrame):
    anomalies = []
    threshold = df['total_sales'].mean() + 3 * df['total_sales'].std()
    for index, row in df.iterrows():
        if row['total_sales'] > threshold:
            anomalies.append({
                "product_name": row['product_name'],
                "total_sales": row['total_sales'],
                "location": row['location']
            })
    return anomalies

def detect_inventory_anomalies(df: pd.DataFrame):
    anomalies = []
    for index, row in df.iterrows():
        if row['quantity'] < 10:  # Example threshold for low stock alert
            anomalies.append({
                "product_name": row['product_name'],
                "quantity": row['quantity'],
                "location": row['location']
            })
    return anomalies

def format_anomaly_alerts(anomalies: list, alert_type: str):
    alerts = []
    for anomaly in anomalies:
        description = f"Anomaly detected in {anomaly['product_name']} at {anomaly['location']}: {anomaly['total_sales'] if 'total_sales' in anomaly else anomaly['quantity']} units"
        alert = {
            "alert_type": alert_type,
            "description": description,
            "severity_level": "High",
            "action_plan": "Investigate the cause and take necessary actions.",
            "responsible_department": "Sales" if alert_type == "Sales Anomaly" else "Inventory",
            "notification_method": "Email",
            "automated_response": "No",
            "data_source": "Sales Data" if alert_type == "Sales Anomaly" else "Inventory Data",
            "additional_info": "Generated from anomaly detection module"
        }
        alerts.append(alert)
    return alerts

def insert_anomaly_alerts(alerts: list):
    for alert in alerts:
        insert_action_item(
            alert_type=alert["alert_type"],
            description=alert["description"],
            severity_level=alert["severity_level"],
            action_plan=alert["action_plan"],
            responsible_department=alert["responsible_department"],
            notification_method=alert["notification_method"],
            automated_response=alert["automated_response"],
            data_source=alert["data_source"],
            additional_info=alert["additional_info"]
        )

def get_budtender_transaction_data(query_date_filter: str):
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
    return run_query(query)

def get_Lebanon_data(query_date_filter: str):
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
    return run_query(query)

@st.cache_data
def get_inventory_aging_data():
    query = """
        SELECT
            SPLIT_PART (LOCATION, ' - ', 2) AS LOCATION,
            PRODUCT, CATEGORY, MASTERCATEGORY, CANNABISINVENTORY, 
            "0-30", "31-60", "61-90", "91-120", "121+" 
        FROM floraos.blue_sage.report_inventory_aging_may_7_24
    """ 
    return run_query(query)

def display_popular_products_by_sales(df: pd.DataFrame) -> str:
    df_sorted_sales = df.sort_values(by="total_sales", ascending=False).reset_index(drop=True)
    popular_sales_markdown = "### :trophy: Top 10 Products by :blue[Total Sales] :trophy:\n"
    for i in range(min(10, len(df_sorted_sales))):
        sales_product = df_sorted_sales.iloc[i]
        popular_sales_markdown += f"{i + 1}. **{sales_product['productname']}** - ${sales_product['total_sales']:.2f} in sales\n"
    return popular_sales_markdown

def display_popular_products_by_transactions(df: pd.DataFrame) -> str:
    df_sorted_transactions = df.sort_values(by="total_transactions", ascending=False).reset_index(drop=True)
    popular_transactions_markdown = "### :trophy: Top 10 Products by :blue[Total Transactions] :trophy:\n"
    for i in range(min(10, len(df_sorted_transactions))):
        trans_product = df_sorted_transactions.iloc[i]
        popular_transactions_markdown += f"{i + 1}. **{trans_product['productname']}** - {trans_product['total_transactions']} transactions\n"
    return popular_transactions_markdown

def display_inventory_aging(df: pd.DataFrame) -> str:
    df_filtered = df[df["CANNABISINVENTORY"]]
    df_products_with_large_inventory_Lebanon = (
        df_filtered[
            (df_filtered['LOCATION'] == 'Lebanon (SMO5)') &  
            (df_filtered['CATEGORY'] != 'Edibles')
        ]
        .sort_values(by="121+", ascending=False)
        .head(10)
    )

    df_products_with_large_inventory_Carthage = (
        df_filtered[
            (df_filtered['LOCATION'] == 'Carthage (SMO4)') &  
            (df_filtered['CATEGORY'] == 'Flower')
        ]
        .sort_values(by="121+", ascending=False)
        .head(10)
    )

    carthage_inventory_markdown = "### Carthage Inventory\n"
    for i, product in df_products_with_large_inventory_Carthage.iterrows():
        carthage_inventory_markdown += f"{i + 1}. **{product['PRODUCT']}** - {product['121+']} units aged 121+ days\n"

    lebanon_inventory_markdown = "### Lebanon Inventory\n"
    for i, product in df_products_with_large_inventory_Lebanon.iterrows():
        lebanon_inventory_markdown += f"{i + 1}. **{product['PRODUCT']}** - {product['121+']} units aged 121+ days\n"

    return carthage_inventory_markdown + "\n" + lebanon_inventory_markdown