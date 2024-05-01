import streamlit as st

st.set_page_config(page_title="Cannabis Analytics Dashboard", page_icon="🌿")

st.title('Cannabis Analytics Dashboard')

st.sidebar.success("Select a dashboard from the menu.")
st.sidebar.write("Navigate through different analytics perspectives:")

# Multipage setup
st.markdown("""
### Please Select a Dashboard from the Sidebar
- Sales Analytics
- Employee Analytics
- Inventory Analytics
""")
