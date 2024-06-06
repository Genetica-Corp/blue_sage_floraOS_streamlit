import streamlit as st
import streamlit.components.v1 as components

# Your embedded app URL
embedded_app_url = "https://app.hex.tech/daf8a75c-dce1-4ed6-8c40-f4872fbb2467/app/5134e23b-fa38-4edb-a488-0c647f524a98/latest?embedded=true&embeddedStaticCellId=fc07422f-3aa5-4b13-876c-9a633b432456"

# Custom CSS to style the border
custom_css = """
<style>
.embedded-app-container {
    position: relative;
    width: 100%;
    height: 600px;
    border: 5px solid #3498db;
    border-radius: 10px;
    overflow: hidden;
}

.embedded-app-iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
}
</style>
"""

# HTML to embed the app with custom CSS
html_content = f"""
{custom_css}
<div class="embedded-app-container">
    <iframe class="embedded-app-iframe" src="{embedded_app_url}"></iframe>
</div>
"""

# Display the custom HTML in Streamlit
components.html(html_content, height=650)