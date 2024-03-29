import streamlit as st
st.set_page_config(
    page_title="Inspirehl",
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
# Inspirehl
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
df['Short_title'] = df['Artikal'].str.split(' ').str[0]
df['Regija'] = df['Regija'].str.title()


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

#st.write(df1)

def total_artikal(artikal):
    art = df1.query('Short_title == "'+str(artikal)+'"')
    art = art['Količina'].sum()
    return art

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    art = 'Dorzol'
    st.metric(label=art,value=int(total_artikal(art)),delta=None)
with col2:
    art = 'Glaumax'
    st.metric(label=art,value=int(total_artikal(art)),delta=None)
with col3:
    art = 'Latanox'
    st.metric(label=art,value=int(total_artikal(art)),delta=None)
with col4:
    art = 'Bimanox'
    st.metric(label=art,value=int(total_artikal(art)),delta=None)
with col5:
    art = 'Moksacin'
    st.metric(label=art,value=int(total_artikal(art)),delta=None)

col1, col2 = st.columns([3,1])
with col1:
    """
    ### Pregled prodaje po mjesecima
    """
    #Ostvarena prodaja po mjesecu
    by_month = df1.groupby(['Year','Month'])['Količina'].sum().reset_index()
    fig = px.bar(by_month, x=['Year','Month'], y='Količina', color='Year', text_auto=True)
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    fig.update_xaxes(type='category')
    fig.update_xaxes(nticks=12) 
    #fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True, config=dict(
        displayModeBar=False))


with col2:
    """
    ### Omjer prodaje po artiklu
    """
    #Omjer prodaje po artikli
    by_product = df1.groupby(['Short_title'])['Količina'].sum().reset_index()

    fig = px.pie(by_product, values='Količina',names='Short_title')
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True, config=dict(
            displayModeBar=False))


col1, col2 = st.columns([3,1])
with col1:
    """
    ### Pregled prodaje po Entitetu/Regiji
    """
    #Ostvarena prodaja po regionu
    by_region = df1.groupby(['Entitet','Regija'])['Količina'].sum().reset_index()
    by_region = by_region.sort_values(by=['Regija'])
    fig = px.bar(by_region, x='Regija', y='Količina', color='Entitet', text_auto=True)
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    fig.update_xaxes(type='category')
    #fig.update_xaxes(nticks=12) 
    #fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True, config=dict(
        displayModeBar=False))

with col2:
    """
    ### Omjer prodaje po regionu
    """
    #Omjer prodaje po regionu
    by_entity = df1.groupby(['Entitet'])['Količina'].sum().reset_index()

    fig = px.pie(by_entity, values='Količina',names='Entitet')
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True, config=dict(
            displayModeBar=False))


"""
### Ostvarena prodaja po mjesecu i artiklu
"""
#Ostvarena prodaja po mjesecu i artiklu
by_month_product = df1.groupby(['Year','Month','Artikal'])['Količina'].sum().reset_index()
by_month_product["Period"] = by_month_product["Year"].astype(str) +"/" + by_month_product["Month"].astype(str)
#fig = px.bar(by_month_product, x='Period', y='Količina', color='Artikal', text_auto=True)
fig = px.line(by_month_product, x='Period', y='Količina', color='Artikal')
fig.update_layout(dragmode=False)
fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
#fig.update_xaxes(type='category')
#fig.update_xaxes(nticks=12) 
#fig.update_traces(textposition='inside')
st.plotly_chart(fig, use_container_width=True, config=dict(
    displayModeBar=False))

by_month_product_pivot = by_month_product.pivot(index='Artikal', columns='Period', values='Količina')
by_month_product_pivot = by_month_product_pivot.sort_values(by=['Artikal'])
st.write(by_month_product_pivot)

"""
### Ostvarena prodaja po regionu i artiklu
"""
#Ostvarena prodaja po regionu i artiklu
by_region_product = df1.groupby(['Entitet','Regija','Artikal'])['Količina'].sum().reset_index()
by_region_product = by_region_product.sort_values(by=['Regija'])
fig = px.bar(by_region_product, x='Regija', y='Količina', color='Artikal', text_auto=True)
fig.update_layout(dragmode=False)
fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.update_xaxes(type='category')
#fig.update_xaxes(nticks=12) 
#fig.update_traces(textposition='inside')
st.plotly_chart(fig, use_container_width=True, config=dict(
    displayModeBar=False))

by_region_product_pivot = by_region_product.pivot(index=['Entitet','Regija'], columns='Artikal', values='Količina')
by_region_product_pivot = by_region_product_pivot.sort_values(by=['Regija'])
st.write(by_region_product_pivot)