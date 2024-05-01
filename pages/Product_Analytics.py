import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from snowflake.connector import connect
import datetime
import plotly as px
import plotly.graph_objects as go
from Functions import *

st. set_page_config(layout='wide', initial_sidebar_state='expanded')

def run_query(query):
    #with get_snowflake_connection() as conn:
    conn = st.connection("snowflake")
    cur = conn.cursor()
    cur.execute(query)
    df = cur.fetch_pandas_all()
    #return pd.read_sql(query, conn)
    return df
    #return pd.read_sql(query, conn)


def load_page():
    st.title(':blue[Product Analytics]')
    # Get today's date
    today = datetime.date.today()

    # Calculate the last month's date range
    last_month_end = today.replace(day=1) - datetime.timedelta(days=1)  # Last day of the previous month
    last_month_start = last_month_end.replace(day=1)  # First day of the previous month

    # Default to the last month's date range
    date_range = st.sidebar.date_input("Select Date Range", value=[last_month_start, last_month_end], key="date_range")
    #date_range = st.sidebar.date_input("Select Date Range", [])
    query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
    date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

    # Sidebar for selecting analytics
    st.sidebar.header('Analytics Options')
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ('Sales by Product', 'Average Sale Amount', 'Transaction Counts',
         'Total Discounts', 'Sales by Payment Type', 'Top Selling Products', 'Revenue by Tax Type'))
    
    if analysis_type == 'Sales by Product':
        
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
                AND p.location = 'carthage'
                GROUP BY
                p.productname,
                p.location
                ORDER BY
                total_sales DESC
                limit 10;

                """
        df = run_query(query)
        st.markdown(f"#### Below you will find the 10 best-selling products :blue[{date_range_text}]")
        #st.bar_chart(df.set_index('PRODUCTNAME')['TOTAL_SALES'])  
        #df["TOTAL_SALES"] = df["TOTAL_SALES"].round(2)  # Round to 2 decimal places
        #print(df)

        bar_chart = go.Figure(
            data=[
                go.Bar(
                    x=df["PRODUCTNAME"],  # Use full product names on x-axis
                    y=df["TOTAL_SALES"],  # Total sales on y-axis
                    text=df["TOTAL_SALES"].apply(lambda x: f"${x:.2f}"),  # Display values as text on bars
                    textposition="auto",  # Position text automatically
                    marker_color="royalblue",  # Set bar color
                        )
                    ]
                )

            # Set layout for the chart
        bar_chart.update_layout(
                title="Top Selling Products for Carthage",
                xaxis_title="Product Name",
                yaxis_title="Total Sales ($)",
                xaxis_tickangle=45,  # Rotate x-axis labels by 45 degrees
                yaxis_tickformat="$",  # Display y-axis labels with dollar sign
                margin=dict(l=60, r=60, b=100, t=60),  # Adjust margins
            )

        popular_sales_markdown = display_popular_products_by_sales(df)
        popular_transactions_markdown = display_popular_products_by_transactions(df)
        col = st.columns((2, 2, .5), gap='small')
        with col[0]:            
            st.markdown(popular_sales_markdown)
        with col[1]:
            st.markdown(popular_transactions_markdown)  # Add an empty markdown placeholder for the second column

        #with st.expander("Open to view the data behind the chart"):
         #   df["TOTAL_SALES"] = df["TOTAL_SALES"].apply(lambda x: f"${x:.2f}") # Format as currency
          #  st.table(df)

load_page()