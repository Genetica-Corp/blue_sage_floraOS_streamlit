import datetime
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from functions.functions import (run_query, display_top_customers, display_top_customers_medical, display_top_customers_recreational)

# Set page configuration with error handling
try:
    st.set_page_config(page_title="Customer Analytics", layout='wide', initial_sidebar_state='expanded')
except Exception as e:
    st.error(f"Error setting page configuration: {e}")

def run_query(query):
    try:
        conn = st.connection("snowflake")
        cur = conn.cursor()
        cur.execute(query)
        df = cur.fetch_pandas_all()
        return df
    except Exception as e:
        st.error(f"Error running query: {e}")
        return None

def get_customer_data(date_range):
    query_date_filter_customer = f"WHERE dt.checkindate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
    query = f"""
            SELECT
                dc.CUSTOMERTYPE,
                CONCAT(dc.FIRSTNAME, ' ', dc.LASTNAME) AS CustomerName,
                COUNT(dt.transactionid) AS NumberOfTransactions,
                SUM(dt.total) AS TotalRevenue,
                AVG(dt.total) AS AverageRevenue
            FROM FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS AS dt
            INNER JOIN FLORAOS.BLUE_SAGE.DUTCHIE_CUSTOMERS AS dc
                ON dt.customerid = dc.customerid
            {query_date_filter_customer}
            GROUP BY
                dc.CUSTOMERTYPE,
                CustomerName
            ORDER BY
                TOTALREVENUE DESC;
            """
    return run_query(query)
    


def load_page():
    try:
        st.title(':blue[Customer Analytics]')

        # Get today's date
        today = datetime.date.today()

        # Calculate the last month's date range
        last_month_end = today.replace(day=1) - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        # Default to the last month's date range
        date_range = st.sidebar.date_input("Select Date Range", value=[
                                           last_month_start, last_month_end], key="date_range", max_value=last_month_end)

        query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

        # Sidebar for selecting analytics
        st.sidebar.header('Analytics Options')
        analysis_type = st.sidebar.radio(
            "Select Analysis Type",
            ('Customer Popularity', 'Customer Segmentation'))
        
        

        if analysis_type == 'Customer Popularity':
            df_customer_transactions_revenue = get_customer_data(date_range)
            #st.dataframe(df_customer_transactions_revenue)

            markdown_content = display_top_customers(df_customer_transactions_revenue)
            st.markdown(markdown_content)

            with st.expander("Please expand to see segmentation by customer type (Medical/Recreational)"):
                col = st.columns((1, 1, 1), gap='small')

                medical_customers_markdown = display_top_customers_medical(df_customer_transactions_revenue)
                recreational_customers_markdown = display_top_customers_recreational(df_customer_transactions_revenue)

                with col[0]:
                    st.markdown(medical_customers_markdown)

                with col[1]:
                    st.markdown(recreational_customers_markdown)




    except Exception as e:
        st.error(f"An error occurred: {e}")




load_page()
