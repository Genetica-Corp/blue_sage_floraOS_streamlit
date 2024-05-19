import datetime
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
                                           last_month_start, last_month_end], key="date_range", max_value=last_month_end)

        query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

        # Sidebar for selecting analytics
        st.sidebar.header('Analytics Options')
        analysis_type = st.sidebar.radio(
            "Select Analysis Type",
            ('Sales by Product', 'Average Sale Amount')
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

                df_inventory_aging = get_Inventory_Aging_data()
                if df_inventory_aging is not None and not df_inventory_aging.empty:
                    st.markdown("### :blue[Inventory Aging]")
                    st.markdown(
                        "##### *Below you will find which non-edible Cannabis products have been in inventory for 121+ days*")
                    with st.expander("Please expand to see the Inventory Aging data"):
                        df_filtered = df_inventory_aging[df_inventory_aging["CANNABISINVENTORY"]]
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

                        carthage_inventory_markdown = display_inventory_aging(
                            df_products_with_large_inventory_Carthage)
                        st.markdown(carthage_inventory_markdown)

                        lebanon_inventory_markdown = display_inventory_aging(
                            df_products_with_large_inventory_Lebanon)
                        st.markdown(lebanon_inventory_markdown)
                else:
                    st.warning("No inventory aging data available.")
            else:
                st.warning("No data available for the selected date range.")
    except Exception as e:
        st.error(f"An error occurred: {e}")


load_page()
