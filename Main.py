import streamlit as st

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
except Exception as e:
    st.error(f"Error setting main content: {e}")
