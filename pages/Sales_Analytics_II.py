import streamlit as st
import streamlit_shadcn_ui as ui
import datetime
import plotly.express as px
from functions.functions import (get_weekly_profitability, 
                                 get_customer_sales,
                                 get_hourly_profitability,
                                 run_query)

# Set page configuration with error handling
try:
    st.set_page_config(page_title="Sales Analytics",
                       layout='wide', initial_sidebar_state='expanded')
except Exception as e:
    st.error(f"Error setting page configuration: {e}")



st.cache
def fetch_flt_data():
    try:
        query = """
            SELECT 
                TOTALPRICE, 
                TRANSACTIONID,
                TRANSACTIONDATE,
                CHECKINDATE
            FROM FLORAOS.BLUE_SAGE.DUTCHIE_TRANSACTIONS_FLT
            limit 5;
            """
        return run_query(query)
    except Exception as e:
        st.error(f"Error fetching data: {e}")

def load_page():
    try:
        st.title(':blue[Sales Analytics]')
        today = datetime.date.today()
        last_month_end = today.replace(day=1) - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(
            day=1)
        date_range = st.sidebar.date_input("Select Date Range", value=[
                                           last_month_start, today], key="date_range", max_value=today)
    
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(title="Total Revenue", content="$45,231.89", description="+20.1% from last month", key="card1")
        with cols[1]:
            ui.metric_card(title="Total Transactions", content="4895", description="+9.1% from last month", key="card2")
        with cols[2]:
            ui.metric_card(title="Total New Customers", content="88", description="+13.1% from last month", key="card3")
    
        data = fetch_flt_data()
        st.write(data)
    except Exception as e:
        st.error(f"Error setting up date range: {e}")


load_page()