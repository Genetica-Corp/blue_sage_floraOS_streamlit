import streamlit as st
import streamlit_shadcn_ui as ui


try:
    st.set_page_config(
        page_title="Cannabis Analytics Dashboard", page_icon="🌿")
except Exception as e:
    st.error(f"Error setting page configuration: {e}")

try:
    st.title('Cannabis Analytics Dashboard')
    st.sidebar.success("Select a dashboard from the menu.")
    st.sidebar.write("Navigate through different analytics perspectives:")
except Exception as e:
    st.error(f"Error setting up sidebar: {e}")

try:
    st.markdown("""
    ### Please Select a Dashboard from the Sidebar
    - Product Sales Analytics
    - Sales Analytics
    - Customer Analytics
    - Alerts and Recommendations
    """)



    cols = st.columns(3)
    with cols[0]:
        ui.metric_card(title="Total Revenue", content="$45,231.89", description="+20.1% from last month", key="card1")
    with cols[1]:
        ui.metric_card(title="Total Transactions", content="4895", description="+9.1% from last month", key="card2")
    with cols[2]:
        ui.metric_card(title="Total New Customers", content="88", description="+13.1% from last month", key="card3")


except Exception as e:
    st.error(f"Error setting main content: {e}")
