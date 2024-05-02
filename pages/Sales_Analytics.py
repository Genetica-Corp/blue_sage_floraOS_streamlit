import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from snowflake.connector import connect
import datetime
import plotly as px
import plotly.graph_objects as go
from Functions import *

st. set_page_config(layout='wide', initial_sidebar_state='expanded')

def run_query(query):
        conn = st.connection("snowflake")
        cur = conn.cursor()
        cur.execute(query)
        df = cur.fetch_pandas_all()
        return df

def load_page():
        st.title(':blue[Sales Analytics]')







load_page()