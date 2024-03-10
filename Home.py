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

"""
# Inspirel 
## Pregled prodaje po mjesecima
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
    d = []
    for c in entitet:
        d.append(c)
    df1 = df[df['Entitet'].isin(d)]

if len(kanton) > 0:
    d = []
    for c in kanton:
        d.append(c)
    df1 = df1[df1['Regija'].isin(d)]

st.write(df1)

#Ostvarena prodaja po mjesecu
by_month = df.groupby(['Year','Month'])['Količina'].sum().reset_index()

fig = px.histogram(by_month, x='Month', y='Količina', color='Year', barmode='group', nbins=12)
fig.update_layout(dragmode=False)
fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.add_trace(go.Histogram(x=by_month['Količina'], name="count", texttemplate="%{x}", textfont_size=20))
st.plotly_chart(fig, use_container_width=True, config=dict(
    displayModeBar=False))




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