import streamlit as st
st.set_page_config(
    page_title="Inspirel",
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

df['Datum'] = df['Datum'].str.replace(" ","")
df['Datum'] = pd.to_datetime(df['Datum'], format='mixed', dayfirst=True)
#Napraviti Entitet polje

def set_color(row):
    if row["Regija"] == "11 - Brčko Distrikt":
        return "BD"
    elif row["Regija"] == "12 - RS":
        return "RS"
    else:
        return "FBiH"

df = df.assign(Entitet=df.apply(set_color, axis=1))

df['Year'] = df['Datum'].dt.year 
df['Month'] = df['Datum'].dt.month 

#Dataframovi

#Ostvarena prodaja po mjesecu
by_month = df.groupby(['Year','Month'])['Količina'].sum().reset_index()


#Omjer prodaje po artikli
by_product = df.groupby(['Artikal'])['Količina'].sum().reset_index()


#Ostvarena prodaja po regionu
by_region = df.groupby(['Entitet','Regija'])['Količina'].sum().reset_index()


#Omjer prodaje po regionu
by_entity = df.groupby(['Entitet'])['Količina'].sum().reset_index()


#Ostvarena prodaja po mjesecu i artiklu
by_month_product = df.groupby(['Year','Month','Artikal'])['Količina'].sum().reset_index()


#Ostvarena prodaja po regionu i artiklu
by_region_product = df.groupby(['Entitet','Regija','Artikal'])['Količina'].sum().reset_index()