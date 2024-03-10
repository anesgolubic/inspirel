import streamlit as st
st.set_page_config(
    page_title="Inspirel",
    #page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
from datetime import date, timedelta, datetime
import plotly.express as px
import numpy as np
from io import StringIO
from dateutil.relativedelta import relativedelta
import openpyxl
import plotly.graph_objects as go

"""
# Inspirel 
"""


df = pd.read_csv('Inspirel_consolidated.csv')

df['Datum'] = df['Datum'].str.replace(" ","")
df['Datum'] = pd.to_datetime(df['Datum'], format='mixed', dayfirst=True)
yesterday_date = date.today() - timedelta(1)

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

#Filteri

col1, col2, col3 = st.columns(3)
prvi_datum = datetime(2022, 1, 1)

with col1:   
    d = st.date_input(
    "Izaberi početni datum",
    prvi_datum)

    
with col2:
    d2 = st.date_input(
        "Izaberi krajnji datum",
        yesterday_date)

#with col3:
    #poredjenje = st.selectbox("Izaberi poređenje: ",("Prethodni period (MoM)","Prethodna godina (YoY)"),index=1)


with col3:
    entitet = st.multiselect("Izaberi Entitet", options=('FBiH','RS','BD'), default=('FBiH','RS','BD'))

kantoni = df.Regija.unique()
kanton = st.multiselect("Izaberi Kanton/Regiju", options=kantoni, default=kantoni)


dana = (d2 - d)

# if poredjenje == "Prethodna godina (YoY)":
#     momd = d - relativedelta(years=1)
#     momd2 = d2 - relativedelta(years=1)
#     ppp = " YoY"
# else:
#     momd = d - timedelta(dana.days)
#     momd2 = d2 - timedelta(dana.days)
#     ppp = " MoM"

df1 = df.query('Datum >= "'+str(d)+'" & Datum <= "'+str(d2)+'"')


if len(entitet) > 0:
    ddd = []
    for c in entitet:
        ddd.append(c)
    df1 = df1[df1['Entitet'].isin(ddd)]

if len(kanton) > 0:
    ddd = []
    for c in kanton:
        ddd.append(c)
    df1 = df1[df1['Regija'].isin(ddd)]

st.write(df1)

col1, col2 = st.columns([3,1])
with col1:
    """
    ## Pregled prodaje po mjesecima
    """
    #Ostvarena prodaja po mjesecu
    by_month = df1.groupby(['Year','Month'])['Količina'].sum().reset_index()
    fig = px.bar(by_month, x='Month', y='Količina', color='Year', barmode='group', text_auto=True)
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    #fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True, config=dict(
        displayModeBar=False))

with col2:
    """
    ## Omjer prodaje po artiklu
    """
    #Omjer prodaje po artikli
    by_product = df1.groupby(['Artikal'])['Količina'].sum().reset_index()

    fig = px.pie(by_product, values='Količina',name='Artikal')
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True, config=dict(
            displayModeBar=False))






#Ostvarena prodaja po regionu
by_region = df.groupby(['Entitet','Regija'])['Količina'].sum().reset_index()


#Omjer prodaje po regionu
by_entity = df.groupby(['Entitet'])['Količina'].sum().reset_index()


#Ostvarena prodaja po mjesecu i artiklu
by_month_product = df.groupby(['Year','Month','Artikal'])['Količina'].sum().reset_index()


#Ostvarena prodaja po regionu i artiklu
by_region_product = df.groupby(['Entitet','Regija','Artikal'])['Količina'].sum().reset_index()