import streamlit as st
import datetime
import plotly.express as px
from functions.functions import (
    get_weekly_profitability,
    get_customer_sales
)

try:
    st.set_page_config(layout='wide', initial_sidebar_state='expanded')
except Exception as e:
    st.error(f"Error setting page configuration: {e}")


def load_page():
    try:
        st.title(':blue[Sales Analytics]')

        # Get today's date
        today = datetime.date.today()

        # Calculate the last month's date range
        # Last day of the previous month
        last_month_end = today.replace(day=1) - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        # Default to the last month's date range
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=[last_month_start, last_month_end],
            key="date_range"
        )

        query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

        # Sidebar for selecting analytics
        st.sidebar.header('Analytics Options')
        analysis_type = st.sidebar.radio(
            "Select Analysis Type",
            ('Profitability Analysis', 'Customer Analysis',)
        )

        if analysis_type == 'Profitability Analysis':
            st.markdown(
                f"#### Below you will find insightful sale metrics :blue[*{date_range_text}*]"
            )
            df_weekly_profitability = get_weekly_profitability(
                query_date_filter)
            fig1 = px.bar(
                df_weekly_profitability,
                x='DAY_OF_WEEK',
                y='TOTAL_REVENUE',
                title='This chart shows which days of the week are the most profitable'
            )
            st.plotly_chart(fig1, use_container_width=True)

        elif analysis_type == 'Customer Analysis':
            query_date_filter = f"WHERE CREATIONDATE BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
            st.markdown(
                f"#### Below you will find customer sale metrics :blue[*{date_range_text}*]"
            )
            df_customer_sales = get_customer_sales(query_date_filter)
            df_customer_sales = df_customer_sales.dropna(
                subset=['LATITUDE', 'LONGITUDE']
            )
            st.markdown(
                '#### The map below shows the :blue[location of customers] based on their home address.'
            )
            st.map(df_customer_sales[['LATITUDE', 'LONGITUDE']].astype(float))

    except KeyError as e:
        st.error(f"Key error: {e}")
    except ValueError as e:
        st.error(f"Value error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# Load the page content
load_page()
