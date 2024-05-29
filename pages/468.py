import datetime
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import openai
import random
import time
import os
import json
from functions.functions import (
    get_budtender_transaction_data,
    display_popular_products_by_sales,
    display_popular_products_by_transactions,
    get_Lebanon_data,
    display_inventory_aging
)

# Set page configuration with error handling
try:
    st.set_page_config(page_title="Product Sales Analytics", layout='wide', initial_sidebar_state='expanded')
except Exception as e:
    st.error(f"Error setting page configuration: {e}")

# Initialize OpenAI API key
openai.api_key = 'sk-proj-U7Mp3L3xVeuXsrTCUNMcT3BlbkFJzaWpjnRQeCWREhVSlNcK'

# File to store date selections
DATE_SELECTIONS_FILE = "date_selections.json"

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

def generate_summary(text):
    try:
        response = openai.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following top 10 analysis results:\n\n{text}, and provide an action plan on the results."}
        ],
        max_tokens=2500,
        temperature=0.3)
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Summary generation failed."

@st.cache_data
def get_Inventory_Aging_data():
    query = """
        SELECT
        SPLIT_PART (LOCATION, ' - ', 2) AS LOCATION,
        PRODUCT, CATEGORY, MASTERCATEGORY, CANNABISINVENTORY, 
        "0-30", "31-60", "61-90", "91-120", "121+" 
        FROM floraos.blue_sage.report_inventory_aging_may_7_24
        """
    return run_query(query)

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
                                           last_month_start, last_month_end], key="date_range", max_value=last_month_end)

        if st.sidebar.button("Save Date Range"):
            st.session_state['date_selections'].append({
                'start_date': str(date_range[0]),
                'end_date': str(date_range[1])
            })
            save_date_selections(st.session_state['date_selections'])

        query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

        # Sidebar for selecting analytics
        st.sidebar.header('Analytics Options')
        analysis_type = st.sidebar.radio(
            "Select Analysis Type",
            ('Sales by Product', 'Average Sale Amount', 'Inventory Aging', 'Additional Analysis', 'Chatbot', 'Compare Dates')
        )

        if analysis_type == 'Average Sale Amount':
            st.markdown(
                f"#### Below you will find product sale metrics :blue[*{date_range_text}*]")
            df_budtender = get_budtender_transaction_data(query_date_filter)

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

                # Generate summary for Average Sale Amount
                summary_text = f"Average Sale Amount per Budtender:\n{df_sorted_sales.to_string()}\n\nTotal Transactions per Budtender:\n{df_sorted_transactions.to_string()}"
                summary = generate_summary(summary_text)
                st.markdown("### :orange[Summary]")
                st.write(summary)

                # Store analysis result in session state
                st.session_state['average_sale_amount'] = df_sorted_sales
                st.session_state['total_transactions'] = df_sorted_transactions

            else:
                st.warning("No data available for the selected date range.")

        elif analysis_type == 'Sales by Product':
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

                # Generate summary for Sales by Product
                summary_text = df.to_string()
                summary = generate_summary(summary_text)
                st.markdown("### :orange[Summary]")
                st.write(summary)

                # Store analysis result in session state
                st.session_state['sales_by_product'] = df

            else:
                st.warning("No data available for the selected date range.")

        elif analysis_type == 'Inventory Aging':
            st.markdown(
                f"#### Below you will find inventory aging data :blue[*{date_range_text}*]")

            df_inventory_aging = get_inventory_aging_data()

            if df_inventory_aging is not None and not df_inventory_aging.empty:
                st.markdown("### Inventory Aging Data")

                fig = px.bar(df_inventory_aging, x="PRODUCT", y=["0-30 DAYS", "31-60 DAYS", "61-90 DAYS", "91+ DAYS"],
                             title="Inventory Aging by Product", labels={"value": "Inventory Count", "variable": "Aging Category"},
                             barmode='stack', color_discrete_sequence=px.colors.qualitative.Vivid)
                st.plotly_chart(fig)

                # Generate summary for Inventory Aging
                summary_text = df_inventory_aging.to_string()
                summary = generate_summary(summary_text)
                st.markdown("### :orange[Summary]")
                st.write(summary)

                # Store analysis result in session state
                st.session_state['inventory_aging'] = df_inventory_aging

            else:
                st.warning("No inventory aging data available.")

        elif analysis_type == 'Additional Analysis':
            st.markdown("#### Additional Analysis Section")
            st.markdown("This section is reserved for any additional analysis you might want to perform.")

            # Example additional analysis: Monthly sales trend
            query = f"""
                    SELECT
                    DATE_TRUNC('month', transactiondate) AS month,
                    SUM(totalprice) AS total_sales
                    FROM FLORAOS.BLUE_SAGE.flattened_itemsv_blue_sage_04_28_2024
                    {query_date_filter}
                    GROUP BY month
                    ORDER BY month;
                    """
            df_monthly_sales = run_query(query)

            if df_monthly_sales is not None and not df_monthly_sales.empty:
                st.markdown("### Monthly Sales Trend")

                fig = px.line(df_monthly_sales, x='month', y='total_sales', title='Monthly Sales Trend')
                st.plotly_chart(fig)

                # Generate summary for Monthly Sales Trend
                summary_text = df_monthly_sales.to_string()
                summary = generate_summary(summary_text)
                st.markdown("### :orange[Summary]")
                st.write(summary)

                # Store analysis result in session state
                st.session_state['monthly_sales_trend'] = df_monthly_sales

            else:
                st.warning("No monthly sales data available for the selected date range.")

        elif analysis_type == 'Compare Dates':
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
                        FLORAOS.BLUE_SAGE.flattened_itemsv_blue_sage_04_28_2024 AS i
                        JOIN FLORAOS.BLUE_SAGE.dutchie_inventory AS p ON i.productid = p.productid
                        JOIN FLORAOS.BLUE_SAGE.dutchie_transactions AS t ON i.transactionid = t.transactionid
                        WHERE transactiondate BETWEEN '{date1_start}' AND '{date1_end}'
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
                        FLORAOS.BLUE_SAGE.flattened_itemsv_blue_sage_04_28_2024 AS i
                        JOIN FLORAOS.BLUE_SAGE.dutchie_inventory AS p ON i.productid = p.productid
                        JOIN FLORAOS.BLUE_SAGE.dutchie_transactions AS t ON i.transactionid = t.transactionid
                        WHERE transactiondate BETWEEN '{date2_start}' AND '{date2_end}'
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

        elif analysis_type == 'Chatbot':
            st.markdown("#### Chatbot Section")
            st.title("Simple chat")

            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Streamed response emulator
            def response_generator():
                user_message = st.session_state.messages[-1]["content"] if st.session_state.messages else ""

                analysis_summary = ""
                if "average_sale_amount" in st.session_state and "average sale amount" in user_message.lower():
                    analysis_summary = generate_summary(st.session_state["average_sale_amount"].to_string())
                elif "sales_by_product" in st.session_state and "sales by product" in user_message.lower():
                    analysis_summary = generate_summary(st.session_state["sales_by_product"].to_string())
                elif "inventory_aging" in st.session_state and "inventory aging" in user_message.lower():
                    analysis_summary = generate_summary(st.session_state["inventory_aging"].to_string())
                elif "monthly_sales_trend" in st.session_state and "monthly sales trend" in user_message.lower():
                    analysis_summary = generate_summary(st.session_state["monthly_sales_trend"].to_string())
                else:
                    analysis_summary = "No specific analysis data available to summarize."

                response = f"### Here is the summary of the latest analysis:\n\n{analysis_summary}"
                for word in response.split():
                    yield word + " "
                    time.sleep(0.05)

            # Accept user input
            if prompt := st.chat_input("Ask me about the analysis data"):
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(prompt)
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})

                # Generate assistant response
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    full_response = ""
                    for word in response_generator():
                        full_response += word
                        response_placeholder.markdown(full_response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"Error loading page: {e}")

load_page()