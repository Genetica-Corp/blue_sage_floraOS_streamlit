import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Hex",
                       layout='wide', initial_sidebar_state='expanded')


# Your embedded app URL
embedded_app_url = "https://app.hex.tech/daf8a75c-dce1-4ed6-8c40-f4872fbb2467/app/5134e23b-fa38-4edb-a488-0c647f524a98/latest?embedded=true&embeddedStaticCellId=fc07422f-3aa5-4b13-876c-9a633b432456"

# Custom CSS to style the border and cover the bottom border
custom_css = """
<style>
.embedded-app-container {
    position: relative;
    width: 100%;
    height: 700px; /* Increased height to extend the bottom border */
    border: 5px solid #3498db;
    border-radius: 20px;
    overflow: hidden;
}

.embedded-app-iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%; /* Make iframe cover the full height */
    border: none;
}

.bottom-cover {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 36px; /* Height of the cover element */
    background-color: #1f1f29; /* Background color to match the page */
}
</style>
"""

# HTML to embed the app with custom CSS
html_content1 = f"""
{custom_css}
<div class="embedded-app-container">
    <iframe class="embedded-app-iframe" src="{embedded_app_url}"></iframe>
    <div class="bottom-cover"></div> <!-- Cover element to hide the bottom border -->
</div>
"""

embedded_app_url2 = "https://app.hex.tech/daf8a75c-dce1-4ed6-8c40-f4872fbb2467/app/5134e23b-fa38-4edb-a488-0c647f524a98/latest?embedded=true&embeddedStaticCellId=c5d92893-639f-4677-a868-2e8139cd566f"
html_content2 = f"""
{custom_css}
<div class="embedded-app-container">
    <iframe class="embedded-app-iframe" src="{embedded_app_url2}"></iframe>
    <div class="bottom-cover"></div> <!-- Cover element to hide the bottom border -->
</div>
"""


# Display the custom HTML in Streamlit
components.html(html_content1, height=750) # 
components.html(html_content2, height=750)

