import streamlit as st
import pandas as pd
from Functions import *

st.set_page_config(page_title="FloraOS Analytics Admin Panel", page_icon="🌿", layout='wide')
st.title('FloraOS Analytics Admin Panel 🌿')


st.markdown("""### :blue[Store Level Data]""")
st.markdown("""#### Updated Store level data coming soon!""")
#st.metric("Average Weekly Transactions", "$1,000,000")

data = get_transaction_data()
# Assuming `data` is the DataFrame obtained from the SQL query
data["TRANSACTION_DATE"] = pd.to_datetime(data["TRANSACTION_DATE"])

# Set date as index
data.set_index("TRANSACTION_DATE", inplace=True)

# Daily aggregates
daily_data = data.resample("D").agg(
    {"TRANSACTIONID": "nunique", "TOTAL": "sum"}  # Count unique transaction IDs per day
)

# Weekly aggregates
weekly_data = data.resample("W").agg(
    {
        "TRANSACTIONID": "nunique",  # Count unique transaction IDs per week
        "TOTAL": "sum",
    }
)

# Monthly aggregates
monthly_data = data.resample("M").agg(
    {
        "TRANSACTIONID": "nunique",  # Count unique transaction IDs per month
        "TOTAL": "sum",
    }
)

# Yearly aggregates
yearly_data = data.resample("Y").agg(
    {
        "TRANSACTIONID": "nunique",  # Count unique transaction IDs per year
        "TOTAL": "sum",
    }
)

weekly_data = weekly_data["TOTAL"].mean().round(2)

#st.write(weekly_data)
