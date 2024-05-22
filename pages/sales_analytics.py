import streamlit as st
import datetime
import plotly.express as px
from functions.functions import (get_weekly_profitability, 
                                 get_customer_sales,
                                 get_hourly_profitability)

# Set page configuration with error handling
try:
    st.set_page_config(page_title="Sales Analytics",
                       layout='wide', initial_sidebar_state='expanded')
except Exception as e:
    st.error(f"Error setting page configuration: {e}")


def load_page():
    try:
        st.title(':blue[Sales Analytics]')
        today = datetime.date.today()
        last_month_end = today.replace(day=1) - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(
            day=1)
        date_range = st.sidebar.date_input("Select Date Range", value=[
                                           last_month_start, last_month_end], key="date_range")

        query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
        date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"
        st.sidebar.header('Analytics Options')
        analysis_type = st.sidebar.radio(
            "Select Analysis Type",
            ('Profitability Analysis', 'Customer Analysis',))


        if analysis_type == 'Profitability Analysis':
            st.markdown(
                f"#### Below you will find insightful sale metrics :blue[*{date_range_text}*]")
            df_weekly_profitability = get_weekly_profitability(
                query_date_filter)
            fig1 = px.bar(df_weekly_profitability, x='DAY_OF_WEEK', y='TOTAL_REVENUE',
                          title='This chart shows which days of the week are the most profitable')
            st.plotly_chart(fig1, use_container_width=True)


            df_hourly_profitability = get_hourly_profitability(query_date_filter)

            fig = px.line(df_hourly_profitability, x="HOURFORMATTED", y="AVERAGEREVENUEPERHOUR", title="Average Revenue per Hour")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)




        if analysis_type == 'Customer Analysis':
            query_date_filter = f"WHERE CREATIONDATE BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
            st.markdown(
                f"#### Below you will find customer sale metrics :blue[*{date_range_text}*]")
            df_customer_sales = get_customer_sales(query_date_filter)
            if df_customer_sales is not None and not df_customer_sales.empty:
                df_customer_sales = df_customer_sales.dropna(
                    subset=['LATITUDE', 'LONGITUDE'])
                st.markdown(
                    '#### The map below shows the :blue[location of customers] based on their home address.')
                st.map(
                    df_customer_sales[['LATITUDE', 'LONGITUDE']].astype(float))
            else:
                st.warning(
                    "No customer data available for the selected date range.")
    except Exception as e:
        st.error(f"An error occurred: {e}")


load_page()
