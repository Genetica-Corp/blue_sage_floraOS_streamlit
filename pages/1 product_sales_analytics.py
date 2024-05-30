import datetime
import toml
import json
import os
from dotenv import load_dotenv
import openai
import random
import time
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from functions.functions import (
    get_budtender_transaction_data,
    display_popular_products_by_sales,
    display_popular_products_by_transactions,
    get_Lebanon_data,
    display_inventory_aging
    )

# Load the .env file
load_dotenv()

# Access the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")


DATE_SELECTIONS_FILE = "date_selections.json"

def generate_summary(text):
    try:
        response = openai.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""This is the top 10 products sold by this store. 
                Please summarize the following analysis results and create an action plan based on the summary.
                Additionally, make comparisons between the two date ranges and suggest actions based on the data.
                
                Analysis Results:
                {text}
                
                Format the response as follows:
                
                **Summary:**
                - Key point 1
                - Key point 2
                - Key point 3

                **Comparison:**
                - Comparison point 1
                - Comparison point 2
                - Comparison point 3

                **Action Plan:**
                1. Action item 1
                2. Action item 2
                3. Action item 3
                
                End the summary with '### End of Summary'.
                """}
        ],
        max_tokens=3000,
        temperature=0.3,
        stop=["### End of Summary"])
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Summary generation failed."




def load_date_selections():
    if os.path.exists(DATE_SELECTIONS_FILE):
        with open(DATE_SELECTIONS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_date_selections(date_selections):
    with open(DATE_SELECTIONS_FILE, 'w') as file:
        json.dump(date_selections, file)

# Load previous date selections
if 'date_selections' not in st.session_state:
    st.session_state['date_selections'] = load_date_selections()

# Set page configuration with error handling
try:
    st.set_page_config(page_title="Product Sales Analytics", layout='wide', initial_sidebar_state='expanded')
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


def load_page():
    try:
        st.title(':blue[Product Analytics]')

        # Get today's date
        today = datetime.date.today()

        # Calculate the last month's date range
        last_month_end = today.replace(day=1) - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        # Default to the last month's date range
        date_range = st.sidebar.date_input("Select Date Range", value=[
                                           last_month_start, today], key="date_range", max_value=today)

        query_date_filter = f"WHERE T.TRANSACTIONDATE BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        query_date_filter_budtender = f"WHERE TRANSACTIONDATE BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        #print(query_date_filter)
        date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

        if st.sidebar.button("Save Date Range"):
            st.session_state['date_selections'].append({
                'start_date': str(date_range[0]),
                'end_date': str(date_range[1])
            })
            save_date_selections(st.session_state['date_selections'])

        # Sidebar for selecting analytics
        st.sidebar.header('Analytics Options')
        analysis_type = st.sidebar.radio(
            "Select Analysis Type",
            ('Sales by Product', 'Average Sale Amount', 'Compare Dates')
        )

        if analysis_type == 'Average Sale Amount':
            st.markdown(
                f"#### Below you will find product sale metrics :blue[*{date_range_text}*]")
            df_budtender = get_budtender_transaction_data(query_date_filter_budtender)

            if df_budtender is not None and not df_budtender.empty:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Average Sale Amount per Budtender")
                    df_sorted_sales = df_budtender.sort_values(
                        by="AVERAGE_SALE_AMOUNT", ascending=False)
                    df_sorted_sales["AVERAGE_SALE_AMOUNT"] = df_sorted_sales["AVERAGE_SALE_AMOUNT"].apply(
                        lambda x: f"${x:.2f}")

                    plt.figure(figsize=(10, 5))
                    sns.barplot(data=df_sorted_sales,
                                x="AVERAGE_SALE_AMOUNT", y="BUDTENDER", color="c")
                    plt.xlabel("Average Sale Amount ($)")
                    plt.ylabel("Budtender")
                    plt.title("Average Sale Amount per Budtender")
                    st.pyplot(plt)

                with col2:
                    st.markdown("### Total Transactions per Budtender")
                    df_sorted_transactions = df_budtender.sort_values(
                        by="TOTAL_TRANSACTIONS", ascending=False)
                    plt.figure(figsize=(10, 5))
                    sns.barplot(data=df_sorted_transactions,
                                x="TOTAL_TRANSACTIONS", y="BUDTENDER", color="m")
                    plt.xlabel("Total Transactions")
                    plt.ylabel("Budtender")
                    plt.title("Total Transactions per Budtender")
                    st.pyplot(plt)

                # Plotly Visualization: Average Sale Amount
                fig1 = px.bar(
                    df_sorted_sales,
                    x="AVERAGE_SALE_AMOUNT",
                    y="BUDTENDER",
                    title="Average Sale Amount per Budtender",
                    labels={
                        "AVERAGE_SALE_AMOUNT": "Average Sale Amount ($)", "BUDTENDER": "Budtender"},
                    orientation="h",
                    color="AVERAGE_SALE_AMOUNT",
                    color_continuous_scale="Viridis",
                )

                # Plotly Visualization: Total Transactions
                fig2 = px.bar(
                    df_sorted_transactions,
                    x="TOTAL_TRANSACTIONS",
                    y="BUDTENDER",
                    title="Total Transactions per Budtender",
                    labels={"TOTAL_TRANSACTIONS": "Total Transactions",
                            "BUDTENDER": "Budtender"},
                    orientation="h",
                    color="TOTAL_TRANSACTIONS",
                    color_continuous_scale="Magma",
                )

                st.markdown(
                    "### :blue[Different Scheme] for Average Sale Amount and Total Transactions per Budtender")
                col1, col2 = st.columns(2)
                col1.plotly_chart(fig1)
                col2.plotly_chart(fig2)
            else:
                st.warning("No data available for the selected date range.")

        if analysis_type == 'Sales by Product':
            query = f"""
                    SELECT
                    p.productname,
                    p.location,
                    SUM(i.totalprice) AS total_sales,
                    COUNT(DISTINCT i.transactionid) AS total_transactions
                    FROM
                    FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS_FLT AS i
                    JOIN FLORAOS.BLUE_SAGE.dutchie_inventory AS p ON i.productid = p.productid
                    JOIN FLORAOS.BLUE_SAGE.dutchie_transactions AS t ON i.transactionid = t.transactionid
                    {query_date_filter}
                    AND p.location = 'carthage'
                    GROUP BY
                    p.productname,
                    p.location
                    ORDER BY
                    total_sales DESC
                    LIMIT 10;
                    """
            df = run_query(query)
            if df is not None and not df.empty:
                st.markdown(
                    f"#### Below you will find the 10 best-selling products :blue[{date_range_text}]")
                st.markdown(
                    "##### *You can change the time frame by changing the date range in the sidebar*")
                st.markdown("\n\n")

                bar_chart = go.Figure(
                    data=[
                        go.Bar(
                            x=df["PRODUCTNAME"],
                            y=df["TOTAL_SALES"],
                            text=df["TOTAL_SALES"].apply(
                                lambda x: f"${x:.2f}"),
                            textposition="auto",
                            marker_color="royalblue",
                        )
                    ]
                )

                bar_chart.update_layout(
                    title="Top Selling Products for Carthage",
                    xaxis_title="Product Name",
                    yaxis_title="Total Sales ($)",
                    xaxis_tickangle=45,
                    yaxis_tickformat="$",
                    margin=dict(l=60, r=60, b=100, t=60),
                )

                popular_sales_markdown = display_popular_products_by_sales(df)
                popular_transactions_markdown = display_popular_products_by_transactions(
                    df)

                st.markdown(
                    "### :orange[Carthage] -  *Sales* and *Transactions* by Product")
                with st.expander("Please expand to see the Carthage Sales and Product data"):
                    col = st.columns((1, 1, 1), gap='small')
                    with col[0]:
                        st.markdown(popular_sales_markdown)
                    with col[1]:
                        st.markdown(popular_transactions_markdown)
                    with col[2]:
                        st.dataframe(df)

                st.markdown(
                    "### :orange[Lebanon] -  *Sales* and *Transactions* by Product")
                with st.expander("Please expand to see the Lebanon Sales and Product data"):
                    col = st.columns((1, 1, 1), gap='small')

                    df_lebanon = get_Lebanon_data(query_date_filter)
                    if df_lebanon is not None and not df_lebanon.empty:
                        with col[0]:
                            st.markdown(
                                display_popular_products_by_sales(df_lebanon))
                        with col[1]:
                            st.markdown(
                                display_popular_products_by_transactions(df_lebanon))
                        with col[2]:
                            st.dataframe(df_lebanon)
                    else:
                        st.warning(
                            "No data available for Lebanon for the selected date range.")

            else:
                st.warning("No data available for the selected date range.")

        if analysis_type == 'Compare Dates':
                st.markdown("#### Compare Date Ranges")
                saved_dates = st.session_state['date_selections']

                if not saved_dates:
                    st.warning("No date ranges have been saved yet.")
                else:
                    selected_dates = st.multiselect(
                        "Select Date Ranges to Compare",
                        options=[f"{d['start_date']} to {d['end_date']}" for d in saved_dates],
                        default=[f"{d['start_date']} to {d['end_date']}" for d in saved_dates[:2]]  # Default to the first two date ranges
                    )

                    if len(selected_dates) != 2:
                        st.warning("Please select exactly two date ranges to compare.")
                    else:
                        date1, date2 = selected_dates
                        date1_start, date1_end = date1.split(" to ")
                        date2_start, date2_end = date2.split(" to ")

                        query1 = f"""
                            SELECT
                            p.productname,
                            SUM(i.totalprice) AS total_sales,
                            COUNT(DISTINCT i.transactionid) AS total_transactions
                            FROM
                            FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS_FLT AS i
                            JOIN FLORAOS.BLUE_SAGE.dutchie_inventory AS p ON i.productid = p.productid
                            JOIN FLORAOS.BLUE_SAGE.dutchie_transactions AS t ON i.transactionid = t.transactionid
                            WHERE T.transactiondate BETWEEN '{date1_start}' AND '{date1_end}'
                            GROUP BY p.productname
                            ORDER BY total_sales DESC
                            LIMIT 10;
                        """

                        query2 = f"""
                            SELECT
                            p.productname,
                            SUM(i.totalprice) AS total_sales,
                            COUNT(DISTINCT i.transactionid) AS total_transactions
                            FROM
                            FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS_FLT AS i
                            JOIN FLORAOS.BLUE_SAGE.dutchie_inventory AS p ON i.productid = p.productid
                            JOIN FLORAOS.BLUE_SAGE.dutchie_transactions AS t ON i.transactionid = t.transactionid
                            WHERE T.transactiondate BETWEEN '{date2_start}' AND '{date2_end}'
                            GROUP BY p.productname
                            ORDER BY total_sales DESC
                            LIMIT 10;
                        """

                        df1 = run_query(query1)
                        df2 = run_query(query2)

                        if df1 is not None and df2 is not None:
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown(f"### Top 10 Products from {date1}")
                                st.dataframe(df1)
                                summary1 = generate_summary(df1.to_string())
                                st.markdown("### :orange[Summary]")
                                st.write(summary1)

                            with col2:
                                st.markdown(f"### Top 10 Products from {date2}")
                                st.dataframe(df2)
                                summary2 = generate_summary(df2.to_string())
                                st.markdown("### :orange[Summary]")
                                st.write(summary2)

                            comparison_summary = generate_summary(f"Comparison between {date1} and {date2}:\n\n{df1.to_string()}\n\n{df2.to_string()}")
                            st.markdown("### :orange[Comparison Summary]")
                            st.write(comparison_summary)
    except Exception as e:
        st.error(f"An error occurred: {e}")


load_page()
