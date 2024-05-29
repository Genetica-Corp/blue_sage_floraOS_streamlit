import streamlit as st
import pandas as pd
import plotly.express as px
from functions.functions import (
    get_inventory_levels,
    run_query,
    detect_inventory_anomalies,
    format_anomaly_alerts,
    insert_anomaly_alerts
)
from openai_integration import OpenAIIntegration
import asyncio

# Initialize OpenAI Integration
openai_integration = OpenAIIntegration()

def load_page():
    st.set_page_config(page_title="Inventory Management", layout='wide')
    st.title(':blue[Inventory Management]')

    today = pd.Timestamp.today()
    last_month_end = today.replace(day=1) - pd.Timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    date_range = st.sidebar.date_input("Select Date Range", value=[last_month_start, last_month_end], key="date_range")

    query_date_filter = f"WHERE transactiondate BETWEEN '{date_range[0]}' AND '{date_range[1]}'" if date_range else ""
    date_range_text = f"for the time frame between {date_range[0]} and {date_range[1]}"

    st.sidebar.header('Analytics Options')
    analysis_type = st.sidebar.radio("Select Analysis Type", ('Inventory Levels', 'Stock Analysis'))

    if analysis_type == 'Inventory Levels':
        st.markdown(f"#### Below you will find inventory levels :blue[*{date_range_text}*]")
        df_inventory_levels = get_inventory_levels(query_date_filter)
        
        if not df_inventory_levels.empty:
            fig = px.pie(df_inventory_levels, values='quantity', names='product_name', title='Inventory Levels by Product')
            st.plotly_chart(fig)

            if st.button("Generate Insights and Action Plan"):
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(openai_integration.generate_insights(df_inventory_levels, max_tokens=150))
                st.markdown(f"### Insights:\n{result}")

                action_plan = loop.run_until_complete(openai_integration.generate_insights(pd.DataFrame({"insights": [result]}), max_tokens=150))
                st.markdown(f"### Action Plan:\n{action_plan}")

                insert_anomaly_alerts(
                    alert_type="Inventory Levels",
                    description=result,
                    severity_level="High",
                    action_plan=action_plan,
                    responsible_department="Inventory",
                    notification_method="Email",
                    automated_response="Yes",
                    data_source="Inventory Management",
                    additional_info="Generated from OpenAI integration"
                )
                st.success("Action Plan inserted into Snowflake.")
        else:
            st.warning("No inventory data available for the selected date range.")

    elif analysis_type == 'Stock Analysis':
        st.markdown(f"#### Below you will find stock analysis :blue[*{date_range_text}*]")
        df_stock_analysis = run_query(f"SELECT * FROM FLORAOS.BLUE_SAGE.STOCK_ANALYSIS {query_date_filter}")
        
        if not df_stock_analysis.empty:
            fig = px.bar(df_stock_analysis, x='product_name', y='stock_level', title='Stock Analysis')
            st.plotly_chart(fig)

            if st.button("Generate Insights and Action Plan"):
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(openai_integration.generate_insights(df_stock_analysis, max_tokens=150))
                st.markdown(f"### Insights:\n{result}")

                action_plan = loop.run_until_complete(openai_integration.generate_insights(pd.DataFrame({"insights": [result]}), max_tokens=150))
                st.markdown(f"### Action Plan:\n{action_plan}")

                insert_anomaly_alerts(
                    alert_type="Stock Analysis",
                    description=result,
                    severity_level="Medium",
                    action_plan=action_plan,
                    responsible_department="Inventory",
                    notification_method="Email",
                    automated_response="No",
                    data_source="Stock Analysis",
                    additional_info="Generated from OpenAI integration"
                )
                st.success("Action Plan inserted into Snowflake.")
        else:
            st.warning("No stock data available for the selected date range.")

    # Chat interface
    st.sidebar.header('Chat with OpenAI')
    with st.sidebar.form(key='chat_form'):
        user_input = st.text_area('Enter your message:')
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        loop = asyncio.get_event_loop()
        chat_response = loop.run_until_complete(openai_integration.chat_response(user_input))
        st.sidebar.markdown(f"### OpenAI Response:\n{chat_response}")

if __name__ == "__main__":
    load_page()