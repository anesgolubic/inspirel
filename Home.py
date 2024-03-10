import streamlit as st
st.set_page_config(
    page_title="OLX V3 KPIs",
    #page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import numpy as np
from io import StringIO
from dateutil.relativedelta import relativedelta
import openpyxl

"""
# Inspirel 
## Pregled prodaje po mjesecima
"""


df = pd.read_csv('Inspirel_consolidated.csv')

st.write(df)
