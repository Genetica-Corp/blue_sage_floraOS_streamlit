import datetime
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from functions.functions import (run_query, display_inventory_aging)

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

@st.cache_data
def get_Inventory_Aging_data():
    query = """
        SELECT
        SPLIT_PART (LOCATION, ' - ', 2) AS LOCATION,
        PRODUCT, CATEGORY, MASTERCATEGORY, CANNABISINVENTORY, 
        "0-30", "31-60", "61-90", "91-120", "121+" 
        FROM floraos.blue_sage.report_inventory_aging
        """
    return run_query(query)
   


def load_page():
    try:
        
        
        
        st.title(':blue[Alerts and Recommendations]')

        # Get today's date
        today = datetime.date.today()

        # Calculate the last month's date range
        last_month_end = today.replace(day=1) - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        # Default to the last month's date range
        date_range = st.sidebar.date_input("Select Date Range", value=[
                                           last_month_start, today], key="date_range", max_value=today)

        query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

        # Sidebar for selecting analytics
        st.sidebar.header('Analytics Options')
        analysis_type = st.sidebar.radio(
            "Select Analysis Type",
            ('Inventory Aging', 'Summary'))        
        

        if analysis_type == 'Inventory Aging':
            df_inventory_aging = get_Inventory_Aging_data()
            if df_inventory_aging is not None and not df_inventory_aging.empty:
                    st.markdown("### :blue[Inventory Aging]")
                    st.markdown(
                        "##### *Below you will find which non-edible Cannabis products have been in inventory for 121+ days*")
                    st.markdown("##### It is recommended to :orange[markdown these products] to move them faster")
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





    except Exception as e:
        st.error(f"An error occurred: {e}")




load_page()
